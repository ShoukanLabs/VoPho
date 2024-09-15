import warnings

from termcolor import colored

from phonemizers import english, japanese, mandarin, russian
from langtokenizers.multicoded import Tokenizer, LANGUAGE_COLORS
import re

class Phonemizer:
    def __init__(self, working_path=None):
        self.working_path = working_path
        self._phonemizers = {}
        self.Tokenizer = Tokenizer()

    def pretty_print(self, phonemized_dict: dict):
        """
        Takes the dict output from the phonemization and prints it with colors from LANGUAGE_COLORS.
        Unknown languages should be marked in bold dark red.
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

    def get_phonemizer(self, lang):
        if lang not in self._phonemizers:
            if lang == 'en':
                self._phonemizers[lang] = english.Phonemizer()
            elif lang == 'ja':
                self._phonemizers[lang] = japanese.Phonemizer()
            elif lang == 'zh':
                self._phonemizers[lang] = mandarin.Phonemizer()
            elif lang == 'ru':
                self._phonemizers[lang] = russian.Phonemizer(working_path=self.working_path)
        return self._phonemizers.get(lang)

    def seperate_languages(self, text):
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

    def phonemize_text_segment(self, text, lang):
        phonemizer = self.get_phonemizer(lang)
        if phonemizer:
            return phonemizer.phonemize(text)
        return f"<??>{text}</??>"  # Return original text if no phonemizer available

    def phonemize(self, input_text, output_dict=False):
        separated = self.seperate_languages(input_text)
        result = []
        for item in separated:
            phonemized_text = self.phonemize_text_segment(item['text'], item['lang'])
            checked_languages = self.Tokenizer.detect_japanese_korean_chinese(phonemized_text)
            if item["lang"] in ["zh", "ja", "ko"]:
                if checked_languages != "??":
                    segmentsCJK = self.Tokenizer.split_non_cjk_in_segment(phonemized_text)
                    for CJK in segmentsCJK:
                        CJKLang = self.Tokenizer.detect_japanese_korean_chinese(CJK)
                        if CJKLang != "??":
                            phonemized_text = phonemized_text.replace(CJK,
                                                                      self.phonemize_text_segment(CJK, CJKLang))

                            if output_dict:
                                result.append({"text": phonemized_text, "lang": CJKLang})
            else:
                if output_dict:
                    if not "??" in phonemized_text:
                        result.append({"text": phonemized_text, "lang": item["lang"]})
                    else:
                        result.append({"text": phonemized_text, "lang": "??"})

            if not output_dict:
                result.append(phonemized_text)
                fin = ''.join(result)

                if "<??>" in fin:
                    warnings.warn(
                        "Your output contains unsupported languages, "
                        "<??> tags have been added to allow for manual filtering")
            else:
                fin = result

        return fin

if __name__ == "__main__":
    input_text = "hello, 你好は中国語でこんにちはと言う意味をしています。مرحبا! Привет! नमस्ते!"
    engine = Phonemizer()
    output = engine.phonemize(input_text, output_dict=True)
    print(input_text)
    engine.pretty_print(output)