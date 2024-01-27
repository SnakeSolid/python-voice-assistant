from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import NLTKWordTokenizer
import collections
import fire
import nltk
import re

STEMMERS = [SnowballStemmer(language) for language in ["english", "russian"]]
TOKENIZER = NLTKWordTokenizer()
REGEX_NUMBER = re.compile(r"""^\d+$""")
PUNCTUATION = [".", ",", ":", ";", "!", "?", "-"]
TOKEN_GROUP_START = "("
TOKEN_GROUP_END = ")"
TOKEN_NUMBER = "#"
TOKEN_WORD = "*"
TOKEN_TAIL = "..."

Token = collections.namedtuple("Token", ["word", "start", "end"])
Stem = collections.namedtuple("Stem", ["word", "stem", "start", "end"])


def word_to_stem(word: str) -> str:
    result = word

    for stemmer in STEMMERS:
        result = stemmer.stem(result)

        if result != word:
            break

    return result


def text_to_tokens(text: str) -> list[Token]:
    tokens = TOKENIZER.span_tokenize(text)
    result = []

    for start, end in tokens:
        result.append(Token(text[start:end], start, end))

    return result


class Matcher:

    def match(self, text: str, tokens: list[Stem],
              index: int) -> tuple[int, object]:
        return -1, None


class Word(Matcher):

    def __init__(self, word: str):
        self.word = word

    def match(self, text: str, tokens: list[Stem],
              index: int) -> tuple[int, object]:
        index = index

        if index < len(tokens) and tokens[index].stem == self.word:
            return index + 1, None

        return -1, None

    def __repr__(self):
        return self.word


class Or(Matcher):

    def __init__(self, words: list[str]):
        self.words = words

    def match(self, text: str, tokens: list[Stem],
              index: int) -> tuple[int, object]:
        index = index

        if index < len(tokens) and tokens[index].stem in self.words:
            return index + 1, None

        return -1, None

    def __repr__(self):
        return "( {} )".format(" | ".join([word for word in self.words]))


class Any(Matcher):

    def __init__(self):
        pass

    def match(self, text: str, tokens: list[Stem],
              index: int) -> tuple[int, object]:
        index = index

        if index < len(tokens):
            return index + 1, tokens[index].word

        return -1, None

    def __repr__(self):
        return "*"


class Tail(Matcher):

    def __init__(self):
        pass

    def match(self, text: str, tokens: list[Stem],
              index: int) -> tuple[int, object]:
        length = len(tokens)

        if index < length:
            return length, text[tokens[index].start:]
        else:
            return length, ""

    def __repr__(self):
        return "..."


class Integer(Matcher):

    def __init__(self):
        pass

    def match(self, text: str, tokens: list[Stem],
              index: int) -> tuple[int, object]:
        index = index

        if index < len(tokens) and REGEX_NUMBER.match(
                tokens[index].word) is not None:
            return index + 1, int(tokens[index].word)

        return -1, None

    def __repr__(self):
        return "#"


class Words:

    def __init__(self, text: str):
        self.words = self.__parse(text)

    def match(self, text: str,
              tokens: list[Token]) -> tuple[bool, list[object]]:
        stems: list[Stem] = self.__tokens_to_stems(tokens)
        arguments = []
        index = 0

        for word in self.words:
            index, value = word.match(text, stems, index)

            if index == -1:
                return False, []

            if value is not None:
                arguments.append(value)

            index = self.__skip_punctuation(index, stems)

        return True, arguments

    def __tokens_to_stems(self, tokens: list[Token]) -> list[Stem]:
        return [
            Stem(token.word, word_to_stem(token.word), token.start, token.end)
            for token in tokens
        ]

    def __repr__(self):
        return " ".join([repr(word) for word in self.words])

    def __skip_punctuation(self, index: int, stems: list[Stem]):
        while index < len(stems) and stems[index] in PUNCTUATION:
            index += 1

        return index

    def __parse(self, text: str) -> list[Matcher]:
        result: list[Matcher] = []
        tokens = text_to_tokens(text)
        index = 0

        while index < len(tokens):
            word = tokens[index].word

            if word == TOKEN_NUMBER:
                result.append(Integer())
            elif word == TOKEN_WORD:
                result.append(Any())
            elif word == TOKEN_GROUP_START:
                index += 1
                group = []

                while index < len(tokens):
                    alternatives = tokens[index].word

                    if alternatives == TOKEN_GROUP_END:
                        break

                    for alternative in alternatives.split("|"):
                        if alternative:
                            group.append(word_to_stem(alternative))

                    index += 1

                result.append(Or(group))
            elif word == TOKEN_TAIL:
                result.append(Tail())

                break
            else:
                result.append(Word(word_to_stem(word)))

            index += 1

        return result


def start(expression: str):
    words = Words(str(expression))
    print("Expression:", words)

    while True:
        sentence = input("Sentence: ")
        tokens = text_to_tokens(sentence)
        success, arguments = words.match(sentence, tokens)

        print("success: {}, result: {}".format(success, arguments))


if __name__ == "__main__":
    fire.Fire(start)
