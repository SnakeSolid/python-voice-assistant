from words import sentence_to_stem, Words
import collections
import log
import logging


LOGGER = logging.getLogger(__name__)


Action = collections.namedtuple("Action", [ "words", "callback" ])


class Agent:
    def __init__(self):
        self.actions = []


    def action(self, pattern, callback):
        LOGGER.info("New action for `%s`.", pattern)

        words = Words(pattern)

        LOGGER.info("Words for pattern `%s`.", words)

        self.actions.append(Action(words, callback))


    def execute(self, sentence):
        LOGGER.info("Sentence `%s`", sentence)
        stems = sentence_to_stem(sentence)
        LOGGER.info("Word stems %s", stems)

        for action in self.actions:
            arguments = action.words.match(stems)

            if arguments is not None:
                LOGGER.info("Action found.")

                action.callback(*arguments)

                return True

        return False


if __name__ == "__main__":
    def timer(minutes, seconds):
        print("Таймер на {}:{:02}".format(minutes, seconds))

    def alarm(hours, minutes):
        print("Будильник на {}:{:02}:00".format(hours, minutes))

    def search(query):
        print("Найти `{}`".format(query))

    agent = Agent()
    agent.action("(поставь|заведи|добавь|создай) таймер на # секунд", lambda s: timer(0, s))
    agent.action("(поставь|заведи|добавь|создай) таймер на # минут", lambda m: timer(m, 0))
    agent.action("(поставь|заведи|добавь|создай) будильник на # #", lambda h, m: alarm(h, m))
    agent.action("(поставь|заведи|добавь|создай) будильник на # часов", lambda h: alarm(h, 0))
    agent.action("(поставь|заведи|добавь|создай) будильник на # минут", lambda m: alarm(-1, m))
    agent.action("(поставь|заведи|добавь|создай) будильник на # часов # минут", lambda h, m: alarm(h, m))
    agent.action("(открой|запусти) будильник на # часов # минут", lambda h, m: alarm(h, m))
    agent.action("(найди|поищи) ...", lambda q: search(q))

    LOGGER.info("Ready.")

    while True:
        request = input("User: ")

        if agent.execute(request):
            LOGGER.info("Success.")
        else:
            LOGGER.info("No action found.")
