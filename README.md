# watchdog_mqtt_telegram

simple python watchdog to watch MQTT que and send alerts to Telegram

The goal is to have simple script for monitoring of other devices (like IoT sensors sending readings over MQTT). If run on 2 different machines, can monitor if one of them is down.

This simple script connects to MQTT broker, subscribes to chosen topics (can subsribe to multiple topics) and periodically checks if new message is received. If for more than 3 checks there is no new message, sends alert to Telegram chat. Additionally sends MQTT message periodically (as a heartbeat, indicating that script is alive).

Written in Python 3 using 2 libraries (see requirements [below](#requirements)).
Container based on Python3-alpine image to have smaller image (built image of python:3.10-alpine is ~70MB, compared to ~900MB of standard python:3.10 and ~135MB of python:3.10-slim)

## details

### usage

simplest way is to use it as docker container
first, clone repository:

```bash
git clone https://github.com/pawelbura/watchdog_mqtt_telegram.git
cd watchdog_mqtt_telegram
```

#### docker

##### docker build

```bash
docker build . -t watchdog  
```

##### docker run

```bash
docker run --name watchdogA -d --restart on-failure:5 -e MQTT_ADDR="mqtt.eclipseprojects.io" -e TELEGRAM_TOKEN="...paste_your_token..." -e TELEGRAM_CHAT_ID="...paste_chat_id..." watchdog
```

It is possible to run multiple watchdog, below second watchdog to watch the one above:

```bash
docker run --name watchdogB -d --restart on-failure:5 -e WATCHDOG_NAME="watchdogB" -e WATCH_QUES="watchdog/watchdogA" -e HEARTBEAT_QUE="watchdog/watchdogB" -e MQTT_ADDR="mqtt.eclipseprojects.io" -e TELEGRAM_TOKEN="...paste_your_token..." -e TELEGRAM_CHAT_ID="...paste_chat_id..." watchdog
```

and now you have 2 watchdogs watching each other (doesn't make much sense on a single machine, but you can run it on different machines and get an alert whenever one is down)

### configuration

watchdog uses configuration in environment variables:

- **obligatory:**

address of mqtt server - you can use a public one ([read this](http://mqtt.eclipseprojects.io/)), or run one on your own ([read this](https://github.com/eclipse/mosquitto))

token and chat_id of telegram (how to get them - [read this](https://core.telegram.org/bots))

```text
MQTT_ADDR  # url or IP address, for example "mqtt.eclipseprojects.io" of "192.168.1.1"
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
```

- **optional** (defaults to values below):

```text
WATCHDOG_NAME="watchdogA"        # MQTT client id, should be unique on mqtt server (otherwise causes disconnections)
MQTT_ADDR_PORT=1883
WATCH_QUES=watchdog/watchdogB    # MQTT ques to watch for incomming messages, for multiple ques separate with semicolon (';')
HEARTBEAT_QUE=watchdog/watchdogA # MQTT que to send periodical messages indicating that script is alive
WATCH_INTERVAL=5*60              # message on WATCH_QUES expected every WATCH_INTERVAL seconds
LOGGING_LEVEL=20                 # logging.INFO, change to 10 (logging.DEBUG) for debugging
```

### requirements

Python 3

libraries used:

- [paho mqtt python client](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
- [python telegram bot](https://github.com/python-telegram-bot/python-telegram-bot)
