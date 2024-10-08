from VoPho.engine import Phonemizer
from time import time

input_text = "I suppose i can, dont take my word for it though. 音素のテストを行うことは、発音の理解を深めるために重要です。"

engine = Phonemizer()
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