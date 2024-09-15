from ruphon import RUPhon
from ruaccent import RUAccent
import torch

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

class Phonemizer:
    def __init__(self, working_path=None):
        self.phonemizer = RUPhon()
        self.phonemizer = self.phonemizer.load("small", workdir=working_path, device=device)

        self.accentizer = RUAccent()
        self.accentizer.load(omograph_model_size='turbo3', use_dictionary=True, tiny_mode=False)

    def phonemize(self, text):
        accented_text = self.accentizer.process_all(text)

        result = self.phonemizer.phonemize(accented_text, put_stress=True, stress_symbol="'")

        return result