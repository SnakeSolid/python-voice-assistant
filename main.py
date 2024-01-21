from assistant import Assistant
from datetime import datetime
from datetime import timedelta
import fire
import llm
import log
import logging
import queue
import re
import threading
import time


LOGGER = logging.getLogger(__name__)


def sleep_and_send(speaker, duration, message):
    time.sleep(duration)
    speaker(message)


def start_timer(speaker, hours, minutes, seconds):
    wait_sconds = hours * 3600 * minutes * 60 + seconds

    if hours == 0 and minutes == 0:
        name = "{} секунд".format(seconds)
    elif hours == 0 and seconds == 0:
        name = "{} минут".format(minutes)
    elif hours == 0:
        name = "{} минут {} секунд".format(minutes, seconds)
    elif minutes == 0 and minutes == 0:
        name = "{} часов".format(hours)
    else:
        name = "{} часов {} минут".format(hours, minutes)

    thread_input = threading.Thread(
        target = lambda: sleep_and_send(speaker, wait_sconds, "Таймер {} сработал".format(name)),
        daemon = True
    )
    thread_input.start()

    speaker("Таймер {} установлен".format(name))


def start_alarm(speaker, hours, minutes):
    now = datetime.now()
    alarm = now.replace(minute = minutes)
    alarm = alarm.replace(hour = hours)

    if minutes == 0:
        name = "{} часов".format(hours)
    else:
        name = "{} часов {} минут".format(hours, minutes)

    if now >= alarm:
        alarm = alarm + timedelta(days = 1)

    wait_sconds = (alarm - now).total_seconds()
    thread_input = threading.Thread(
        target = lambda: sleep_and_send(speaker, wait_sconds, "Будильник на {} сработал".format(name)),
        daemon = True
    )
    thread_input.start()

    speaker("Будильник на {} установлен".format(name))


def start(model_path, stt_model = "medium", speaker = "xenia", device = "auto"):
    assistant = Assistant(model_path, stt_model = stt_model, speaker = speaker, device = device)
    assistant.action("напомни через # секунд", lambda speaker, s: start_timer(speaker, 0, 0, s))
    assistant.action("напомни через # минут # секунд", lambda speaker, m, s: start_timer(speaker, 0, m, s))
    assistant.action("напомни через # минут", lambda speaker, m: start_timer(speaker, 0, m, 0))
    assistant.action("напомни через # часов # минут", lambda speaker, h, m: start_timer(speaker, h, m, 0))
    assistant.action("напомни через # часов", lambda speaker, h: start_timer(speaker, h, 0, 0))
    assistant.action("(поставь|заведи|добавь|создай) таймер на # секунд", lambda speaker, s: start_timer(speaker, 0, 0, s))
    assistant.action("(поставь|заведи|добавь|создай) таймер на # минут # секунд", lambda speaker, m, s: start_timer(speaker, 0, m, s))
    assistant.action("(поставь|заведи|добавь|создай) таймер на # минут", lambda speaker, m: start_timer(speaker, 0, m, 0))
    assistant.action("(поставь|заведи|добавь|создай) таймер на # часов # минут", lambda speaker, h, m: start_timer(speaker, h, m, 0))
    assistant.action("(поставь|заведи|добавь|создай) таймер на # часов", lambda speaker, h: start_timer(speaker, h, 0, 0))
    assistant.action("(поставь|заведи|добавь|создай) будильник на # #", lambda speaker, h, m: start_alarm(speaker, h, m))
    assistant.action("(поставь|заведи|добавь|создай) будильник на # часов # минут", lambda speaker, h, m: start_alarm(speaker, h, m))
    assistant.action("(поставь|заведи|добавь|создай) будильник на # часов", lambda speaker, h: start_alarm(speaker, h, 0))
    assistant.start()

    LOGGER.info("Ready.")


if __name__ == "__main__":
    fire.Fire(start)
