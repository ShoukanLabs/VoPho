from dataclasses import dataclass


@dataclass
class Token:
    graphemes: str
    phonemes: str
    language: str
    whitespace: bool
    start_second: float = 0
    end_second: float = 0
