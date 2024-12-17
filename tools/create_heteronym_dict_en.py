import json
import nltk
from nltk.corpus import wordnet
from pywsd.lesk import simple_lesk

# Download necessary NLTK resources
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)


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
    # Check if the word is a homonym
    if is_homonym(word):
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
                word_defs[definition] = None
                used_defs.add(definition)

        return word_defs

    # If not a homonym, return an empty dictionary
    return {}


def create_comprehensive_word_definitions_json():
    # Use NLTK to get a comprehensive list of words
    words = set()

    # Add some common words known to have multiple meanings
    manual_words = [
        "lead", "tear", "read", "wind",
        "row", "live", "close", "bass"
    ]

    # Combine with words from WordNet
    for synset in list(wordnet.all_synsets()):
        words.add(synset.name().split('.')[0])

    # Add manual words to ensure they're included
    words.update(manual_words)

    # Dictionary to store all word definitions
    word_definitions = {}

    # Process each word
    for word in words:
        # Get definitions for homonyms
        definitions = get_word_definitions(word)

        # Only add to the dictionary if it has multiple definitions
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
    print(f"Total number of words with multiple meanings: {len(word_definitions)}")

    # Optionally, print a few sample entries
    print("\nSample Entries:")
    for word, defs in list(word_definitions.items())[:5]:
        print(f"\n{word}:")
        for definition in defs:
            print(f"- {definition}")


if __name__ == "__main__":
    main()

# Note: Make sure to install required libraries
# pip install nltk pywsd