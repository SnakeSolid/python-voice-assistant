from agent import Agent
from datetime import datetime
from datetime import timedelta
from llm import LLM
from stt import STT
from tts import TTS
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

    speaker("Будильник на {}:{} установлен".format(hours * 60 + minutes))


class Assistant:
    def __init__(self, model_path, stt_model = "base", speaker = "xenia", device = "auto"):
        self.agent = Agent()
        self.stt = STT(model = stt_model, device = device, model_root = "whisper")
        self.llm = LLM(model_path)
        self.tts = TTS(speaker = "xenia", device = device)
        self.queue_input = queue.Queue(maxsize = 4)
        self.queue_output = queue.Queue(maxsize = 4)


    def action(self, pattern, callback):
        self.agent.action(pattern, lambda *args: callback(self.queue_output.put, *args))


    def start(self):
        thread_input = threading.Thread(target = self.__process_input, daemon = True)
        thread_input.start()

        thread_output = threading.Thread(target = self.__say_output, daemon = True)
        thread_output.start()

        # This method does not returns control, so it must be called last
        self.stt.listen_loop(self.__save_message, phrase_time_limit = 60)


    def __save_message(self, message):
        self.queue_input.put(message)


    def __process_input(self):
        while True:
            message = self.queue_input.get()
            matcher = llm.ACTIVATION_REGEX.match(message)

            self.llm.message(message)

            if matcher is not None:
                prefix = matcher.group(1)
                postfix = matcher.group(2)

                if not self.agent.execute(postfix):
                    response = self.llm.generate()
                    self.queue_output.put(response)


    def __say_output(self):
        while True:
            response = self.queue_output.get()
            self.tts.say(response)


def start(model_path, stt_model = "medium", speaker = "xenia", device = "auto"):
    assistant = Assistant(model_path, stt_model = stt_model, speaker = speaker, device = device)
    assistant.action("(поставь|заведи|добавь|создай) таймер на # секунд", lambda speaker, s: start_timer(speaker, 0, 0, s))
    assistant.action("(поставь|заведи|добавь|создай) таймер на # минут", lambda speaker, m: start_timer(speaker, 0, m, 0))
    assistant.action("(поставь|заведи|добавь|создай) будильник на # #", lambda speaker, h, m: start_alarm(speaker, h, m))
    assistant.action("(поставь|заведи|добавь|создай) будильник на # часов # минут", lambda speaker, h, m: start_alarm(speaker, h, m))
    assistant.action("(поставь|заведи|добавь|создай) будильник на # часов", lambda speaker, h: start_alarm(speaker, h, 0))
    assistant.start()

    LOGGER.info("Ready.")


if __name__ == "__main__":
    fire.Fire(start)
