import json
import os
import string
import warnings
import re
from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException
from lingua import LanguageDetectorBuilder
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
}

# Mapping of predefined language codes to specific colors
LANGUAGE_COLORS = {
    'en': 'green',
    'zh': 'yellow',
    'ja': 'cyan',
    'ko': 'blue',
    'ar': 'green',
    'cy': 'magenta',
    'hi': 'red',
    'mr': 'red',
    'he': 'white',
    'th': 'blue',
    'phoneme': 'blue',
    '??': 'red'
}

unknown_language_colors = {}


def random_color():
    colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    return random.choice(colors)


def print_colored_text(text):
    pattern = r'<(\w+)>(.*?)</\1>'
    last_pos = 0

    for match in re.finditer(pattern, text):
        lang, content = match.groups()
        start, end = match.span()

        if last_pos < start:
            print(text[last_pos:start], end="")

        if lang not in LANGUAGE_COLORS:
            if lang not in unknown_language_colors:
                unknown_language_colors[lang] = random_color()
            color = unknown_language_colors[lang]
        else:
            color = LANGUAGE_COLORS[lang]

        if lang == "??":
            color = 'red'

        print(colored(content, color), end="")
        last_pos = end

    if last_pos < len(text):
        print(text[last_pos:])


def load_manual_word_dict(file_path='manual_word_dict.json'):
    base_path = os.path.dirname(__file__)  # Directory of the current file
    file_path = os.path.join(base_path, file_path)
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # print(f"Warning: {file_path} not found. Using empty dictionary.")
        return {}


def manual_tag(sentence, manual_word_dict):
    # Convert the sentence to lowercase and strip it of extra spaces
    sentence_lower = sentence.lower().strip()
    # Split the sentence into words
    words = sentence_lower.split()
    # Check each word against the manual dictionary
    for word in words:
        # Check if the word is in the manual dictionary
        if word in manual_word_dict:
            return manual_word_dict[word]
    return None  # Return None if no match is found


class Tokenizer:
    def __init__(self):
        self.min_confidence = 0.5
        self.manual_word_dict = load_manual_word_dict()
        self.detector = LanguageDetectorBuilder.from_all_languages().build()

    def detect_language(self, text):
        # Adjusted logic to improve language detection
        text_lower = text.lower().strip()
        manual_lang = manual_tag(text_lower, self.manual_word_dict)
        if manual_lang:
            return manual_lang
        try:
            langs = self.detector.detect_language_of(text)
            if langs is not None:
                langs = langs.iso_code_639_1.name.lower()
                return langs
            else:
                return '??'
        except LangDetectException:
            return '??'

    def is_writing_system(self, char, system):
        if len(char) > 1:
            # Valid punctuation characters, including space
            return all(self.is_writing_system(c) for c in char)  # Check each character individually
        else:
            code_point = ord(char)
            return any(start <= code_point <= end for start, end in WRITING_SYSTEMS_UNICODE_RANGES.get(system, []))

    def detect_japanese_korean_chinese(self, text):
        is_japanese = any(self.is_writing_system(char, 'ja') for char in text)
        is_korean = any(self.is_writing_system(char, 'ko') for char in text)
        is_chinese = any(self.is_writing_system(char, 'zh') for char in text)

        if is_japanese:
            return "ja"
        elif is_korean:
            return "ko"
        elif is_chinese:
            return "zh"
        else:
            return "??"

    def detect_writing_system(self, text):
        for system, ranges in WRITING_SYSTEMS_UNICODE_RANGES.items():
            if any(ord(char) in range(start, end + 1) for char in text for start, end in ranges):
                if system not in ["zh", "ja", "ko"]:
                    return system
                else:
                    return "cjk"
        return None

    def is_punctuation(self, char):
        not_punctuation = ["'", '"', "(", ")", "{", "}", "[", "]", "&"]
        if len(char) > 1:
            # Valid punctuation characters, including space
            return all(self.is_punctuation(c) for c in char)  # Check each character individually
        else:
            # Single character check (as per your original logic)
            return (not char.isalnum()  # Is not alphanumeric
                    and not char.isspace()  # Is not whitespace
                    and not self.is_writing_system(char, self.detect_writing_system(char))
                    and char not in not_punctuation)  # Is not in a writing system                                                                             self.detect_writing_system(

    def split_text_by_writing_system(self, text):
        segments = []
        current_segment = ""
        current_type = None

        for char in text:
            if self.is_punctuation(char):
                if current_segment:
                    segments.append((current_segment, current_type))
                    current_segment = ""
                segments.append((char, "punctuation"))
                current_type = None
            else:
                char_system = self.detect_writing_system(char)
                if char_system != current_type:
                    if current_segment:
                        segments.append((current_segment, current_type))
                    current_type = char_system
                    current_segment = char
                else:
                    current_segment += char

        if current_segment:
            segments.append((current_segment, current_type))

        return segments

    @staticmethod
    def split_non_cjk_in_segment(text):
        return re.findall(r'[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7AF。]'
                          r'+(?:\s*)|[\w.,!?;:\'"(){}\[\]\-–—\s]+', text)

    def _tokenize(self, text):
        segments = self.split_text_by_writing_system(text)

        processed_segments = []

        for segment, seg_type in segments:
            print(f'-{segment}-')
            if seg_type == "cjk":
                lang = self.detect_japanese_korean_chinese(segment)
                processed_segments.append(f"<{lang}>{segment}</{lang}>")
            elif seg_type in WRITING_SYSTEMS_UNICODE_RANGES:
                if seg_type != "deva":
                    processed_segments.append(f"<{seg_type}>{segment}</{seg_type}>")
                else:
                    lang = self.detect_language(segment)
                    processed_segments.append(f"<{lang}>{segment.strip()}</{lang}>")
            elif seg_type == "punctuation" or segment == " ":
                processed_segments.append(f"<punctuation>{segment}</punctuation>")

            else:
                words = self.split_non_cjk_in_segment(segment)
                current_lang = None
                current_segment = ""

                for word in words:
                    if self.is_punctuation(word):
                        if current_segment:
                            processed_segments.append(f"<{current_lang}>{current_segment.strip()}</{current_lang}>")
                            current_segment = ""
                        processed_segments.append(f"<punctuation>{word}</punctuation>")
                        current_lang = None
                    else:
                        lang = self.detect_language(word)
                        if lang != current_lang:
                            if current_segment:
                                processed_segments.append(
                                    f"<{current_lang}>{current_segment.strip()}</{current_lang}>")
                                current_segment = ""
                            current_lang = lang
                        current_segment += word + " "

                # Handle any remaining text
                if current_segment:
                    processed_segments.append(f"<{current_lang}>{current_segment.strip()}</{current_lang}>")

        return "".join(processed_segments)

    def _group_segments(self, text):
        pattern = r'(<(\w+)>.*?</\2>|<punctuation>.*?</punctuation>)'
        tokens = re.findall(pattern, text)

        grouped_segments = []
        current_lang = None
        current_content = []

        for segment, lang in tokens:
            if lang:
                content = re.search(r'<\w+>(.*?)</\w+>', segment).group(1)
                if lang == current_lang:
                    current_content.append(content)
                else:
                    if current_content:
                        grouped_segments.append(f"<{current_lang}>{''.join(current_content)}</{current_lang}>")
                    current_lang = lang
                    current_content = [content]
            else:
                if current_content:
                    current_content[-1] += segment
                else:
                    grouped_segments.append(segment)

        if current_content:
            grouped_segments.append(f"<{current_lang}>{''.join(current_content)}</{current_lang}>")

        # Clean up punctuation handling
        return ''.join(grouped_segments) \
            .replace("<punctuation>", "") \
            .replace("</punctuation>", " ") \
            .replace("  ", " ").strip()

    def tokenize(self, text, group=True):
        # Split the input text into segments based on existing tags
        pattern = r'(<\w+>.*?</\w+>)|([^<]+)'  # Matches either tagged segments or untagged text
        segments = re.findall(pattern, text)

        processed_segments = []

        for tagged_segment, untagged_segment in segments:
            if tagged_segment:  # If this segment is already tagged, just add it
                processed_segments.append(tagged_segment)
            else:  # If the segment is untagged, process it as usual
                result = self._tokenize(untagged_segment)
                processed_segments.append(result)

        result = ''.join(processed_segments)

        if group:
            result = self._group_segments(result)

        if "<??>" in result:
            warnings.warn(
                "Your output contains tokenization errors. We were unable to detect a language or writing system, or there was an error in processing.")

        return result


# Main function
if __name__ == "__main__":
    input_text = "На улице сегодня холодно и пасмурно."
    token = Tokenizer()
    processed_text = token.tokenize(input_text)
    print("Input text:")
    print(input_text)
    print("\nProcessed text:")
    print(processed_text)
    print_colored_text(processed_text)
