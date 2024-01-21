import log
import logging
import numpy as np
import queue
import speech_recognition as sr
import threading
import time
import torch 
import whisper


LOGGER = logging.getLogger(__name__)


class STT:
    def __init__(self,
            model = "base",
            device = ("cuda" if torch.cuda.is_available() else "cpu"),
            energy = 500,
            pause = 1,
            dynamic_energy = False,
            model_root="~/.cache/whisper",
            mic_index = None
        ):
        self.energy = energy
        self.pause = pause
        self.dynamic_energy = dynamic_energy
        self.audio_model = whisper.load_model(model, download_root = model_root).to(device)
        self.audio_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.microphone_active = False
        self.banned_results = [ "", " ", "\n", None ]
        self.__setup_mic(mic_index)


    def __setup_mic(self, mic_index):
        LOGGER.info("Setup microphone %s", mic_index)

        self.source = sr.Microphone(sample_rate = 16000, device_index = mic_index)
        self.recorder = sr.Recognizer()
        self.recorder.pause_threshold = self.pause
        self.recorder.energy_threshold = self.energy
        self.recorder.dynamic_energy_threshold = self.dynamic_energy

        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)


    def __preprocess(self, data):
        return torch.from_numpy(np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0)


    def __get_all_audio(self, min_time = -1.):
        LOGGER.info("Get audio minimal time = %f0.3", min_time)
        
        audio = bytes()
        got_audio = False
        time_start = time.time()

        while not got_audio or time.time() - time_start < min_time:
            while not self.audio_queue.empty():
                audio += self.audio_queue.get()
                got_audio = True

        data = sr.AudioData(audio, 16000, 2)
        data = data.get_raw_data()

        return data


    def __record_load(self, _, audio):
        data = audio.get_raw_data()

        if self.microphone_active:
            self.audio_queue.put_nowait(data)


    def __transcribe_forever(self):
        while True:
            audio_data = self.__get_all_audio()
            audio_data = self.__preprocess(audio_data)
            result = self.audio_model.transcribe(audio_data, fp16 = False, language = "ru")
            predicted_text = result["text"]

            if predicted_text not in self.banned_results:
                self.result_queue.put_nowait(predicted_text)


    def listen_loop(self, callback, phrase_time_limit = None):
        LOGGER.info("Listening...")

        self.enable_microphone()
        self.recorder.listen_in_background(self.source, self.__record_load, phrase_time_limit = phrase_time_limit)

        thread = threading.Thread(target = self.__transcribe_forever, daemon = True)
        thread.start()

        while True:
            message = self.result_queue.get()

            LOGGER.info("Recognized text `%s`", message)

            callback(message)


    def enable_microphone(self):
        self.microphone_active = True


    def disable_microphone(self):
        self.microphone_active = False


if __name__ == "__main__":
    stt = STT(dynamic_energy = True, model = "base", device = "cpu", model_root = "whisper")
    stt.listen_loop(print, phrase_time_limit = 60)

    LOGGER.info("Ready.")
