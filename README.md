# VoPho

VoPho is a phonemization meta-library designed to make multilingual phonemization fast, accessible, multilingual, and accurate!

## Installation

You can install VoPho via pip:

```bash
pip install VoPho
```

# Quick Start
Here's a quick example of how to use VoPho to phonemize multilingual text:

```python
from VoPho.engine import Phonemizer
from time import time

# Example input text in multiple languages
from VoPho.engine import Phonemizer
from time import time

input_text = "<phoneme>I suppose i can</phoneme>, dont take my word for it though. 音素のテストを行うことは、発音の理解を深めるために重要です。"

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

```

```
<phoneme>I suppose i can</phoneme>, dont take my word for it though. 音素のテストを行うことは、発音の理解を深めるために重要です。
I suppose i can, dɔnt teɪk maɪ wɜːd fɔːɹ ɪt ðˌoʊ. onso no tesɯto o okonaɯ koto wa, hatsɯoɴ no ɽikai o fɯkamerɯ tame ni dʑɯɯjoɯ desɯ. 
Took - First: 8.168637990951538

<phoneme>I suppose i can</phoneme>, dont take my word for it though. 音素のテストを行うことは、発音の理解を深めるために重要です。
I suppose i can, dɔnt teɪk maɪ wɜːd fɔːɹ ɪt ðˌoʊ. onso no tesɯto o okonaɯ koto wa, hatsɯoɴ no ɽikai o fɯkamerɯ tame ni dʑɯɯjoɯ desɯ. 
Took - Instantiated: 0.02039504051208496
```

you can also use:
```
engine.phonemize_for_language(text, lang="ISO LANG ID (en, zh, etc.)")

OR

<en>Language tags like this</en>
```

to force particular languages

# Features
- Fast: Optimized for performance.
- Accessible: Easy to integrate and use.
- Multilingual: Supports a wide range of languages.
- Accurate: Provides precise phonemization.

# Supported Languages
| Language  | Supported           | Verified Accuracy     | Notes                                                                                 |
|-----------|---------------------|-----------------------|---------------------------------------------------------------------------------------|
| English   | Yes                 | Yes                   | Fully supported and verified (under heavy development - currently on par with espeak) |
| Russian   | Yes                 | Yes                   | Fully supported and verified                                                          |
| French    | Planned             | N/A                   | Planned for future support                                                            |
| German    | Planned             | N/A                   | Planned for future support                                                            |
| Spanish   | Planned             | N/A                   | Planned for future support                                                            |
| Italian   | Planned             | N/A                   | Planned for future support                                                            |
| Mandarin  | Yes                 | Yes                   | Fully supported and verified                                                          |
| Japanese  | Yes                 | Yes                   | Fully supported and verified                                                          |
| Korean    | Planned             | N/A                   | Planned for future support                                                            |
| Thai      | Yes                 | No                    | Supported, accuracy unverified                                                        |
| Arabic    | Planned (Difficult) | N/A                   | Planned for future support                                                            |
| Persian   | Planned (Difficult) | N/A                   | Planned for future support                                                            |
| Norwegian | Planned             | Yes (government body) | Planned for future support                                                            |


# License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/ShoukanLabs/VoPho/blob/main/LICENSE) file for details.