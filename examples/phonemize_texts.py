from VoPho.engine import Phonemizer
from time import time

input_text = "just because i read the script doesn't mean i know how to read! 音素のテストを行うことは、発音の理解を深めるために重要です。"

engine = Phonemizer(stress=True)
start = time()
output = engine.phonemize(input_text, output_tokens=True)
end = time()
print(input_text)
print(output)
engine.pretty_print(output[1])
print(f"Took - First: {end - start}")

for i in range(5):
    start = time()
    output = engine.phonemize(input_text, output_tokens=True)
    end = time()
    print(input_text)
    engine.pretty_print(output[1])
    print(f"Took - Instantiated: {end - start}")