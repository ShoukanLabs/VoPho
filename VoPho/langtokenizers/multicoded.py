import warnings
import re
from fast_langdetect import detect
import random
from termcolor import colored

# Unicode ranges for various writing systems
WRITING_SYSTEMS_UNICODE_RANGES = {
    'zh': [(0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0x20000, 0x2A6DF), (0x2A700, 0x2B73F), (0x2B740, 0x2B81F)],  # Chinese
    'ja': [(0x3040, 0x309F), (0x30A0, 0x30FF)],  # Japanese (Hiragana and Katakana)
    'ko': [(0xAC00, 0xD7AF)],  # Korean (Hangul)
    'ar': [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)],  # Arabic
    'cy': [(0x0400, 0x04FF)],  # Cyrillic
    'deva': [(0x0900, 0x097F)],  # Devanagari (used for Hindi, Sanskrit, etc.)
    'he': [(0x0590, 0x05FF)],  # Hebrew
    'th': [(0x0E00, 0x0E7F)],  # Thai
    # Add other writing systems here as needed
}

# Mapping of predefined language codes to specific colors
LANGUAGE_COLORS = {
    'en': 'green',  # Chinese
    'zh': 'yellow',  # Chinese
    'ja': 'cyan',  # Japanese
    'ko': 'blue',  # Korean
    'ar': 'green',  # Arabic
    'cy': 'magenta',  # Cyrillic
    'hi': 'red',  # Devanagari
    'mr': 'red',  # Devanagari
    'he': 'white',  # Hebrew
    'th': 'blue',  # Thai
    '??': 'red'  # Undefined or unknown languages
}

# Keep track of colors assigned to never-before-seen languages
unknown_language_colors = {}


def random_color():
    """
    Returns a random color from the set of basic colors.

    :return: A string representing a random color.
    """
    colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    return random.choice(colors)

def print_colored_text(text):
    """
    Print the tokenized text with each language in a different color.
    New, unseen languages get assigned a random color,
    while unknown languages ('??') get a dark red color.

    :param text: The tokenized text to print.
    """
    # ... (implementation remains unchanged)

class Tokenizer:
    """
    A class for tokenizing text based on different writing systems and languages.
    """

    def __init__(self):
        """
        Initialize the Tokenizer.
        """

    @staticmethod
    def is_writing_system(char, system):
        """
        Check if a character belongs to a specific writing system.

        :param char: The character to check.
        :param system: The writing system to check against.
        :return: Boolean indicating if the character belongs to the specified writing system.
        """
        code_point = ord(char)
        return any(start <= code_point <= end for start, end in WRITING_SYSTEMS_UNICODE_RANGES.get(system, []))

    @staticmethod
    def detect_japanese_korean_chinese(text):
        """
        Detect if the given text is Japanese, Korean, or Chinese.

        :param text: The text to analyze.
        :return: Language code ('ja', 'ko', 'zh') or '??' if undetermined.
        """
        # ... (implementation remains unchanged)

    def detect_writing_system(self, text):
        """
        Detect which writing system a text belongs to.

        :param text: The text to analyze.
        :return: The detected writing system or 'cjk' for Chinese, Japanese, or Korean.
        """
        # ... (implementation remains unchanged)

    def is_punctuation(self, char):
        """
        Check if a character is a punctuation mark.

        :param char: The character to check.
        :return: Boolean indicating if the character is punctuation.
        """
        # ... (implementation remains unchanged)

    def split_text_by_writing_system(self, text):
        """
        Split text into segments based on different writing systems.

        :param text: The text to split.
        :return: A list of tuples containing text segments and their writing system.
        """
        # ... (implementation remains unchanged)

    @staticmethod
    def split_non_cjk_in_segment(text):
        """
        Split non-CJK text into individual words or punctuation.

        :param text: The text to split.
        :return: A list of words and punctuation marks.
        """
        return re.findall(r'\w+|[^\w\s]', text)

    def _tokenize(self, text):
        """
        Tokenize text by detecting writing systems and handling punctuation.

        :param text: The text to tokenize.
        :return: A string with tokenized and tagged text.
        """
        # ... (implementation remains unchanged)

    @staticmethod
    def _group_segments(text):
        """
        Group segments of the same language or writing system together.

        :param text: The tokenized text to group.
        :return: A string with grouped segments.
        """
        # ... (implementation remains unchanged)

    def tokenize(self, text, group=True):
        """
        Tokenize input text and optionally group segments of the same writing system.

        :param text: The input text to tokenize.
        :param group: Boolean indicating whether to group segments (default is True).
        :return: A string with tokenized and optionally grouped text.
        """
        result = self._tokenize(text)
        if group:
            result = self._group_segments(result)
        if "<??>" in result:
            warnings.warn(
                "Your output contains tokenization errors. We were unable to detect a language or writing system, or there was an error in processing.")
        return result

if __name__ == "__main__":
    input_text = "hello, 你好は中国語でこんにちはと言う意味をしています。مرحبا! Привет! नमस्ते!"
    token = Tokenizer()
    processed_text = token.tokenize(input_text)
    print("Input text:")
    print(input_text)
    print("\nProcessed text:")
    print(processed_text)
    print(print_colored_text(processed_text))