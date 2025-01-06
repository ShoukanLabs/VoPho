import warnings
from termcolor import colored
from .phonemizers import english, japanese, mandarin, russian, thai
from .langtokenizers.multicoded import Tokenizer, LANGUAGE_COLORS
import re


class Phonemizer:
    """
    A class for phonemizing text in multiple languages,
    """

    def __init__(self, working_path=None, stress=False):
        """
        Initialize the Phonemizer.

        :param working_path: Optional path for working directory
        :param stress: Optional toggle for stress, for phonemisers that support it
        """
        self.working_path = working_path
        self.stress = stress
        self._phonemizers = {}
        self.Tokenizer = Tokenizer()

    def pretty_print(self, phonemized_dict: list):
        """
        Print the phonemized text with colors based on language.

        :param phonemized_dict: A list of dictionaries containing phonemized text segments and their languages
        """
        for segment in phonemized_dict:
            text = segment['text']
            lang = segment['lang']

            pattern = r'<\?\?>(.*?)</\?\?>'

            # Determine the color based on the language
            color = LANGUAGE_COLORS[lang]

            # Replace the tagged content with colored content
            def replace_with_color(match):
                return '\033[1m' + f"{match.group(1)}" + '\033[0m'

            # Substitute the pattern with colored text
            colored_text = re.sub(pattern, replace_with_color, text)

            # Print the text with the corresponding color
            print(colored(colored_text, color), end='')
        print("")

    def get_phonemizer(self, lang):
        """
        Get or create a phonemizer for the specified language.

        :param lang: Language code (e.g., 'en', 'ja', 'zh', 'ru')
        :return: A phonemizer instance for the specified language, or None if not supported
        """
        if lang not in self._phonemizers:
            if lang == 'en':
                self._phonemizers[lang] = english.Phonemizer(stress=self.stress)
            elif lang == 'ja':
                self._phonemizers[lang] = japanese.Phonemizer()
            elif lang == 'zh':
                self._phonemizers[lang] = mandarin.Phonemizer()
            elif lang == 'cy': # cyrillic treated as russian
                self._phonemizers[lang] = russian.Phonemizer(working_path=self.working_path)
            elif lang == 'th':
                self._phonemizers[lang] = thai.Phonemizer()
        return self._phonemizers.get(lang)

    def seperate_languages(self, text):
        """
        Separate the input text into segments based on language tags.

        :param text: Input text with language tags
        :return: A list of dictionaries containing text segments and their languages
        """
        text = self.Tokenizer.tokenize(text)

        pattern = r'(<(\w+)>(.*?)</\2>)|([^<]+)'
        matches = re.findall(pattern, text)

        result = []
        current_item = {"text": "", "lang": None}

        for match in matches:
            if match[1]:  # Tagged content
                lang, content = match[1], match[2]
                if current_item["lang"] != lang:
                    if current_item["text"]:
                        result.append(current_item)
                    current_item = {"text": content, "lang": lang}
                else:
                    current_item["text"] += content
            else:  # Untagged content (punctuation or spaces)
                untagged_content = match[3]
                if current_item["text"]:
                    current_item["text"] += untagged_content
                else:
                    result.append({"text": untagged_content, "lang": "untagged"})

        if current_item["text"]:
            result.append(current_item)

        return result

    def phonemize_for_language(self, text, lang):
        """
        Phonemize the given text for a specific language.

        :param text: The plaintext to phonemize
        :param lang: The language ID for phonemization
        :return: Phonemized text, or original text wrapped in <??> tags if language is not supported
        """
        if lang != "phoneme":
            phonemizer = self.get_phonemizer(lang)
            if phonemizer:
                return phonemizer.phonemize(text)
            return f"<??>{text}</??>"  # Return original text if no phonemizer available
        else:
            return text

    def phonemize(self, input_text, output_dict=False):
        """
        Phonemize the input text, handling multiple languages including CJK.

        :param input_text: The input text to phonemize
        :param output_dict: If True, return a list of dictionaries with text and language; if False, return a single string
        :return: Phonemized text as a string or list of dictionaries
        """
        separated = self.seperate_languages(input_text)
        result = []

        for item in separated:
            # if self.Tokenizer.detect_japanese_korean_chinese(item["text"]) != "??":
            #     result.append(self._process_cjk_segment(item))
            # else:
            result.append(item)


        phonemized_result = []
        for item in result:
            phonemized_text = self.phonemize_for_language(item['text'], item['lang'])
            if output_dict:
                lang = item["lang"] if "??" not in phonemized_text else "??"
                phonemized_result.append({"text": phonemized_text, "lang": lang})
            else:
                phonemized_result.append(phonemized_text)

        if not output_dict:
            fin = ''.join(phonemized_result)
            if "<??>" in fin:
                warnings.warn(
                    "Your output contains unsupported languages, "
                    "<??> tags have been added to allow for manual filtering")
            return fin
        else:
            return phonemized_result

    def _process_cjk_segment(self, item):
        """
        Process a CJK (Chinese, Japanese, Korean) text segment.

        :param item: A dictionary containing the text segment and its language
        :return: A list of dictionaries with processed CJK segments and their detected languages
        """
        processed_segments = []
        segmentsCJKog = self.Tokenizer.split_non_cjk_in_segment(item["text"])

        for CJKog in segmentsCJKog:
            phonemized_text = self.phonemize_for_language(CJKog, item['lang'])
            segmentsCJK = self.Tokenizer.split_non_cjk_in_segment(phonemized_text)

            for CJK in segmentsCJK:
                CJKLang = self.Tokenizer.detect_japanese_korean_chinese(CJK)
                if CJKLang != "??":
                    processed_segments.append({"text": CJK, "lang": CJKLang})

                    remaining = str(CJKog.split(CJK, 1)[-1])
                    remaining = remaining.replace(CJK.strip(), "")
                    if remaining:
                        remaining_lang = self.Tokenizer.detect_japanese_korean_chinese(remaining)
                        processed_segments.append({"text": remaining, "lang": remaining_lang})

        return processed_segments


if __name__ == "__main__":
    input_text = "hello, 你好は中国語でこんにちはと言う意味をしています。مرحبا! Привет! नमस्ते!"
    engine = Phonemizer()
    from time import time

    start = time()
    output = engine.phonemize(input_text, output_dict=True)
    end = time()
    print(input_text)
    engine.pretty_print(output)
    print(f"Took - First: {end - start}")

    start = time()
    output = engine.phonemize(input_text, output_dict=True)
    end = time()
    print(input_text)
    engine.pretty_print(output)
    print(f"Took - Instantiated: {end - start}")