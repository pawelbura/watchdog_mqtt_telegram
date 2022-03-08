FROM python:3.10-alpine

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY watchdog_mqtt_telegram.py /
WORKDIR /

CMD ["python", "watchdog_mqtt_telegram.py"]