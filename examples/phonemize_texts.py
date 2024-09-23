from VoPho.engine import Phonemizer
from time import time

input_text = "hello, 你好は中国語でこんにちはと言う意味をしています。 ます。 (testing, this is a test) [me too], Привет"

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