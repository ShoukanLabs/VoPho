import warnings

from fast_langdetect import detect
import re

CJK_UNICODE_RANGES = {
    'zh': [(0x4E00, 0x9FFF), (0x3400, 0x4DBF), (0x20000, 0x2A6DF), (0x2A700, 0x2B73F), (0x2B740, 0x2B81F)],
    'ja': [(0x3040, 0x309F), (0x30A0, 0x30FF)],  # Hiragana and Katakana ranges for Japanese
    'ko': [(0xAC00, 0xD7AF)]  # Hangul range for Korean
}


class Tokenizer:
    def __init__(self):
        """
        The base VoPho tokenizer class
        """

    def tokenize(self, text, group=True):
        """
        :param text: the text to tokenize
        :param group: whether to group words of the same LangID, defaults to true

        :returns string:
        """
        result = self._tokenize(text)
        if group:
            result = self._group_segments(result)
        if "<??>" in result:
            warnings.warn("You're output resulted in tokenization errors, we were unable to detect a language or the "
                          "input resulted in an error, please filter the resulting output before phonemization."
                          )
        return result

    @staticmethod
    def is_cjk(char):
        code_point = ord(char)
        for ranges in CJK_UNICODE_RANGES.values():
            for start, end in ranges:
                if start <= code_point <= end:
                    return True
        return False

    @staticmethod
    def detect_japanese_korean_chinese(text):
        is_japanese = False
        is_korean = False
        is_chinese = False

        for char in text:
            code_point = ord(char)

            # Check for Chinese characters (CJK ideograms)
            if any(start <= code_point <= end for start, end in CJK_UNICODE_RANGES['zh']):
                is_chinese = True

            # Check for Japanese characters (Hiragana, Katakana)
            if any(start <= code_point <= end for start, end in CJK_UNICODE_RANGES['ja']):
                is_japanese = True

            # Check for Korean characters (Hangul)
            if any(start <= code_point <= end for start, end in CJK_UNICODE_RANGES['ko']):
                is_korean = True

        if is_japanese:
            return "ja"
        elif is_korean:
            return "ko"
        elif is_chinese:
            return "zh"
        else:
            return "??"

    @staticmethod
    def is_punctuation(char):
        return not char.isalnum() and not char.isspace()

    def split_cjk_non_cjk(self, text):
        segments = []
        current_segment = ""
        current_type = None  # None means not determined yet

        for char in text:
            if self.is_punctuation(char):  # Handle punctuation separately
                if current_segment:
                    segments.append((current_segment, current_type))
                    current_segment = ""
                segments.append((char, "punctuation"))
                current_type = None  # Reset after punctuation
            elif self.is_cjk(char):  # Handle CJK characters
                if current_type == "non-cjk":
                    segments.append((current_segment, "non-cjk"))
                    current_segment = ""
                current_type = "cjk"
                current_segment += char
            else:  # Handle non-CJK characters
                if current_type == "cjk":
                    segments.append((current_segment, "cjk"))
                    current_segment = ""
                current_type = "non-cjk"
                current_segment += char

        # Append the last segment if any
        if current_segment:
            segments.append((current_segment, current_type))

        return segments

    @staticmethod
    def split_non_cjk_in_segment(text):
        return re.findall(r'\w+|[^\w\s]', text)

    def _tokenize(self, text):
        segments = self.split_cjk_non_cjk(text)
        processed_segments = []

        for segment, seg_type in segments:
            if seg_type == "cjk":
                lang = self.detect_japanese_korean_chinese(segment)
                processed_segments.append(f"<{lang}>{segment}</{lang}>")
            elif seg_type == "punctuation":
                processed_segments.append(f"<punctuation>{segment}</punctuation>")
            else:
                words = self.split_non_cjk_in_segment(segment)
                current_lang = None
                current_segment = ""

                for word in words:
                    if self.is_punctuation(word):
                        processed_segments.append(f"<punctuation>{word}</punctuation>")
                        continue
                    try:
                        lang = detect(word)["lang"]
                        if lang != current_lang:
                            if current_segment:
                                processed_segments.append(f"<{current_lang}>{current_segment.strip()}</{current_lang}>")
                                current_segment = ""
                            current_lang = lang
                        current_segment += word + " "
                    except:
                        if current_segment:
                            processed_segments.append(f"<??>{current_segment.strip()}</??>")
                            current_segment = ""
                        current_lang = None
                        processed_segments.append(word)

                if current_segment:
                    processed_segments.append(f"<{current_lang}>{current_segment.strip()}</{current_lang}>")

        return "".join(processed_segments)

    @staticmethod
    def _group_segments(text):
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
                    if segment == '':  # Add space after content
                        current_content[-1] += segment
                    else:  # Append punctuation to the last content item
                        current_content[-1] += segment
                else:
                    grouped_segments.append(segment)  # Append punctuation directly if current_content is empty

        if current_content:
            grouped_segments.append(f"<{current_lang}>{''.join(current_content)}</{current_lang}>")

        fintext = ''.join(grouped_segments)

        return fintext.replace("<punctuation>", "").replace("</punctuation>", "")


if __name__ == "__main__":
    input_text = "你好は中国語でこんにちはと言う意味をしています。"
    token = Tokenizer()
    processed_text = token.tokenize(input_text)
    print("input text:")
    print(input_text)
    print("\nout text:")
    print(processed_text)
