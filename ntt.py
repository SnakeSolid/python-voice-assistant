import decimal
import log
import logging


LOGGER = logging.getLogger(__name__)
UNITS = [
    "ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять",
    "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"
]
TENS = [ "~00", "~10", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто" ]
HUNDREDS = [ "~000", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот" ]
ORDERS = [ (None, None, None), ("тысяча", "тысячи", "тысяч"), ("миллион", "миллиона", "миллионов"), ("миллиард", "миллиарда", "миллиардов") ]
MINUS = "минус"


class NTT:
    def __init__(self):
        pass


    def convert(self, value):
        LOGGER.info("Comvert %d to words.", value)

        if value == 0:
            return UNITS[0]

        name_parts = []

        if value > 0:
            number = value
        else:
            name_parts.append(MINUS)
            number = -value

        factor = 1_000_000_000

        for index in reversed(range(0, 4)):
            units = (number // factor) % 1_000
            name_parts += NTT.__thousand_to_text(units, allow_zero = False)
        
            if units > 0 and index > 0:
                name_parts.append(NTT.__get_order(index, units))

            factor //= 1_000

        return " ".join(name_parts)


    def __get_order(factor, value):
        remainder = value % 100

        if remainder == 0:
            return ""
        elif remainder == 1:
            return ORDERS[factor][0]
        elif value == 2:
            return ORDERS[factor][1]
        else:
            return ORDERS[factor][2]


    def __hundred_to_text(value, allow_zero = True):
        name_parts = []

        if value == 0:
            if allow_zero:
                name_parts.append(UNITS[0])
        elif value < 20:
            name_parts.append(UNITS[value])
        elif value < 100:
            units = value % 10
            name_parts.append(TENS[value // 10])

            if units != 0:
                name_parts.append(UNITS[units]) 

        return name_parts


    def __thousand_to_text(value, allow_zero = True):
        name_parts = []

        if value < 100:
            name_parts += NTT.__hundred_to_text(value, allow_zero = allow_zero)
        else:
            hundred = value % 100
            name_parts.append(HUNDREDS[value // 100])
            name_parts += NTT.__hundred_to_text(hundred, allow_zero = False)

        return name_parts


if __name__ == "__main__":
    import sys

    nts = NTT()

    LOGGER.info("Ready.")

    for argument in sys.argv[1:]:
        value = int(argument)

        print("{} => `{}`".format(value, nts.convert(value)))
