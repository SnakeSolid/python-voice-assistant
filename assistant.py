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
                 llm_model_path: str | None = None,
                 llm_story_mode: bool = False,
                 stt_energy: int = 500,
                 stt_pause: int = 1,
                 stt_dynamic_energy: bool = False,
                 stt_model: str = "base",
                 tts_speaker: str = "xenia",
                 tts_sample_rate: int = 24000,
                 dialog_mode: bool = False,
                 device: str = "auto"):
        self.agent = Agent()
        self.stt = STT(energy=stt_energy,
                       pause=stt_pause,
                       dynamic_energy=stt_dynamic_energy,
                       model=stt_model,
                       device=device,
                       model_root="whisper")
        self.llm = (LLM(llm_model_path, story_mode=llm_story_mode)
                    if llm_model_path is not None else None)
        self.tts = TTS(speaker=tts_speaker,
                       sample_rate=tts_sample_rate,
                       device=device)
        self.dialog_mode = dialog_mode
        self.queue_input: queue.Queue = queue.Queue(maxsize=4)
        self.queue_output: queue.Queue = queue.Queue(maxsize=4)

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
            send_request = self.dialog_mode

            if matcher is not None:
                prefix = matcher.group(1)
                postfix = matcher.group(2)
                send_request |= not self.agent.execute(postfix)

            if send_request and self.llm is not None:
                self.llm.message(message)
                response = self.llm.generate()
                self.queue_output.put(response)

    def __say_output(self):
        while True:
            response = self.queue_output.get()
            self.tts.say(response)


def start(llm_model_path: str | None = None,
          llm_story_mode: bool = False,
          stt_energy: int = 500,
          stt_pause: int = 1,
          stt_dynamic_energy: bool = False,
          stt_model: str = "base",
          tts_speaker: str = "xenia",
          tts_sample_rate: int = 24000,
          dialog_mode: bool = False,
          device: str = "auto"):
    assistant = Assistant(llm_model_path,
                          llm_story_mode=llm_story_mode,
                          stt_energy=stt_energy,
                          stt_pause=stt_pause,
                          stt_dynamic_energy=stt_dynamic_energy,
                          stt_model=stt_model,
                          tts_speaker=tts_speaker,
                          tts_sample_rate=tts_sample_rate,
                          dialog_mode=dialog_mode,
                          device=device)
    assistant.start()

    LOGGER.info("Ready.")


if __name__ == "__main__":
    fire.Fire(start)
