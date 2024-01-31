import fire
import log
import logging
import ntt
import os
import re
import subprocess
import torch


LOGGER = logging.getLogger(__name__)
MODEL_URI = "https://models.silero.ai/models/tts/ru/v4_ru.pt"
MODEL_FILE = "silero/model.pt"
AUDIO_PATH = "temp/output.wav"
REGEX_WORD = re.compile(r"(\w+|\.|,|:|;|!|\?)")
REGEX_NUMBER = re.compile(r"(\d+)")


def get_model(device = "cpu", n_threads = 4):
    device = torch.device(device)
    torch.set_num_threads(n_threads)

    if not os.path.isfile(MODEL_FILE):
        LOGGER.info("Downloading model...")
        torch.hub.download_url_to_file(MODEL_URI, MODEL_FILE)  

    LOGGER.info("Importing model...")
    model = torch.package.PackageImporter(MODEL_FILE).load_pickle("tts_models", "model")
    model.to(device)

    LOGGER.info("Model created.")

    return model


class TTS:
    def __init__(self, sample_rate = 48000, speaker = "xenia", device = "auto", n_threads = 4):
        self.ntt = ntt.NTT()
        self.model = get_model(device, n_threads)
        self.sample_rate = sample_rate
        self.speaker = speaker


    def say(self, message):
        LOGGER.debug("Speech message `%s`.", message)
        text = self.__transcribe(message)

        LOGGER.info("Speech generation for `%s`.", text)
        self.model.save_wav(text = text, speaker = self.speaker, sample_rate = self.sample_rate, audio_path = AUDIO_PATH)
        LOGGER.info("Generation complete.")

        LOGGER.info("Start playing.")
        subprocess.call(["ffplay", "-nodisp", "-autoexit", "-hide_banner", AUDIO_PATH], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        LOGGER.info("Playing complete.")


    def __transcribe(self, text):
        return REGEX_WORD.sub(lambda word: self.__transcribe_word(word.group(0)), text)


    def __transcribe_word(self, word):
        if REGEX_NUMBER.fullmatch(word) is not None:
            return self.ntt.convert(int(word))
        return word \
            .replace("0", "ноль") \
            .replace("1", "один") \
            .replace("2", "два") \
            .replace("3", "три") \
            .replace("4", "четыре") \
            .replace("5", "пять") \
            .replace("6", "шесть") \
            .replace("7", "семь") \
            .replace("8", "восемь") \
            .replace("9", "девять") \
            .replace("ee", "и") \
            .replace("oo", "у") \
            .replace("b", "б") \
            .replace("c", "ц") \
            .replace("d", "д") \
            .replace("e", "е") \
            .replace("f", "ф") \
            .replace("g", "г") \
            .replace("h", "х") \
            .replace("i", "и") \
            .replace("j", "дж") \
            .replace("k", "к") \
            .replace("l", "л") \
            .replace("m", "м") \
            .replace("n", "н") \
            .replace("o", "о") \
            .replace("p", "п") \
            .replace("q", "ку") \
            .replace("r", "р") \
            .replace("s", "с") \
            .replace("t", "т") \
            .replace("u", "у") \
            .replace("v", "в") \
            .replace("w", "в") \
            .replace("x", "кс") \
            .replace("y", "у") \
            .replace("z", "з") \
            .replace("…", "") \
            .replace("“", "") \
            .replace("”", "") \
            .replace("$", " доллар ") \
            .replace("%", " процент ")


def start(device = "cpu", n_threads = 4):
    tts = TTS(device = device, n_threads = n_threads)

    LOGGER.info("Ready.")

    while True:
        message = input("Message: ")
        tts.say(message)


if __name__ == "__main__":
    fire.Fire(start)
