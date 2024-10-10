import re
from openphonemizer import OpenPhonemizer

general = {
    # Basic contractions and common words
    "I'm": "aɪm",
    "you're": "jɔːr",
    "we're": "wɪər",
    "they're": "ðɛər",
    "isn't": "ɪznt",
    "aren't": "ɑːrnt",
    "can't": "kænt",
    "won't": "woʊnt",
    "don't": "doʊnt",
    "I'll": "aɪl",
    "you'll": "juːl",
    "we'll": "wiːl",
    "he'll": "hiːl",
    "she'll": "ʃiːl",
    "it'll": "ɪtl",
    "there's": "ðɛrz",
    "here's": "hɪrz",
    "that's": "ðæts",
    "what's": "wɒts",
    "where's": "wɛrz",
    "who's": "huːz",
    "let's": "lɛts",
    "didn't": "dɪdnt",
    "couldn't": "kʊdnt",
    "shouldn't": "ʃʊdnt",
    "wouldn't": "wʊdnt",
    "I've": "aɪv",
    "you've": "juːv",
    "we've": "wiːv",
    "they've": "ðeɪv",
    "y'all": "jɔːl",

    # Proper names or common mispronunciations
    "Google": "ɡuːɡl",
    "Linux": "lɪnʊks",
    "Tesla": "tɛslə",
    "Elon": "iːlɒn",
    "AI": "eɪ aɪ",
    "NASA": "næsə",
    "COVID": "koʊvɪd",
    "GIF": "dʒɪf",
    "JPEG": "dʒeɪpɛɡ",
    "Python": "paɪθɒn",

    # Contextual fixes: Words that change pronunciation based on context

    # Context-based past tense of "read"
    "I read": "aɪ rɛd",  # past tense
    "you read": "juː rɛd",  # past tense
    "he read": "hiː rɛd",  # past tense
    "she read": "ʃiː rɛd",  # past tense
    "we read": "wiː rɛd",  # past tense
    "they read": "ðeɪ rɛd",  # past tense

    # Present tense of "read"
    "I will read": "aɪ wɪl riːd",
    "you will read": "juː wɪl riːd",
    "he will read": "hiː wɪl riːd",
    "she will read": "ʃiː wɪl riːd",
    "we will read": "wiː wɪl riːd",
    "they will read": "ðeɪ wɪl riːd",
    "I can read": "aɪ kæn riːd",
    "you can read": "juː kæn riːd",
    "he can read": "hiː kæn riːd",
    "she can read": "ʃiː kæn riːd",
    "we can read": "wiː kæn riːd",
    "they can read": "ðeɪ kæn riːd",

    # Contextual forms of "live"
    "I live": "aɪ lɪv",  # verb (reside)
    "you live": "juː lɪv",  # verb (reside)
    "he lives": "hiː lɪvz",  # verb (reside)
    "she lives": "ʃiː lɪvz",  # verb (reside)
    "we live": "wiː lɪv",  # verb (reside)
    "they live": "ðeɪ lɪv",  # verb (reside)

    # "live" as in "broadcast"
    "a live broadcast": "ə laɪv brɔːdkæst",
    "live TV": "laɪv tiːviː",
    "live stream": "laɪv striːm",
    "is live": "ɪz laɪv",

    # Contextual forms of "wind"
    "the wind": "ðə wɪnd",  # noun
    "wind is": "wɪnd ɪz",  # noun
    "to wind": "tuː waɪnd",  # verb (e.g., wind a clock)

    # Contextual forms of "lead"
    "to lead": "tuː liːd",  # verb (guide)
    "lead pipe": "lɛd paɪp",  # noun (metal)

    # Contextual forms of "bass"
    "bass guitar": "beɪs ɡɪˈtɑː",  # instrument
    "sea bass": "siː bæs",  # fish

    # Contextual fixes for "graduate"
    "graduate": "ˈɡrædʒuət",  # noun (a person who has graduated)
    "I graduated": "aɪ ˈɡrædʒueɪtɪd",  # past tense
    "you graduated": "juː ˈɡrædʒueɪtɪd",  # past tense
    "he graduated": "hiː ˈɡrædʒueɪtɪd",  # past tense
    "she graduated": "ʃiː ˈɡrædʒueɪtɪd",  # past tense
    "we graduated": "wiː ˈɡrædʒueɪtɪd",  # past tense
    "they graduated": "ðeɪ ˈɡrædʒueɪtɪd",  # past tense
    "graduate program": "ˈɡrædʒuət ˈprəʊɡræm",  # academic program
    "graduate school": "ˈɡrædʒuət skuːl",  # advanced education after undergraduate
    "graduate student": "ˈɡrædʒuət ˈstjuːdənt",  # a student in a graduate program
    "he is a graduate": "hiː ɪz ə ˈɡrædʒuət",  # stating someone has graduated
    "she is graduating": "ʃiː ɪz ˈɡrædʒueɪtɪŋ",  # present tense (the act of graduating)

    # Additional context-based fixes for "graduATE"
    "i will graduate": "aɪ wɪl ˈɡrædʒueɪt",  # future tense
    "he will graduate": "hiː wɪl ˈɡrædʒueɪt",  # future tense
    "children graduate": "ˈtʃɪldren ˈɡrædʒueɪt",  # present tense
    "they will graduate": "ðeɪ wɪl ˈɡrædʒueɪt",  # future tense
    "students graduate": "ˈstjuːdənts ˈɡrædʒueɪt",  # present tense
    "the class will graduate": "ðə klæs wɪl ˈɡrædʒueɪt",  # future tense
    "we will graduate": "wiː wɪl ˈɡrædʒueɪt",  # future tense
    "the graduates will celebrate": "ðə ˈɡrædʒuəts wɪl ˈsɛlɪˌbreɪt",  # referring to graduates celebrating

    # Contextual forms of "tear"
    "tear up": "tɛər ʌp",  # verb (to rip)
    "he tears up": "hiː tɛərz ʌp",  # verb (to rip)
    "she tears up": "ʃiː tɛərz ʌp",  # verb (to rip)
    "they tear up": "ðeɪ tɛər ʌp",  # verb (to rip)
    "you tear up": "juː tɛər ʌp",  # verb (to rip)
    "we tear up": "wiː tɛər ʌp",  # verb (to rip)
    "I tear up": "aɪ tɛər ʌp",  # verb (to rip)

    "a tear": "ə tɛr",  # noun (crying)
    "he has a tear": "hiː hæz ə tɛr",  # noun (cry)
    "she has a tear": "ʃiː hæz ə tɛr",  # noun (cry)
    "they have a tear": "ðeɪ hæv ə tɛr",  # noun (cry)
    "you have a tear": "juː hæv ə tɛr",  # noun (cry)
    "we have a tear": "wiː hæv ə tɛr",  # noun (cry)
    "I have a tear": "aɪ hæv ə tɛr",  # noun (cry)

    "he has tears": "hiː hæz tɪrz",  # noun (cry)
    "she has tears": "ʃiː hæz tɪrz",  # noun (cry)
    "they have tears": "ðeɪ hæv tɪrz",  # noun (cry)
    "you have tears": "juː hæv tɪrz",  # noun (cry)
    "we have tears": "wiː hæv tɪrz",  # noun (cry)
    "I have tears": "aɪ hæv tɪrz",  # noun (cry)

    "he shed a tear": "hiː ʃɛd ə tɪr",  # noun (cry)
    "she shed a tear": "ʃiː ʃɛd ə tɪr",  # noun (cry)
    "they shed a tear": "ðeɪ ʃɛd ə tɪr",  # noun (cry)
    "you shed a tear": "juː ʃɛd ə tɪr",  # noun (cry)
    "we shed a tear": "wiː ʃɛd ə tɪr",  # noun (cry)
    "I shed a tear": "aɪ ʃɛd ə tɪr",  # noun (cry)

    "he's in tears": "hiː z ɪn tɪrz",  # noun (cry)
    "she's in tears": "ʃiː z ɪn tɪrz",  # noun (cry)
    "they're in tears": "ðeɪər ɪn tɪrz",  # noun (cry)
    "you're in tears": "jʊər ɪn tɪrz",  # noun (cry)
    "we're in tears": "wɪər ɪn tɪrz",  # noun (cry)
    "i'm in tears": "aɪm ɪn tɪrz",  # noun (cry)

    # Contextual forms of "record"
    "to record": "tuː rɪˈkɔːrd",  # verb (to capture sound)
    "a record": "ə ˈrɛkərd",
    "my record": "maɪ ˈrɛkərd",
    "your record": "jʊər ˈrɛkərd",
    "his record": "hɪz ˈrɛkərd",
    "her record": "hɜːr ˈrɛkərd",
    "our record": "aʊər ˈrɛkərd",
    "their record": "ðeər ˈrɛkərd",

    # Contextual fixes for "record" as a verb (to document)
    "I record": "aɪ rɪˈkɔːrd",
    "you record": "juː rɪˈkɔːrd",
    "he records": "hiː rɪˈkɔːrdz",
    "she records": "ʃiː rɪˈkɔːrdz",
    "we record": "wiː rɪˈkɔːrd",
    "they record": "ðeɪ rɪˈkɔːrd",
    "will record": "wɪl rɪˈkɔːrd",

    # Additional contexts for "record"
    "this record": "ðɪs ˈrɛkərd",
    "that record": "ðæt ˈrɛkərd",
    "the record": "ðə ˈrɛkərd",

    # Contextual fixes for "I have a record"
    "I have a record": "aɪ hæv ə ˈrɛkərd",
    "you have a record": "juː hæv ə ˈrɛkərd",
    "he has a record": "hiː hæz ə ˈrɛkərd",
    "she has a record": "ʃiː hæz ə ˈrɛkərd",
    "we have a record": "wiː hæv ə ˈrɛkərd",
    "they have a record": "ðeɪ hæv ə ˈrɛkərd",

    # Contextual fixes for "keeping a record"
    "I keep a record": "aɪ kiːp ə ˈrɛkərd",
    "you keep a record": "juː kiːp ə ˈrɛkərd",
    "he keeps a record": "hiː kiːps ə ˈrɛkərd",
    "she keeps a record": "ʃiː kiːps ə ˈrɛkərd",
    "we keep a record": "wiː kiːp ə ˈrɛkərd",
    "they keep a record": "ðeɪ kiːp ə ˈrɛkərd",

    # Contextual fixes for "break a record"
    "I break a record": "aɪ breɪk ə ˈrɛkərd",
    "you break a record": "juː breɪk ə ˈrɛkərd",
    "he breaks a record": "hiː breɪks ə ˈrɛkərd",
    "she breaks a record": "ʃiː breɪks ə ˈrɛkərd",
    "we break a record": "wiː breɪk ə ˈrɛkərd",
    "they break a record": "ðeɪ breɪk ə ˈrɛkərd",
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

# Combine both dictionaries
manual_phonemizations = {**general, **proper_names, **common_mispronunciations}


class Phonemizer:
    def __init__(self, manual_fixes=None):
        if manual_fixes is None:
            manual_fixes = manual_phonemizations
        self.phonemizer = OpenPhonemizer()

        # Dictionary of manual phonemizations
        self.manual_phonemizations = manual_fixes

        # Post-processing filters
        self.manual_filters = {
            " . . . ": "... ",
            " . ": ". "
        }

        # Regex to detect text wrapped in <phoneme> tags
        self.phoneme_tag_pattern = re.compile(r"<phoneme>(.*?)</phoneme>")

    def preprocess(self, text):
        # Replace words in the text with their manual phonemizations wrapped in <phoneme> tags
        for word, ipa in self.manual_phonemizations.items():
            text = re.sub(rf"\b{word}\b", f"<phoneme>{ipa}</phoneme>", text, flags=re.IGNORECASE)
        return text

    def postprocess(self, text):
        # Remove the <phoneme> tags but retain the IPA within them, preserving spaces
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
    test_text = "I'm excited because I graduated from a graduate program, and now I can read a record of my achievements. I also tear up when I think about how my friends will graduate too, and they have tears of joy."
    print(f"Original: {test_text}")
    print(f"Phonemized: {phonem.phonemize(test_text)}")
