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

    thread_input = threading.Thread(
        target = lambda: sleep_and_send(speaker, wait_sconds, "Таймер на {} минут сработал".format(hours * 60 + minutes)),
        daemon = True
    )
    thread_input.start()

    speaker("Таймер на {} минут установлен".format(hours * 60 + minutes))


def start_alarm(speaker, hours, minutes):
    now = datetime.now()
    alarm = now.replace(minute = minutes)

    if hours != -1:
        alarm = alarm.replace(hour = hours)

    if now >= alarm:
        alarm = alarm + timedelta(days = 1)

    wait_sconds = (alarm - now).total_seconds()
    thread_input = threading.Thread(
        target = lambda: sleep_and_send(speaker, wait_sconds, "Будильник на {}:{} сработал".format(alarm.hour, alarm.minute)),
        daemon = True
    )
    thread_input.start()

    speaker("Будильник на {}:{} установлен".format(hours, minutes))


def start(model_path, stt_model = "medium", speaker = "xenia", device = "auto"):
    assistant = Assistant(model_path, stt_model = stt_model, speaker = speaker, device = device)
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
