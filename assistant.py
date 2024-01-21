from agent import Agent
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


class Assistant:

    def __init__(self,
                 llm_model_path,
                 stt_energy=500,
                 stt_pause=1,
                 stt_dynamic_energy=False,
                 stt_model="base",
                 tts_speaker="xenia",
                 tts_sample_rate=48000,
                 device="auto"):
        self.agent = Agent()
        self.stt = STT(energy=stt_energy,
                       pause=stt_pause,
                       dynamic_energy=stt_dynamic_energy,
                       model=stt_model,
                       device=device,
                       model_root="whisper")
        self.llm = LLM(llm_model_path)
        self.tts = TTS(speaker=tts_speaker,
                       sample_rate=tts_sample_rate,
                       device=device)
        self.queue_input = queue.Queue(maxsize=4)
        self.queue_output = queue.Queue(maxsize=4)

    def action(self, pattern, callback):
        self.agent.action(pattern,
                          lambda *args: callback(self.queue_output.put, *args))

    def start(self):
        thread_input = threading.Thread(target=self.__process_input,
                                        daemon=True)
        thread_input.start()

        thread_output = threading.Thread(target=self.__say_output, daemon=True)
        thread_output.start()

        # This method does not returns control, so it must be called last
        self.stt.listen_loop(self.__save_message, phrase_time_limit=60)

    def __save_message(self, message):
        self.queue_input.put(message)

    def __process_input(self):
        while True:
            message = self.queue_input.get()
            matcher = llm.ACTIVATION_REGEX.match(message)

            if matcher is not None:
                prefix = matcher.group(1)
                postfix = matcher.group(2)

                if not self.agent.execute(postfix):
                    response = self.llm.generate()
                    self.queue_output.put(response)
                    self.llm.message(prefix)
                else:
                    self.llm.message(message)
            else:
                self.llm.message(message)

    def __say_output(self):
        while True:
            response = self.queue_output.get()
            self.tts.say(response)


def start(llm_model_path,
          stt_energy=500,
          stt_pause=1,
          stt_dynamic_energy=False,
          stt_model="base",
          tts_speaker="xenia",
          tts_sample_rate=24000,
          device="auto"):
    assistant = Assistant(llm_model_path,
                          stt_energy=stt_energy,
                          stt_pause=stt_pause,
                          stt_dynamic_energy=stt_dynamic_energy,
                          stt_model=stt_model,
                          tts_speaker=tts_speaker,
                          tts_sample_rate=tts_sample_rate,
                          device=device)
    assistant.start()

    LOGGER.info("Ready.")


if __name__ == "__main__":
    fire.Fire(start)
