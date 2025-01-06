import json
import nltk
from nltk.corpus import wordnet
from nltk.corpus import cmudict
from pywsd.lesk import simple_lesk

# Download necessary NLTK resources
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('cmudict', quiet=True)

# Load CMUDict
pronunciations = cmudict.dict()


def has_multiple_pronunciations(word):
    """Check if a word has multiple distinct pronunciations in CMUDict."""
    # Convert to lowercase as CMUDict entries are lowercase
    word = word.lower()

    # Check if word exists in CMUDict
    if word not in pronunciations:
        return False

    # Get all pronunciations
    word_pronunciations = pronunciations[word]

    # If there's only one pronunciation, return False
    if len(word_pronunciations) <= 1:
        return False

    # Check if the pronunciations are actually different
    # Convert tuples to strings for comparison
    unique_pronunciations = set(' '.join(p) for p in word_pronunciations)

    return len(unique_pronunciations) > 1


# Function to check if a word is a homonym
def is_homonym(word):
    synsets = wordnet.synsets(word)

    filtered_synsets = []

    for synset in synsets:
        if word == synset.name().split(".")[0].lower():
            filtered_synsets.append(synset)

    return len(filtered_synsets) > 1


# Function to get definitions for a word
def get_word_definitions(word):
    # Check if the word is a homonym AND has multiple pronunciations
    if is_homonym(word) and has_multiple_pronunciations(word):
        # Use WordNet to get different synsets (meanings)
        synsets = wordnet.synsets(word)

        # Create a dictionary to store definitions
        word_defs = {}

        # Track used definitions to avoid duplicates
        used_defs = set()

        for synset in synsets:
            # Get the definition
            definition = synset.definition()

            # Avoid duplicate definitions
            if definition not in used_defs:
                # Add pronunciations to the definition
                word_defs[definition] = None
                used_defs.add(definition)

        return word_defs

    # If not a homonym or doesn't have multiple pronunciations, return an empty dictionary
    return {}


def create_comprehensive_word_definitions_json():
    # Use NLTK to get a comprehensive list of words
    words = set()


    # Combine with words from WordNet
    for synset in list(wordnet.all_synsets()):
        words.add(synset.name().split('.')[0])


    # Dictionary to store all word definitions
    word_definitions = {}

    # Process each word
    for word in words:
        # Get definitions for heteronyms
        definitions = get_word_definitions(word)

        # Only add to the dictionary if it has multiple definitions and pronunciations
        if definitions:
            word_definitions[word] = definitions

    return word_definitions


def main():
    # Create the word definitions dictionary
    word_definitions = create_comprehensive_word_definitions_json()

    # Write to a JSON file
    with open('../VoPho/phonemizers/english_heteronyms.json', 'w', encoding='utf-8') as f:
        json.dump(word_definitions, f, indent=4, ensure_ascii=False)

    # Print the number of words found
    print(f"Total number of heteronyms found: {len(word_definitions)}")

    # Print a few sample entries with their pronunciations
    print("\nSample Entries:")
    for word, defs in list(word_definitions.items())[:5]:
        print(f"\n{word}:")
        for definition, pronuns in defs.items():
            print(f"- Definition: {definition}")


if __name__ == "__main__":
    main()

# Note: Make sure to install required libraries
# pip install nltk pywsd