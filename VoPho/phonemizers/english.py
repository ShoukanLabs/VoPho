import os
import re

import nltk
from misaki import en
from openphonemizer import OpenPhonemizer

from pywsd.lesk import simple_lesk

from functools import lru_cache

nltk.download("wordnet", quiet=True)

from nltk.corpus import wordnet

os.environ['PYTHONIOENCODING'] = 'utf-8'

import epitran

# Initialize Epitran for IPA transcription
# Enforce UTF-8 globally
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    epi = epitran.Epitran('eng-Latn')
except UnicodeDecodeError:
    raise OSError("epitran could not be loaded. if you're on windows, in control panel > region, "
                  "Check Beta: Use Unicode UTF-8 for worldwide language support")

from nltk.tokenize import word_tokenize

general = {
    # Basic contractions and common words
    "y'all": "jɔːl"
}

# Proper names and common mispronunciations
proper_names = {
    "Amazon": "ˈæməˌzɒn",
    "Microsoft": "ˈmaɪkrəˌsɒft",
    "Spotify": "ˈspɒtɪfaɪ",
    "Facebook": "ˈfeɪsˌbʊk",
    "Twitter": "ˈtwɪtər",
    "YouTube": "ˈjuːˌtjuːb",
    "Instagram": "ˈɪnstəˌɡræm",
    "Samsung": "ˈsæmˌsʌŋ",
    "Apple": "ˈæpəl",
    "Adobe": "əˈdoʊbi",
    "Beyoncé": "biˈjɒnseɪ",
    "Rihanna": "riˈɑːnə",
    "Kanye": "ˈkɑːnjeɪ",
    "J.K. Rowling": "ˌdʒeɪ.keɪ ˈroʊlɪŋ",
    "Harry Potter": "ˈhæri ˈpɒtər",
    "Marvel": "ˈmɑrvəl",
    "DC": "diː siː",
    "Pokemon": "ˈpoʊkɪmɒn",
    "Netflix": "ˈnɛtflɪks",
    "Siri": "ˈsɪri",
    "Alexa": "əˈlɛksə",
    "Tesla": "ˈtɛslə",
    "Quora": "ˈkwɔːrə",
    "Wikipedia": "ˌwɪkɪˈpiːdiə",
    "NVIDIA": "ɛnˈvɪdiə",
    "Snapchat": "ˈsnæpˌtʃæt",
    "LinkedIn": "ˈlɪŋktɪn",
    "Zoom": "zuːm",
    "Twitch": "twɪtʃ",
    "Kombucha": "kəmˈbuːtʃə",
    "Chia": "ˈtʃiːə",
    "Yelp": "jɛlp",
    "TikTok": "tɪkˈtɒk",
    "Duolingo": "ˌdjuːəˈlɪŋɡoʊ",
    "Coca-Cola": "ˈkoʊkəˌkoʊlə",
    "Pepsi": "ˈpɛpsi",
    "Starbucks": "ˈstɑrbʌks",
    "Walmart": "ˈwɔːlmɑːrt",
    "IKEA": "aɪˈkiːə",
    "Uber": "ˈjuːbər",
    "Lyft": "lɪft",
    "KFC": "keɪ ɛf ˈsiː",
    "NBA": "ɛn biː eɪ",
    "NFL": "ɛn ɛf ɛl",
    "FIFA": "ˈfiːfə",
    "NHL": "ɛn eɪtʃ ɛl",
    "Reddit": "ˈrɛdɪt",
    "Tinder": "ˈtɪndər",
    "WordPress": "ˈwɜrdprɛs",
}

# Common mispronunciations
common_mispronunciations = {
    "meme": "miːm",
    "pasta": "ˈpɑːstə",
    "quinoa": "ˈkiːnwɑː",
    "sriracha": "sɪˈrɑːtʃə",
    "coup": "kuː",
    "genre": "ˈʒɒnrə",
    "cliché": "kliːˈʃeɪ",
    "façade": "fəˈsɑːd",
    "entrepreneur": "ˌɒntrəprəˈnɜːr",
    "ballet": "bæˈleɪ",
    "jalapeño": "ˌhæləˈpeɪnjoʊ",
    "caramel": "ˈkærəˌmɛl",
    "vaccine": "vækˈsiːn",
    "herb": "hɜːrb",  # (often mispronounced as 'urb')
}

innacurate_from_phonemizer = {
    "british": "ˈbrɪt.ɪʃ"
}

# Combine both dictionaries
manual_phonemizations = {**general, **proper_names, **common_mispronunciations, **innacurate_from_phonemizer}

word_definitions = {
    "lead": {
        "to guide or direct": "liːd",
        "a type of metal": "lɛd"
    },
    "tear": {
        "separate or cause to separate abruptly": "tɛər",
        "fill with tears or shed tears": "tɪər"
    },
    "read": {
        "to look at and comprehend written words": "riːd",
        "past tense of read": "rɛd"
    },
    "wind": {
        "moving air": "wɪnd",
        "to twist or coil": "wɪnd"
    },
    "row": {
        "a linear arrangement of things": "roʊ",
        "to propel a boat": "raʊ"
    },
    "live": {
        "to be alive": "lɪv",
        "happening in real time": "laɪv"
    },
    "close": {
        "to shut something": "kloʊs",
        "near": "kloʊs"
    },
    "bass": {
        "a type of fish": "beɪs",
        "low-frequency sound or voice": "bæs"
    }
}


### ^^^ PLACEHOLDER UNTIL MANUAL DICT CREATED

def get_most_similar_definition(word, query):
    if word not in word_definitions:
        return "", word

    # Get the definitions of the word
    definitions = word_definitions[word]

    # Encode the query sentence and definitions using the model

    return query, definitions[query]


# Global cache for filtered synsets, keyed by the lowercase word.
filtered_sysnets = {}


def get_filtered_synsets(word):
    """Return a cached list of synsets for 'word' whose primary name matches the word (case-insensitive)."""
    lw = word.lower()
    if lw not in filtered_sysnets:
        # Filter synsets where the primary lemma (first part of synset.name()) matches lw.
        filtered_sysnets[lw] = [
            synset for synset in wordnet.synsets(word)
            if synset.name().split('.')[0].lower() == lw
        ]
    return filtered_sysnets[lw]


def is_homonym(word):
    """Return True if the word has more than one filtered synset (i.e. is a homonym)."""
    return len(get_filtered_synsets(word)) > 1


@lru_cache(maxsize=None)
def cached_get_most_similar_definition(word, definition):
    """
    Cached wrapper for get_most_similar_definition.
    This prevents repeated heavy computations for the same word/definition pair.
    """
    return get_most_similar_definition(word, definition)


@lru_cache(maxsize=None)
def generate_pronunciation_dict(word):
    """
    Generate a pronunciation dictionary for the word using cached filtered synsets.
    The keys are definitions and the values are IPA pronunciations.
    """
    return {
        synset.definition(): cached_get_most_similar_definition(word, synset.definition())[1]
        for synset in get_filtered_synsets(word)
    }


@lru_cache(maxsize=1024)
def cached_simple_lesk(context, word):
    return simple_lesk(context, word)


def replace_homonyms(text, verbose=False):
    # Split text while keeping whitespace tokens.
    tokens = re.findall(r'\S+|\s+', text)
    # Precompute lower-case version of every token to avoid repeated lower() calls.
    lower_tokens = [token.lower() for token in tokens]
    # Copy tokens to hold replacements.
    result = tokens[:]

    # Process tokens in a single pass.
    for i, token in enumerate(tokens):
        # Only process non-whitespace tokens.
        if not token.isspace():
            current_word = lower_tokens[i]
            if is_homonym(current_word):
                # Create a context window (using indices from the lower_tokens list).
                context_start = max(0, i - 3)
                context_end = min(len(tokens), i + 5)
                # The context is already in lower-case.
                context = ''.join(lower_tokens[context_start:context_end])

                # Use cached simple_lesk to disambiguate the word.
                sense = cached_simple_lesk(context, current_word)
                if sense:
                    meaning = sense.definition()
                    # Retrieve the pronunciation dictionary (cached per word).
                    pronunciation_dict = generate_pronunciation_dict(current_word)
                    # If the definition isn't found, fall back to the word itself.
                    pronunciation = pronunciation_dict.get(meaning, current_word)

                    if verbose:
                        # Build a display string for context (using original tokens).
                        context_display = ''.join(tokens[context_start:context_end])
                        context_width = 20  # fixed width for display
                        context_padded = (context_display.center(context_width))[:context_width]

                        # Build a display string for the meaning.
                        meaning_width = 50  # fixed width for display
                        meaning_padded = (meaning[:meaning_width].center(meaning_width))[:meaning_width]

                        print(f"[{context_padded}] - {meaning_padded}\r")

                    # Replace the token with its phoneme representation.
                    result[i] = f"<phoneme>{pronunciation}</phoneme>"

    if verbose:
        print("")
    return ''.join(result)


### OPEN PHONEMISER FALLBACK

FROM_ESPEAKS = sorted(
    {'\u0303': '', 'a^ɪ': 'I', 'a^ʊ': 'W', 'd^ʒ': 'ʤ', 'e': 'A', 'e^ɪ': 'A', 'r': 'ɹ', 't^ʃ': 'ʧ', 'x': 'k', 'ç': 'k',
     'ɐ': 'ə', 'ɔ^ɪ': 'Y', 'ə^l': 'ᵊl', 'ɚ': 'əɹ', 'ɬ': 'l', 'ʔ': 't', 'ʔn': 'tᵊn', 'ʔˌn\u0329': 'tᵊn', 'ʲ': '',
     'ʲO': 'jO', 'ʲQ': 'jQ'}.items(), key=lambda kv: -len(kv[0]))


class OpenPhonemiserFallback:
    def __init__(self, backend):
        self.backend = backend

    def __call__(self, token):
        ps = self.backend(token.text)

        if not ps:
            return None, None

        for old, new in FROM_ESPEAKS:
            ps = ps.replace(old, new)
        ps = re.sub(r'(\S)\u0329', r'ᵊ\1', ps).replace(chr(809), '')

        ps = ps.replace('o^ʊ', 'O')
        ps = ps.replace('ɜːɹ', 'ɜɹ')
        ps = ps.replace('ɜː', 'ɜɹ')
        ps = ps.replace('ɪə', 'iə')
        ps = ps.replace('ː', '')

        return ps.replace('^', ''), 2


### BASE PHONEMEISER CLASS
class Phonemizer:
    def __init__(self, manual_fixes=None, allow_heteronyms=True, stress=False):
        if manual_fixes is None:
            manual_fixes = manual_phonemizations
        self.backend = OpenPhonemizer()
        self.fallback = OpenPhonemiserFallback(backend=self.backend)
        self.phonemizer = en.G2P(trf=True, british=False, fallback=self.fallback)
        self.manual_phonemizations = manual_fixes
        self.allow_heteronyms = allow_heteronyms
        self.stress = stress
        self.manual_filters = {
            " . . . ": "... ",
            " . ": ". "
        }

        # Precompute normalized manual phonemizations and regex
        self.manual_lower = {word.lower(): (word, ipa) for word, ipa in self.manual_phonemizations.items()}
        sorted_words = sorted(self.manual_phonemizations.keys(), key=lambda x: (-len(x), x))
        escaped_words = [re.escape(word) for word in sorted_words]
        self.manual_pattern = re.compile(r'\b(' + '|'.join(escaped_words) + r')\b', flags=re.IGNORECASE)

        # Precompile regex patterns
        self.phoneme_tag_pattern = re.compile(r"<phoneme>(.*?)</phoneme>")
        self.postprocess_stress_pattern = re.compile(r'[ˈ\u02C8]')

    def preprocess(self, text):
        if not self.allow_heteronyms:
            text = replace_homonyms(text)

        # Replace manual words using a single regex pass
        def replace_match(match):
            key_lower = match.group(0).lower()
            if key_lower in self.manual_lower:
                return f"<phoneme>{self.manual_lower[key_lower][1]}</phoneme>"
            return match.group(0)

        return self.manual_pattern.sub(replace_match, text)

    def postprocess(self, text):
        if not self.stress:
            text = self.postprocess_stress_pattern.sub('', text)
        return self.phoneme_tag_pattern.sub(r'\1', text)

    def phonemize(self, text):
        preprocessed_text = self.preprocess(text)
        segments = self.phoneme_tag_pattern.split(preprocessed_text)

        # Process each text segment (even indices) using the G2P model
        for i in range(0, len(segments), 2):
            if segments[i]:
                segments[i] = self.phonemizer(segments[i])[0]

        phonemized_text = ''.join(segments)

        # Apply manual filters
        for filter_str, replacement in self.manual_filters.items():
            phonemized_text = phonemized_text.replace(filter_str, replacement)

        return self.postprocess(phonemized_text)


if __name__ == "__main__":
    phonem = Phonemizer(stress=True)
    test_text = "'two heads is better than one.', "
    print(f"Original: {test_text}")
    print(f"Phonemized: {phonem.phonemize(test_text)}")
