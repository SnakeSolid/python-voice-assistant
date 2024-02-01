from llama_cpp import Llama
import fire
import log
import logging
import re

LOGGER = logging.getLogger(__name__)
ACTIVATION_REGEX = re.compile(r"^(.*)\bАлиса\b(.*)$", re.IGNORECASE)
SYSTEM_PROMPT = """Ты — Алиса, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им."""
END_OF_SENTENCE = ["\n", ".", ":", ";"]
MAX_RESPONSE_LENGTH = 256
REPEAT_LENGTH = 64


class LLM:

    def __init__(self,
                 model_path: str,
                 history_length: int = 10,
                 system_prompt: str = SYSTEM_PROMPT,
                 story_mode: bool = False):
        self.model = Llama(model_path=model_path,
                           n_ctx=2000,
                           n_parts=1,
                           n_threads=4,
                           verbose=False)
        self.system_prompt = self.__get_message_tokens(role="system",
                                                       content=system_prompt)
        self.bot_prompt = self.__get_message_tokens(role="bot")
        self.story_mode = story_mode
        self.model.eval(self.system_prompt)
        self.history_length = history_length
        self.history: list[list[int]] = []

    def message(self, message: str):
        while len(self.history) >= self.history_length:
            self.history = self.history[1:]

        prompt = self.__get_message_tokens(role="user", content=message)

        self.history.append(prompt)

    def generate(self):
        prompt = self.__get_prompt()
        generator = self.model.generate(prompt,
                                        top_k=30,
                                        top_p=0.9,
                                        temp=0.2,
                                        repeat_penalty=1.1)
        result = ""

        for token in generator:
            token_str = self.model.detokenize([token]).decode("utf-8",
                                                              errors="ignore")
            result += token_str

            LOGGER.info("Got token `%s`.", token_str)

            if token == self.model.token_eos() or (
                    not self.story_mode and token_str in END_OF_SENTENCE) or (
                        not self.story_mode and token_str == " "
                        and len(result) > MAX_RESPONSE_LENGTH):
                break

            repeat = self.__detect_repeat(result)

            if repeat != -1:
                LOGGER.info("Got repeating sequence.")
                result = result[:repeat]

                break

        prompt = self.__get_message_tokens(role="bot", content=result)
        self.history.append(prompt)

        return result

    def __detect_repeat(self, text: str):
        if REPEAT_LENGTH < len(text):
            tail = text[-REPEAT_LENGTH:]

            if text.find(tail, 0, -REPEAT_LENGTH) != -1:
                return -REPEAT_LENGTH

        return -1

    def __get_prompt(self):
        tokens = self.system_prompt.copy()

        for message in self.history:
            tokens += message

        tokens += self.bot_prompt

        return tokens

    def __get_message_tokens(self, role: str, content: object = None):
        if content is not None:
            content = "<s>{}\n{}</s>".format(role, content)
        else:
            content = "<s>{}\n".format(role)

        content = content.encode("utf-8")
        message_tokens = self.model.tokenize(content, special=True)

        return message_tokens


def start(model_path: str,
          history_length: int = 10,
          system_prompt: str = SYSTEM_PROMPT,
          story_mode: bool = False):
    llm = LLM(model_path,
              history_length=history_length,
              system_prompt=system_prompt,
              story_mode=story_mode)

    LOGGER.info("Story mode = %s.", story_mode)
    LOGGER.info("Ready.")

    while True:
        message = input("User: ")
        llm.message(message)
        response = llm.generate()
        print("Assistant:", response)


if __name__ == "__main__":
    fire.Fire(start)
