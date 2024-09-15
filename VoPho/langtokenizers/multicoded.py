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
    """Returns a random color from the set of basic colors."""
    colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    return random.choice(colors)


def print_colored_text(text):
    """
    Print the tokenized text with each language in a different color.
    New, unseen languages get assigned a random color,
    while unknown languages ('??') get a dark red color.
    """
    pattern = r'<(\w+)>(.*?)</\1>'
    last_pos = 0

    # Iterate over each detected language segment
    for match in re.finditer(pattern, text):
        lang, content = match.groups()
        start, end = match.span()

        # Print any non-matching text before the tokenized segment
        if last_pos < start:
            if text[last_pos:start] is not None:
                print(text[last_pos:start], end="")

        # Assign a random color to new languages
        if lang not in LANGUAGE_COLORS:
            if lang not in unknown_language_colors:
                unknown_language_colors[lang] = random_color()
            color = unknown_language_colors[lang]
        else:
            color = LANGUAGE_COLORS[lang]

        # Assign dark red for undefined languages ('??')
        if lang == "??":
            color = 'red'

        # Print the content in the assigned color
        if content is not None:
            print(colored(content, color), end="")
            last_pos = end

    # Print any remaining part of the text after the last token
    if last_pos < len(text):
        if text[last_pos:] is not None:
            print(text[last_pos:])


class Tokenizer:
    def __init__(self):
        """
        The base VoPho tokenizer class
        """

    @staticmethod
    def is_writing_system(char, system):
        """
        Check if a character belongs to a specific writing system.
        """
        code_point = ord(char)
        return any(start <= code_point <= end for start, end in WRITING_SYSTEMS_UNICODE_RANGES.get(system, []))

    @staticmethod
    def detect_japanese_korean_chinese(text):
        is_japanese = False
        is_korean = False
        is_chinese = False

        for char in text:
            code_point = ord(char)

            # Check for Chinese characters (CJK ideograms)
            if any(start <= code_point <= end for start, end in WRITING_SYSTEMS_UNICODE_RANGES['zh']):
                is_chinese = True

            # Check for Japanese characters (Hiragana, Katakana)
            if any(start <= code_point <= end for start, end in WRITING_SYSTEMS_UNICODE_RANGES['ja']):
                is_japanese = True

            # Check for Korean characters (Hangul)
            if any(start <= code_point <= end for start, end in WRITING_SYSTEMS_UNICODE_RANGES['ko']):
                is_korean = True

        if is_japanese:
            return "ja"
        elif is_korean:
            return "ko"
        elif is_chinese:
            return "zh"
        else:
            return "??"

    def detect_writing_system(self, text):
        """
        Detect which writing system a text belongs to.
        """
        for system, ranges in WRITING_SYSTEMS_UNICODE_RANGES.items():
            if any(ord(char) in range(start, end + 1) for char in text for start, end in ranges):
                if system not in ["zh", "ja", "ko"]:
                    return system
                else:
                    return "cjk"

    def is_punctuation(self, char):
        """
        Check if a character is a punctuation mark.
        """
        return not char.isalnum() and not char.isspace() and not self.is_writing_system(char, self.detect_writing_system(char))

    def split_text_by_writing_system(self, text):
        """
        Split text into segments based on different writing systems.
        """
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
        """
        Split non-CJK text into individual words or punctuation.
        """
        return re.findall(r'\w+|[^\w\s]', text)

    def _tokenize(self, text):
        """
        Tokenize text by detecting writing systems and handling punctuation.
        """
        segments = self.split_text_by_writing_system(text)
        processed_segments = []

        for segment, seg_type in segments:
            if seg_type == "cjk":
                lang = self.detect_japanese_korean_chinese(segment)
                processed_segments.append(f"<{lang}>{segment}</{lang}>")
            elif seg_type in WRITING_SYSTEMS_UNICODE_RANGES:
                if seg_type != "deva":
                    processed_segments.append(f"<{seg_type}>{segment}</{seg_type}>")
                else:
                    try:
                        lang = detect(segment)["lang"]

                        processed_segments.append(f"<{lang}>{segment.strip()}</{lang}>")
                    except Exception as e:
                        processed_segments.append(f"<??>{segment.strip()}</??>")

            elif seg_type == "punctuation":
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
                        try:
                            lang = detect(word)["lang"]
                            if lang != current_lang:
                                if current_segment:
                                    processed_segments.append(
                                        f"<{current_lang}>{current_segment.strip()}</{current_lang}>")
                                    current_segment = ""
                                current_lang = lang
                            current_segment += word + " "
                        except Exception as e:
                            if current_segment:
                                processed_segments.append(f"<??>{current_segment.strip()}</??>")
                                current_segment = ""
                            processed_segments.append(word)
                            current_lang = None

                if current_segment:
                    processed_segments.append(f"<{current_lang}>{current_segment.strip()}</{current_lang}>")

        return "".join(processed_segments)

    @staticmethod
    def _group_segments(text):
        """
        Group segments of the same language or writing system together.
        """
        pattern = r'(<(\w+)>.*?</\2>|[^\w\s])'
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
                    if segment == '':
                        current_content[-1] += segment
                    else:
                        current_content[-1] += segment
                else:
                    grouped_segments.append(segment)

        if current_content:
            grouped_segments.append(f"<{current_lang}>{''.join(current_content)}</{current_lang}>")

        return (''.join(grouped_segments).replace("<punctuation>", "")
                .replace("</punctuation>", " "))

    def tokenize(self, text, group=True):
        """
        Tokenize input text and optionally group segments of the same writing system.
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