# watchdog_mqtt_telegram
simple python watchdog to watch mqtt que and send alerts to telegram

### usage
simplest way is to use it as docker container
first, clone repository:
```
git clone https://github.com/pawelbura/watchdog_mqtt_telegram.git
cd watchdog_mqtt_telegram
```
##### docker build
```
docker build . -t watchdog  
```
##### docker run
```
docker run --name watchdogA -d --restart on-failure:5 -e MQTT_ADDR="mqtt.eclipseprojects.io" -e TELEGRAM_TOKEN="...paste_your_token..." -e TELEGRAM_CHAT_ID="...paste_chat_id..." watchdog
```
It is possible to run multiple watchdog, below second watchdog to watch the one above:
```
docker run --name watchdogB -e WATCHDOG_NAME=watchdogB -e WATCH_QUE=watchdog/watchdogA -e HEARTBEAT_QUE=watchdog/watchdogB -d --restart on-failure:5 -e MQTT_ADDR="mqtt.eclipseprojects.io" -e TELEGRAM_TOKEN="...paste_your_token..." -e TELEGRAM_CHAT_ID="...paste_chat_id..." watchdog
```

### configuration
watchdog uses configuration in environment variables:
- **obligatory:**

address of mqtt server - you can use a public one ([read this]([http://mqtt.eclipseprojects.io/)), or run one on your own ([read this](https://github.com/eclipse/mosquitto))

token and chat_id of telegram (how to get them - [read this](https://core.telegram.org/bots))
```
MQTT_ADDR  # url or IP address, for example "mqtt.eclipseprojects.io" of "192.168.1.1"
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
```
- **optional** (defaults to values below):
```
WATCHDOG_NAME=""  # mqtt client id, should be unique on mqtt server, can be empty and will be randomized
MQTT_ADDR_PORT=1883
WATCH_QUE=watchdog/watchdogB
HEARTBEAT_QUE=watchdog/watchdogA
WATCH_INTERVAL=5*60   # message on WATCH_QUE expected every WATCH_INTERVAL seconds
LOGGING_LEVEL=20  # logging.INFO
```

### requirements
used libraries:
- [paho mqtt python client](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
- [python telegram bot](https://github.com/python-telegram-bot/python-telegram-bot)