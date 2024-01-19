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


LOGGER = logging.getLogger(__name__)


class Assistant:
    def __init__(self, model_path, stt_model = "base", speaker = "xenia", device = "auto"):
        self.stt = STT(dynamic_energy = True, model = stt_model, device = device, model_root = "whisper")
        self.llm = LLM(model_path)
        self.tts = TTS(speaker = "xenia", device = device)
        self.queue_input = queue.Queue(maxsize = 4)
        self.queue_output = queue.Queue(maxsize = 4)


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

            if matcher is None:
                continue

            self.llm.message(message)
            response = self.llm.generate()
            self.queue_output.put(response)


    def __say_output(self):
        while True:
            response = self.queue_output.get()
            self.tts.say(response)


def start(model_path, stt_model = "base", speaker = "xenia", device = "auto"):
    assistant = Assistant(model_path, stt_model = stt_model, speaker = speaker, device = device)
    assistant.start()

    LOGGER.info("Ready.")


if __name__ == "__main__":
    fire.Fire(start)
