from pythainlp.transliterate import transliterate
import warnings

class Phonemizer:
    def __init__(self):
        """
        The base thai phonemizer
        """

        warnings.warn("The thai phonemizer has been loaded, unfortunately we are unable "
                      "to determine the accuracy of this transcript, use at your own risk")

    @staticmethod
    def phonemize(text):
        print(text)
        result = transliterate(text, engine="thaig2p")
        result = (result.replace(" . ", "-.-")
                  .replace("  ", "-||-")
                  .replace(" ", "")
                  .replace("-||-", " ")
                  .replace("-.-", ". "))
        return result
