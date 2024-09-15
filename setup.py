from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="VoPho",
    version="0.0.1",
    author="ShoukanLabs.",
    description="An easy to use Multilingual phonemization meta-library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShoukanLabs/VoPho",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "ruphon==1.3@git+https://github.com/korakoe/ruphon.git",
        "ruaccent==1.5.8"
        "cn2an==0.5.22",
        "colorama==0.4.6",
        "termcolor==2.4.0",
        "openphonemizer==0.1.2",
        "unidic-lite==1.0.8",
        "mecab-python3==1.0.9",
        "cutlet==0.4.0",
        "jieba==0.42.1",
        "pypinyin==0.52.0",
        "torch==2.1.2",
        "fast-langdetect==0.2.1"
    ],
    keywords=['Phonemization', 'TTS', 'Multilingual'],
)