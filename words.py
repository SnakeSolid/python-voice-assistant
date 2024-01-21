from nltk.stem.snowball import SnowballStemmer
import nltk
import re


STEMMERS = [ SnowballStemmer(language) for language in [ "english", "russian" ] ]
REGEX_NUMBER = re.compile(r"""^\d+$""")
PUNCTUATION = [ ".", ",", ":", ";", "!", "?", "-" ]
TOKEN_GROUP_START = "("
TOKEN_GROUP_END = ")"
TOKEN_NUMBER = "#"
TOKEN_WORD = "*"
TOKEN_TAIL = "..."


def token_to_stem(token):
    result = token

    for stemmer in STEMMERS:
        result = stemmer.stem(result)

        if result != token:
            break

    return result


def text_to_stem(text):
    tokens = nltk.word_tokenize(text)
    result = []

    for token in tokens:
        stem = token

        for stemmer in STEMMERS:
            stem = stemmer.stem(stem)

        result.append(stem)

    return result


class Word:
    def __init__(self, word):
        self.word = word

    def match(self, tokens, index):
        index = index

        if index < len(tokens) and tokens[index] == self.word:
            return index + 1, None

        return -1, None

    def __repr__(self):
        return self.word


class Or:
    def __init__(self, *words):
        self.words = list(words)

    def match(self, tokens, index):
        index = index

        if index < len(tokens) and tokens[index] in self.words:
            return index + 1, None

        return -1, None

    def __repr__(self):
        return "( {} )".format(" | ".join(self.words))


class Any:
    def __init__(self):
        pass

    def match(self, tokens, index):
        index = index

        if index < len(tokens):
            return index + 1, tokens[index]

        return -1, None

    def __repr__(self):
        return "*"


class Tail:
    def __init__(self):
        pass

    def match(self, tokens, index):
        return len(tokens), " ".join(tokens[index:])

    def __repr__(self):
        return "..."


class Integer:
    def __init__(self):
        pass

    def match(self, tokens, index):
        index = index

        if index < len(tokens) and REGEX_NUMBER.match(tokens[index]) is not None:
            return index + 1, int(tokens[index])

        return -1, None

    def __repr__(self):
        return "#"


class Words:
    def __init__(self, text):
        self.words = self.__parse(text)


    def match(self, tokens):
        arguments = []
        index = 0

        for word in self.words:
            index, value = word.match(tokens, index)

            if index == -1:
                return None

            if value is not None:
                arguments.append(value)

            index = self.__skip_punctuation(index, tokens)

        return arguments


    def __repr__(self):
        return " ".join([repr(word) for word in self.words])


    def __skip_punctuation(self, index, tokens):
        while index < len(tokens) and tokens[index] in PUNCTUATION:
            index += 1

        return index


    def __parse(self, text):
        result = []
        tokens = nltk.word_tokenize(text)
        index = 0

        while index < len(tokens):
            token = tokens[index]

            if token == TOKEN_NUMBER:
                result.append(Integer())
            elif token == TOKEN_WORD:
                result.append(Any())
            elif token == TOKEN_GROUP_START:
                index += 1
                group = []

                while index < len(tokens):
                    token = tokens[index]

                    if token == TOKEN_GROUP_END:
                        break

                    for word in token.split("|"):
                        if word:
                            group.append(token_to_stem(word))

                    index += 1

                result.append(Or(*group))
            elif token == TOKEN_TAIL:
                result.append(Tail())

                break
            else:
                result.append(Word(token_to_stem(token)))

            index += 1

        return result


if __name__ == "__main__":
    while True:
        sentence = input("Pattern: ")
        words = Words(sentence)
        print("Result:", words)
