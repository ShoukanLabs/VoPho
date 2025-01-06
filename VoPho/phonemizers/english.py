import os
import re

import nltk
from openphonemizer import OpenPhonemizer

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from pywsd.lesk import simple_lesk

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

model = SentenceTransformer('all-MiniLM-L6-v2')

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
    if query not in definitions:
        query_embedding = model.encode([query])
        definition_embeddings = model.encode(list(definitions.keys()))

        # Calculate cosine similarity between the query and the definitions
        similarities = cosine_similarity(query_embedding, definition_embeddings)

        # Find the index of the most similar definition
        most_similar_index = similarities.argmax()

        # Return the most similar definition
        most_similar_definition = list(definitions.keys())[most_similar_index]
        return most_similar_definition, definitions[most_similar_definition]
    else:
        return query, definitions[query]

# Function to check if a word is a homonym
def is_homonym(word):
    synsets = wordnet.synsets(word)

    filtered_sysnets = []

    for synset in synsets:
        if word == synset.name().split(".")[0].lower():
            filtered_sysnets.append(synset)

    return len(filtered_sysnets) > 1


# Function to generate pronunciation dictionary for homonyms
def generate_pronunciation_dict(word):
    synsets = wordnet.synsets(word)
    pronunciation_dict = {}

    for synset in synsets:
        if synset.name().split(".")[0].lower() == word:
            definition = synset.definition()
            # Get the lemma name for transcription
            lemma_name = synset.lemmas()[0].name().replace("_", " ")
            # Generate IPA pronunciation using Epitran
            _, ipa_pronunciation = get_most_similar_definition(word, definition)
            pronunciation_dict[definition] = ipa_pronunciation

    return pronunciation_dict


def replace_homonyms(text):
    verbose = False

    # Use regex to split text while keeping the delimiters
    tokens = re.findall(r'\S+|\s+', text)
    result = tokens.copy()

    # Keep track of homonym indices to process each separately
    homonym_indices = []

    # First pass: identify homonym indices
    for i, token in enumerate(tokens):
        if not token.isspace():
            word_lower = token.lower()
            if is_homonym(word_lower):
                homonym_indices.append(i)

    # Process each homonym separately
    for index in homonym_indices:
        # Create a context window around the current word
        context_start = max(0, index - 3)
        context_end = min(len(tokens), index + 5)

        # Extract context
        context_tokens = tokens[context_start:context_end]
        context = ''.join(context_tokens).lower()

        # Focus on the specific word
        current_word = tokens[index].lower()

        # Disambiguate meaning using Lesk with the specific context
        sense = simple_lesk(context, current_word)

        if sense:
            meaning = sense.definition()
            # Generate pronunciation dictionary for the word
            pronunciation_dict = generate_pronunciation_dict(current_word)

            # Find pronunciation for the matching meaning
            pronunciation = pronunciation_dict.get(meaning, current_word)

            # Verbose output if requested
            if verbose:
                # Prepare sliding context window with padding
                context_display = ''.join(context_tokens)
                context_width = 20  # Fixed width for consistent display
                context_padded = (context_display.center(context_width))[:context_width]

                # Prepare meaning with padding/trimming
                meaning_width = 50  # Fixed width for consistent display
                meaning_padded = (meaning[:meaning_width].center(meaning_width))[:meaning_width]

                # Print in a formatted way
                print(f"[{context_padded}] - {meaning_padded}\r")

            # Replace the token with phoneme representation
            result[index] = f"<phoneme>{pronunciation}</phoneme>"

    if verbose:
        print("")
    return ''.join(result)


class Phonemizer:
    def __init__(self, manual_fixes=None, allow_heteronyms=True, stress=False): # temporarily allow heteronyms until we fill the dictionary
        if manual_fixes is None:
            manual_fixes = manual_phonemizations
        self.phonemizer = OpenPhonemizer()

        # Dictionary of manual phonemizations
        self.manual_phonemizations = manual_fixes
        self.allow_heteronyms=allow_heteronyms
        self.stress = stress

        # Post-processing filters
        self.manual_filters = {
            " . . . ": "... ",
            " . ": ". "
        }

        # Regex to detect text wrapped in <phoneme> tags
        self.phoneme_tag_pattern = re.compile(r"<phoneme>(.*?)</phoneme>")

    def preprocess(self, text):
        if not self.allow_heteronyms:
            text = replace_homonyms(text)

        # Replace words in the text with their manual phonemizations wrapped in <phoneme> tags
        for word, ipa in self.manual_phonemizations.items():
            text = re.sub(rf"\b{word}\b", f"<phoneme>{ipa}</phoneme>", text, flags=re.IGNORECASE)
        return text

    def postprocess(self, text):
        # Remove the <phoneme> tags but retain the IPA within them, preserving spaces
        if not self.stress:
            text = re.sub("ˈ", "", text)
            text = re.sub("\u02C8", "", text) # double check

        return self.phoneme_tag_pattern.sub(r"\1", text)

    def phonemize(self, text):
        # Preprocess the text for manual phonemizations
        preprocessed_text = self.preprocess(text)

        result = []
        in_quotes = False
        current_segment = ""

        i = 0
        while i < len(preprocessed_text):
            # Check for phoneme tags
            phoneme_match = self.phoneme_tag_pattern.match(preprocessed_text, i)
            if phoneme_match:
                # Append the phoneme tag content and preserve spaces before and after
                if current_segment:
                    result.append(self.phonemizer(current_segment))
                    current_segment = ""

                result.append(phoneme_match.group(1))  # Add the IPA content directly
                i = phoneme_match.end()
                continue

            char = preprocessed_text[i]

            if char == '"':
                if current_segment:
                    if not in_quotes:
                        processed_segment = self.phonemizer(current_segment)
                    else:
                        processed_segment = f'{self.phonemizer(current_segment)}'
                    result.append(processed_segment)
                    current_segment = ""

                result.append(char)
                in_quotes = not in_quotes
            else:
                current_segment += char

            i += 1

        # Process any remaining text
        if current_segment:
            if not in_quotes:
                processed_segment = self.phonemizer(current_segment)
            else:
                processed_segment = f'"{self.phonemizer(current_segment)}"'
            result.append(processed_segment)

        phonemized_text = ''.join(result)

        # Apply manual filters
        for filter, item in self.manual_filters.items():
            phonemized_text = phonemized_text.replace(filter, item)

        # Post-process to remove phoneme tags
        final_text = self.postprocess(phonemized_text)

        return final_text


if __name__ == "__main__":
    phonem = Phonemizer()
    test_text = "i tear the paper apart, water welling up in my eyes, a tear in my eye"
    print(f"Original: {test_text}")
    print(f"Phonemized: {phonem.phonemize(test_text)}")
