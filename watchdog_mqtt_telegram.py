#%%
import paho.mqtt.client as mqtt
import telegram
import logging
import time
import os
#%%
# zmienne globalne
last_mqtt_received: float = time.time()   # ustawienie last received na now, żeby nie wysylal alertu w pierwszym uruchomieniu
logger = logging.getLogger(__name__)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info(f"mqtt connected {rc}")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(userdata)

def on_disconnect(client, userdata,  rc):
    logger.info(f"mqtt disconneted {rc}")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global last_mqtt_received
    last_mqtt_received = time.time()
    logger.debug(f"received: {msg.payload}")

def alert_telegram(telegram_bot, TELEGRAM_CHAT_ID, msg):
    telegram_bot.send_message(text=msg, chat_id=TELEGRAM_CHAT_ID)
    logger.warning(f"ALERT! {msg}")

# %%
def main():
    global last_mqtt_received  # w sumie niepotrzebne global, bo tu tylko odczytuję wartość, ale na wszelki wypadek dodaję

    # stałe (w sumie zmienne bo w main pobierane ze zmiennych środowiskowych)
    LOGLEVEL: int # = logging.INFO

    WATCHDOG_NAME: str
    MQTT_ADDR: str
    MQTT_ADDR_PORT: int
    WATCH_QUE: str
    HEARTBEAT_QUE: str
    WATCH_INTERVAL: int # = 5*60   # co ile sekund powinna przyjść wiadomosć
    ALERT_AFTER: int # = 3 * WATCH_INTERVAL + 1        # alert wysyłany po 3x czasie interwału + 1 sekunda, żeby się nie minąć

    TELEGRAM_TOKEN: str
    TELEGRAM_CHAT_ID: int 

    # pobierz konfigurację ze zmiennych środowiskowych
    #   można do przenieść do pętli, dzięki czemu możnaby zmieniać zachowanie podczas działania
    LOGLEVEL = int(os.environ.get("LOGGING_LEVEL", logging.INFO))
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOGLEVEL)
    logger.debug(f"loglevel: {logger.getEffectiveLevel()}")

    # zmienne obligatoryjne
    # możnaby get, ale akurat chcę żeby rzuciło błędem więc nie: TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    try:
        TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
        TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
    except KeyError:
        logger.critical("Telegram configuration environment variables not found!")

    try:
        MQTT_ADDR = os.environ["MQTT_ADDR"]
    except KeyError:
        logger.critical("MQTT configuration environment variables not found!")

    # zmienne opcjonalne
    WATCHDOG_NAME = os.environ.get("WATCHDOG_NAME", "watchdogA")

    MQTT_ADDR_PORT = int(os.environ.get("MQTT_ADDR_PORT", 1883))
    WATCH_QUE = os.environ.get("WATCH_QUE", "watchdog/watchdogB")
    HEARTBEAT_QUE = os.environ.get("HEARTBEAT_QUE", "watchdog/watchdogA")
    WATCH_INTERVAL = int(os.environ.get("WATCH_INTERVAL", 5*60))  # co ile sekund powinna przyjść wiadomosć
    ALERT_AFTER = 3 * WATCH_INTERVAL + 1        # alert wysyłany po 3x czasie interwału + 1 sekunda, żeby się nie minąć

    # pokazanie konfiguracji
    logger.debug(f"{WATCHDOG_NAME}|{MQTT_ADDR}:{MQTT_ADDR_PORT}")
    logger.info(f"watch:{WATCH_QUE}|heartbeat:{HEARTBEAT_QUE}|interval:{WATCH_INTERVAL}|alert_after:{ALERT_AFTER}")
    
    # uruchomienie mqtt i telegra
    telegram_bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.debug(telegram_bot.get_me())

    client = mqtt.Client(WATCHDOG_NAME, userdata=WATCH_QUE)  # WATCH_QUE przesyłane do klienta w userdata, żeby później użyć w on_connecdt
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    # client.connect("mqtt.eclipseprojects.io", 1883, 60)
    client.connect(MQTT_ADDR, MQTT_ADDR_PORT, 60)
    # loop_start i loop_stop uruchamia/zatrzymuję pętlę odczytywania/wysylania wiadomości
    #   w oddzielnym wątku, pozwalając coś zrobić w tym
    client.loop_start()

    # zawsze
    while True:
        # jeżei wiadomość mqtt odebrana dawniej niż to
            # wyslij alert na telegram
        logger.debug(f"last_mqtt_received: {last_mqtt_received}, {time.time()-last_mqtt_received}, {ALERT_AFTER}")
        if (time.time()-last_mqtt_received)>ALERT_AFTER:
            alert_telegram(telegram_bot, TELEGRAM_CHAT_ID, 
                f"Alert, wiadomość z {WATCH_QUE} odebrana {(time.time()-last_mqtt_received):.0f}s ({((time.time()-last_mqtt_received)/60):.0f}min) temu. Wysłał {WATCHDOG_NAME}.")

        # wyślij heartbeat na mqtt publish_hertbeat_mqtt(b"1")
        #   tym samym połączeniem client
        #   wysylam najprostrzą 1, żeby była jakaś wiadomość miminalna
        client.publish(HEARTBEAT_QUE, b"1")
        logger.debug(f"published: {HEARTBEAT_QUE}, {b'1'}")

        # czekaj x min
        logger.debug(f"before sleep {WATCH_INTERVAL}")
        time.sleep(WATCH_INTERVAL)
        logger.debug(f"after sleep {WATCH_INTERVAL}")
    # %% 
    # TODO: dodać obsługę błędów ogólną, żeby to miało szanse się wykonać
    client.loop_stop()
    #%%


if __name__ == "__main__":
    main()
