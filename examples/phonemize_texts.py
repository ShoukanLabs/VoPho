from VoPho.engine import Phonemizer
from time import time

input_text = "An understanding of the natural world is a source of not only great curiosity, but great fulfilment."

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