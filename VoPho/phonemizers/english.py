from openphonemizer import OpenPhonemizer


class Phonemizer:
    def __init__(self):
        self.phonemizer = OpenPhonemizer()

        # post-processing
        self.manual_filters = {
            " . . . ": "... ",
            " . ": ". "
        }

    def phonemize(self, text):
        result = []
        in_quotes = False
        current_segment = ""

        for char in text:
            if char == '"':
                # Process the current segment before changing quote state
                if current_segment:
                    if not in_quotes:
                        processed_segment = self.phonemizer(current_segment)
                    else:
                        processed_segment = f'{self.phonemizer(current_segment)}'
                    result.append(processed_segment)
                    current_segment = ""

                # Add the quote character and flip the state
                result.append(char)
                in_quotes = not in_quotes
            else:
                current_segment += char

        # Process any remaining text
        if current_segment:
            if not in_quotes:
                processed_segment = self.phonemizer(current_segment)
            else:
                processed_segment = f'"{self.phonemizer(current_segment)}"'
            result.append(processed_segment)

        result = ''.join(result)

        # apply manual filters
        for filter, item in self.manual_filters.items():
            result = result.replace(filter, item)

        return result


if __name__ == "__main__":
    phonem = Phonemizer()
    test_text = 'this is a test, "sometimes this is removed", and this is not. graduation is a key part of... celebration'
    print(f"Original: {test_text}")
    print(f"Phonemized: {phonem.phonemize(test_text)}")