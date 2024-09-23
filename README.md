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
input_text = "hello, 你好は中国語でこんにちはと言う意味をしています。 Привет!"

# Instantiate the Phonemizer
engine = Phonemizer()

# Measure the time taken to phonemize
start = time()
output = engine.phonemize(input_text, output_dict=True)
end = time()
print(input_text)
engine.pretty_print(output)
print(f"Took - First: {end - start}")

# Measure the time taken for subsequent calls
start = time()
output = engine.phonemize(input_text, output_dict=True)
end = time()
print(input_text)
engine.pretty_print(output)
print(f"Took - Instantiated: {end - start}")

```

```
>>> OUTPUT: həlˈoʊ, ni˨˩˦hɑʊ˨˩˦ wa tɕɯɯgokɯ go de konnitɕiha to iɯ imi o ɕite imasɯ. prʲɪvʲ'et!
```

# Features
- Fast: Optimized for performance.
- Accessible: Easy to integrate and use.
- Multilingual: Supports a wide range of languages.
- Accurate: Provides precise phonemization.

# Supported Languages
| Language   | Supported | Verified Accuracy | Notes                          |
|------------|-----------|-------------------|--------------------------------|
| English    | Yes       | Yes               | Fully supported and verified   |
| Russian    | Yes       | Yes               | Fully supported and verified   |
| French     | Planned   | N/A               | Planned for future support     |
| German     | Planned   | N/A               | Planned for future support     |
| Spanish    | Planned   | N/A               | Planned for future support     |
| Italian    | Planned   | N/A               | Planned for future support     |
| Mandarin   | Yes       | Yes               | Fully supported and verified   |
| Japanese   | Yes       | Yes               | Fully supported and verified   |
| Korean     | Planned   | N/A               | Planned for future support     |
| Thai       | Yes       | No                | Supported, accuracy unverified |
| Arabic     | Planned   | N/A               | Planned for future support     |
| Persian    | Planned   | N/A               | Planned for future support     |


# License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/ShoukanLabs/VoPho/blob/main/LICENSE) file for details.