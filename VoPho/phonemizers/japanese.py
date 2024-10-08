import cutlet
import re

# MARK: legacy
def convert_numbers_in_string(input_string):
    # Regular expression to find numbers in the string
    number_pattern = re.compile(r'\d+')
    # Function to replace numbers with their Japanese pronunciation
    def replace_with_japanese(match):
        num = int(match.group())
        if num == 0:
            return 'ゼロ'
        if num > 9999:
            # MARK: TODO: DEBUG: uncomment this assert in production!!!
            # assert num < 10000, num
            # print('DEBUG: assert fails on 5+ digits')
            return 'Invalid input'
        digits = ['', 'いち', 'に', 'さん', 'よん', 'ご', 'ろく', 'なな', 'はち', 'きゅう']
        tens = ['', 'じゅう', 'にじゅう', 'さんじゅう', 'よんじゅう', 'ごじゅう', 'ろくじゅう', 'ななじゅう', 'はちじゅう', 'きゅうじゅう']
        hundreds = ['', 'ひゃく', 'にひゃく', 'さんびゃく', 'よんひゃく', 'ごひゃく', 'ろっぴゃく', 'ななひゃく', 'はっぴゃく', 'きゅうひゃく']
        thousands = ['', 'せん', 'にせん', 'さんぜん', 'よんせん', 'ごせん', 'ろくせん', 'ななせん', 'はっせん', 'きゅうせん']
        result = ''
        if num >= 1000:
            result += thousands[num // 1000]
            num %= 1000
        if num >= 100:
            result += hundreds[num // 100]
            num %= 100
        if num >= 10:
            result += tens[num // 10]
            num %= 10
        if num > 0:
            result += digits[num]
        return result
    # Replace all occurrences of numbers in the string
    converted_string = number_pattern.sub(replace_with_japanese, input_string)
    return converted_string

# MARK: legacy
def replace_tashdid_2(s):
    vowels = 'aiueoɯ0123456789.?!_。؟？！．．．＠@＃#＄$％%＾^＆&＊*（)(）_+=[「」]></\\`~～―ー∺"'
    vowels = vowels.replace('u', '') # TODO: impossible for 'u' to occur, it was replaced by roma_mapper
    result = []
    i = 0
    while i < len(s):
        if i < len(s) - 2 and s[i].lower() == s[i + 2].lower() and s[i].lower() not in vowels and s[i + 1] == ' ':
            result.append('ʔ')
            result.append(s[i + 2])
            i += 3
        elif i < len(s) - 1 and s[i].lower() == s[i + 1].lower() and s[i].lower() not in vowels:
            result.append('ʔ')
            result.append(s[i + 1])
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

def replace_tashdid(input_string):
    result = []
    i = 0
    while i < len(input_string):
        if i + 1 < len(input_string) and input_string[i] == input_string[i + 1] and input_string[i] not in 'aiueo':
            result.append('ʔ')
            result.append(input_string[i])
            i += 2  # Skip the next character as it is already processed
        else:
            result.append(input_string[i])
            i += 1
    return ''.join(result)


def hira2ipa(text, roma_mapper=roma_mapper):
    keys_set = set(roma_mapper.keys())
    special_rule = ("n", "ɴ")

    transformed_text = []
    i = 0

    while i < len(text):
        if text[i] == special_rule[0]:
            if i + 1 == len(text) or text[i + 1] not in keys_set:
                transformed_text.append(special_rule[1])
            else:
                transformed_text.append(text[i])
        else:
            transformed_text.append(text[i])

        i += 1

    return ''.join(transformed_text)


def process_japanese_text(ml):
    # Check for small characters and replace them
    if any(char in ml for char in "ぁぃぅぇぉ"):
        ml = ml.replace("ぁ", "あ")
        ml = ml.replace("ぃ", "い")
        ml = ml.replace("ぅ", "う")
        ml = ml.replace("ぇ", "え")
        ml = ml.replace("ぉ", "お")

    # Initialize Cutlet for romaji conversion

    # Convert to romaji and apply transformations
    # output = katsu.romaji(ml, capitalize=False).lower()

    output = katsu.romaji(apply_transformations(alphabetreading(ml)), capitalize=False).lower()

    # Replace specific romaji sequences
    if 'j' in output:
        output = output.replace('j', "dʑ")
    if 'tt' in output:
        output = output.replace('tt', "ʔt")
    if 't t' in output:
        output = output.replace('t t', "ʔt")
    if ' ʔt' in output:
        output = output.replace(' ʔt', "ʔt")
    if 'ssh' in output:
        output = output.replace('ssh', "ɕɕ")

    # Convert romaji to IPA
    output = Roma2IPA(convert_numbers_in_string(output))

    output = hira2ipa(output)

    # Apply additional transformations
    output = replace_chars_2(output)
    output = replace_repeated_chars(replace_tashdid_2(output))
    output = nasal_mapper(output)

    # Final adjustments
    if " ɴ" in output:
        output = output.replace(" ɴ", "ɴ")

    if ' neɽitai ' in output:
        output = output.replace(' neɽitai ', "naɽitai")

    if 'harɯdʑisama' in output:
        output = output.replace('harɯdʑisama', "arɯdʑisama")

    if "ki ni ɕinai" in output:
        output = re.sub(r'(?<!\s)ki ni ɕinai', r' ki ni ɕinai', output)

    if 'ʔt' in output:
        output = re.sub(r'(?<!\s)ʔt', r'ʔt', output)

    if 'de aɽoɯ' in output:
        output = re.sub(r'(?<!\s)de aɽoɯ', r' de aɽoɯ', output)

    return output.lstrip()

def replace_repeating_a(output):
    # Define patterns and their replacements
    patterns = [
        (r'(aː)\s*\1+\s*', r'\1~'),  # Replace repeating "aː" with "aː~~"
        (r'(aːa)\s*aː', r'\1~'),  # Replace "aːa aː" with "aː~~"
        (r'aːa', r'aː~'),  # Replace "aːa" with "aː~"
        (r'naː\s*aː', r'naː~'),  # Replace "naː aː" with "naː~"
        (r'(oː)\s*\1+\s*', r'\1~'),  # Replace repeating "oː" with "oː~~"
        (r'(oːo)\s*oː', r'\1~'),  # Replace "oːo oː" with "oː~~"
        (r'oːo', r'oː~'),  # Replace "oːo" with "oː~"
        (r'(eː)\s*\1+\s*', r'\1~'),
        (r'(e)\s*\1+\s*', r'\1~'),
        (r'(eːe)\s*eː', r'\1~'),
        (r'eːe', r'eː~'),
        (r'neː\s*eː', r'neː~'),
    ]
    # Apply each pattern to the output
    for pattern, replacement in patterns:
        output = re.sub(pattern, replacement, output)
    return output

pre = [
('っ', 'ʔ'),
('ぁ', 'あ'),
('ぃ', 'い'),
('ぅ', 'う'),
('ぇ', 'え'),
('ぉ', 'お'),
('A', 'エイ'),
('B', 'ビー'),
('C', 'シー'),
('D', 'ディー'),
('E', 'イー'),
('F', 'エフ'),
('G', 'ジー'),
('H', 'エイチ'),
('I', 'アイ'),
('J', 'ジェイ'),
('K', 'ケイ'),
('L', 'エル'),
('M', 'エム'),
('N', 'エヌ'),
('O', 'オー'),
('P', 'ピー'),
('Q', 'キュー'),
('R', 'アール'),
('S', 'エス'),
('T', 'ティー'),
('U', 'ユー'),
('V', 'ヴィー'),
('W', 'ダブリュー'),
('X', 'エックス'),
('Y', 'ワイ'),
('Z', 'ゼッド'),
('ワタクシ', 'わたし'),
('チカコ', 'しゅうこ'),
('タノヒト', 'ほかのひと'),
('たのひと', 'ほかのひと'),
('すうは', 'かずは'),
('%', '％'),
('@', 'あっとさいん'),
('$', 'どる'),
('#', 'はっしゅたぐ'),
('＄', 'どる'),
('＃', 'はっしゅたぐ'),
('何が', 'なにが'),
('何も', 'なにも'),
('何か', 'なにか'),
('何は', 'なにが'),
('お父様', 'おとうさま'),
('お兄様', 'おにいさま'),
('何を', 'なにを'),
('良い', 'いい'),
('李衣菜', 'りいな'),
('志希', 'しき'),
('種', 'たね'),
('方々', 'かたがた'),
('颯', 'はやて'),
('茄子さん', 'かこさん'),
('茄子ちゃん', 'かこちゃん'),
('涼ちゃん', 'りょうちゃん'),
('涼さん', 'りょうさん'),
('紗枝', 'さえ'),
('文香', 'ふみか'),
('私', 'わたし'),
('周子', 'しゅうこ'),
('イェ', 'いえ'),
('可憐', 'かれん'),
('加蓮', 'かれん'),
('･', '.'),
('方の', 'かたの'),
('気に', 'きに'),
('唯さん', 'ゆいさん'),
('唯ちゃん', 'ゆいちゃん'),
('聖ちゃん', 'ひじりちゃん'),
('他の', 'ほかの'),
('他に', 'ほかに'),
('一生懸命', 'いっしょうけんめい'),
('楓さん', 'かえでさん'),
('楓ちゃん', 'かえでちゃん'),
('内から', 'ないから'),
('の下で', 'のしたで'),
('仕方', 'しかた'),
('明日', 'あした'),
('従妹', 'いとこ'),
('1人', 'ひとり'),
('2人', 'ふたり'), # TODO: order matters, this right-side value occurs 6 lines down
('一期', 'いちご'),
('一会', 'いちえ'),
('♪', '！'),
('?', '？'),
('どんな方', 'どんなかた'),
('ふたり暮らし', 'ふたりぐらし'),
('新年', 'しんねん'),
('来年', 'らいねん'),
('去年', 'きょねん'),
('壮年', 'そうねん'),
('今年', 'ことし'),
('昨年', 'さくねん'),
('本年', 'ほんねん'),
('平年', 'へいねん'),
('閏年', 'うるうどし'),
('初年', 'しょねん'),
('少年', 'しょうねん'),
('多年', 'たねん'),
('青年', 'せいねん'),
('中年', 'ちゅうねん'),
('老年', 'ろうねん'),
('成年', 'せいねん'),
('幼年', 'ようねん'),
('前年', 'ぜんねん'),
('元年', 'がんねん'),
('経年', 'けいねん'),
('当年', 'とうねん'),
('明年', 'みょうねん'),
('歳年', 'さいねん'),
('数年', 'すうねん'),
('半年', 'はんとし'),
('後年', 'こうねん'),
('実年', 'じつねん'),
('年年', 'ねんねん'),
('連年', 'れんねん'),
('暦年', 'れきねん'),
('各年', 'かくねん'),
('全年', 'ぜんねん'),
('年を', 'としを'),
('年が', 'としが'),
('年も', 'としも'),
('年は', 'としは'),
('奏ちゃん', 'かなでちゃん'),
('負けず嫌い', 'まけずぎらい'),
('貴方', 'あなた'),
('貴女', 'あなた'),
('貴男', 'あなた'),
('その節', 'そのせつ'),
('何し', 'なにし'),
('何する', 'なにする'),
('心さん', 'しんさん'),
('心ちゃん', 'しんちゃん'),
('乃々', 'のの'),
('身体の', 'からだの'),
('身体が', 'からだが'),
('身体を', 'からだを'),
('身体は', 'からだは'),
('身体に', 'からだに'),
('正念場', 'しょうねんば'),
('言う', 'いう'),
('一回', 'いっかい'),
('一曲', 'いっきょく'),
('一日', 'いちにち'),
('一言', 'ひとこと'),
('一杯', 'いっぱい'),
('方が', 'ほうが'),
('縦輪城', 'じゅうりんしろ'),
('深息', 'しんそく'),
('家人', 'かじん'),
('お返し', 'おかえし'),
('化物語', 'ばけものがたり'),
('阿良々木暦', 'あららぎこよみ'),
('何より', 'なにより'),
]
assert len(pre) == 158, len(pre)
assert len(pre) == len({a for a, _ in pre}) # DEBUG: assert unique keys

roma_mapper = [
('my', 'mʲ'),
('by', 'bʲ'),
('ny', 'nʲ'),
('ry', 'rʲ'),
('si', 'sʲ'),
('ky', 'kʲ'),
('gy', 'gʲ'),
('dy', 'dʲ'),
('di', 'dʲ'),
('fi', 'fʲ'),
('fy', 'fʲ'),
('ch', 'tɕ'),
('sh', 'ɕ'),
('hi', 'çi'),
('u', 'ɯ'),
# ('fu', 'ɸɯ'),
('ra', 'ɽa'),
('ri', 'ɽi'),
# ('ru', 'ɽɯ'),
('re', 'ɽe'),
('ro', 'ɽo'),
('ji', 'dʑi'),
('ya', 'ja'),
# ('yu', 'jɯ'),
('yo', 'jo'),
('wo', 'o'),
]
assert len(roma_mapper) == 23, len(roma_mapper)
assert len(roma_mapper) == len({a for a, _ in roma_mapper}) # DEBUG: assert unique keys

nasal_sounds = [
# before m, p, b
('ɴm', 'mm'),
('ɴb', 'mb'),
('ɴp', 'mp'),
# before k, g
('ɴk', 'ŋk'),
('ɴg', 'ŋg'),
# before t, d, n, s, z, ɽ
('ɴt', 'nt'),
('ɴd', 'nd'),
('ɴn', 'nn'),
('ɴs', 'ns'),
('ɴz', 'nz'),
('ɴɽ', 'nɽ'),
('ɴɲ', 'ɲɲ'),
]
assert len(nasal_sounds) == 12, len(nasal_sounds)
assert len(nasal_sounds) == len({a for a, _ in nasal_sounds}) # DEBUG: assert unique keys

k_mapper = [
('ゔぁ', 'ba'),
('ゔぃ', 'bi'),
('ゔぇ', 'be'),
('ゔぉ', 'bo'),
('ゔゃ', 'bʲa'),
('ゔゅ', 'bʲɯ'),
('ゔょ', 'bʲo'),
('ゔ', 'bɯ'),
('あぁ', ' aː'),
('いぃ', ' iː'),
('いぇ', ' je'),
('いゃ', ' ja'),
('うぅ', ' ɯː'),
('えぇ', ' eː'),
('おぉ', ' oː'),
('かぁ', ' kaː'),
('きぃ', ' kiː'),
('くぅ', 'kɯː'),
('くゃ', 'ka'),
('くゅ', 'kʲɯ'),
('くょ', 'kʲo'),
('けぇ', 'keː'),
('こぉ', 'koː'),
('がぁ', 'gaː'),
('ぎぃ', 'giː'),
('ぐぅ', 'gɯː'),
('ぐゃ', 'gʲa'),
('ぐゅ', 'gʲɯ'),
('ぐょ', 'gʲo'),
('げぇ', 'geː'),
('ごぉ', 'goː'),
('さぁ', 'saː'),
('しぃ', 'ɕiː'),
('すぅ', 'sɯː'),
('すゃ', 'sʲa'),
('すゅ', 'sʲɯ'),
('すょ', 'sʲo'),
('せぇ', 'seː'),
('そぉ', 'soː'),
('ざぁ', 'zaː'),
('じぃ', 'dʑiː'),
# ('ずぅ', 'zɯː'), # TODO: overridden by conflict 96 lines down
('ずゃ', 'zʲa'),
('ずゅ', 'zʲɯ'),
('ずょ', 'zʲo'),
('ぜぇ', 'zeː'),
('ぞぉ', 'zeː'),
('たぁ', 'taː'),
('ちぃ', 'tɕiː'),
('つぁ', 'tsa'),
('つぃ', 'tsi'),
('つぅ', 'tsɯː'),
('つゃ', 'tɕa'),
('つゅ', 'tɕɯ'),
('つょ', 'tɕo'),
('つぇ', 'tse'),
('つぉ', 'tso'),
('てぇ', 'teː'),
('とぉ', 'toː'),
('だぁ', 'daː'),
('ぢぃ', 'dʑiː'),
('づぅ', 'dɯː'),
('づゃ', 'zʲa'),
('づゅ', 'zʲɯ'),
('づょ', 'zʲo'),
('でぇ', 'deː'),
('どぉ', 'doː'),
('なぁ', 'naː'),
('にぃ', 'niː'),
('ぬぅ', 'nɯː'),
('ぬゃ', 'nʲa'),
('ぬゅ', 'nʲɯ'),
('ぬょ', 'nʲo'),
('ねぇ', 'neː'),
('のぉ', 'noː'),
('はぁ', 'haː'),
('ひぃ', 'çiː'),
# ('ふぅ', 'ɸɯː'), # TODO: overridden by conflict 126 lines down
('ふゃ', 'ɸʲa'),
('ふゅ', 'ɸʲɯ'),
('ふょ', 'ɸʲo'),
('へぇ', 'heː'),
('ほぉ', 'hoː'),
('ばぁ', 'baː'),
('びぃ', 'biː'),
('ぶぅ', 'bɯː'),
('ぶゅ', 'bʲɯ'),
('べぇ', 'beː'),
('ぼぉ', 'boː'),
('ぱぁ', 'paː'),
('ぴぃ', 'piː'),
('ぷぅ', 'pɯː'),
('ぷゃ', 'pʲa'),
('ぷゅ', 'pʲɯ'),
('ぷょ', 'pʲo'),
('ぺぇ', 'peː'),
('ぽぉ', 'poː'),
('まぁ', 'maː'),
('みぃ', 'miː'),
('むぅ', 'mɯː'),
('むゃ', 'mʲa'),
('むゅ', 'mʲɯ'),
('むょ', 'mʲo'),
('めぇ', 'meː'),
('もぉ', 'moː'),
('やぁ', 'jaː'),
('ゆぅ', 'jɯː'),
('ゆゃ', 'jaː'),
('ゆゅ', 'jɯː'),
('ゆょ', 'joː'),
('よぉ', 'joː'),
('らぁ', 'ɽaː'),
('りぃ', 'ɽiː'),
('るぅ', 'ɽɯː'),
('るゃ', 'ɽʲa'),
('るゅ', 'ɽʲɯ'),
('るょ', 'ɽʲo'),
('れぇ', 'ɽeː'),
('ろぉ', 'ɽoː'),
('わぁ', 'ɯaː'),
('をぉ', 'oː'),
('う゛', 'bɯ'),
('でぃ', 'di'),
('でゃ', 'dʲa'),
('でゅ', 'dʲɯ'),
('でょ', 'dʲo'),
('てぃ', 'ti'),
('てゃ', 'tʲa'),
('てゅ', 'tʲɯ'),
('てょ', 'tʲo'),
('すぃ', 'si'),
('ずぁ', 'zɯa'),
('ずぃ', 'zi'),
('ずぅ', 'zɯ'), # TODO: overrides conflict 96 lines up
('ずぇ', 'ze'),
('ずぉ', 'zo'),
('きゃ', 'kʲa'),
('きゅ', 'kʲɯ'),
('きょ', 'kʲo'),
('しゃ', 'ɕʲa'),
('しゅ', 'ɕʲɯ'),
('しぇ', 'ɕʲe'),
('しょ', 'ɕʲo'),
('ちゃ', 'tɕa'),
('ちゅ', 'tɕɯ'),
('ちぇ', 'tɕe'),
('ちょ', 'tɕo'),
('とぅ', 'tɯ'),
('とゃ', 'tʲa'),
('とゅ', 'tʲɯ'),
('とょ', 'tʲo'),
('どぁ', 'doa'),
('どぅ', 'dɯ'),
('どゃ', 'dʲa'),
('どゅ', 'dʲɯ'),
('どょ', 'dʲo'),
('にゃ', 'nʲa'),
('にゅ', 'nʲɯ'),
('にょ', 'nʲo'),
('ひゃ', 'çʲa'),
('ひゅ', 'çʲɯ'),
('ひょ', 'çʲo'),
('みゃ', 'mʲa'),
('みゅ', 'mʲɯ'),
('みょ', 'mʲo'),
('りゃ', 'ɽʲa'),
('りぇ', 'ɽʲe'),
('りゅ', 'ɽʲɯ'),
('りょ', 'ɽʲo'),
('ぎゃ', 'gʲa'),
('ぎゅ', 'gʲɯ'),
('ぎょ', 'gʲo'),
('ぢぇ', 'dʑe'),
('ぢゃ', 'dʑa'),
('ぢゅ', 'dʑɯ'),
('ぢょ', 'dʑo'),
('じぇ', 'dʑe'),
('じゃ', 'dʑa'),
('じゅ', 'dʑɯ'),
('じょ', 'dʑo'),
('びゃ', 'bʲa'),
('びゅ', 'bʲɯ'),
('びょ', 'bʲo'),
('ぴゃ', 'pʲa'),
('ぴゅ', 'pʲɯ'),
('ぴょ', 'pʲo'),
('うぁ', 'ɯa'),
('うぃ', 'ɯi'),
('うぇ', 'ɯe'),
('うぉ', 'ɯo'),
('うゃ', 'ɯʲa'),
('うゅ', 'ɯʲɯ'),
('うょ', 'ɯʲo'),
('ふぁ', 'ɸa'),
('ふぃ', 'ɸi'),
('ふぅ', 'ɸɯ'), # TODO: overrides conflict 206 lines up
('ふぇ', 'ɸe'),
('ふぉ', 'ɸo'),
('あ', ' a'),
('い', ' i'),
('う', 'ɯ'),
('え', ' e'),
('お', ' o'),
('か', ' ka'),
('き', ' ki'),
('く', ' kɯ'),
('け', ' ke'),
('こ', ' ko'),
('さ', ' sa'),
('し', ' ɕi'),
('す', ' sɯ'),
('せ', ' se'),
('そ', ' so'),
('た', ' ta'),
('ち', ' tɕi'),
('つ', ' tsɯ'),
('て', ' te'),
('と', ' to'),
('な', ' na'),
('に', ' ni'),
('ぬ', ' nɯ'),
('ね', ' ne'),
('の', ' no'),
('は', ' ha'),
('ひ', ' çi'),
('ふ', ' ɸɯ'),
('へ', ' he'),
('ほ', ' ho'),
('ま', ' ma'),
('み', ' mi'),
('む', ' mɯ'),
('め', ' me'),
('も', ' mo'),
('ら', ' ɽa'),
('り', ' ɽi'),
('る', ' ɽɯ'),
('れ', ' ɽe'),
('ろ', ' ɽo'),
('が', ' ga'),
('ぎ', ' gi'),
('ぐ', ' gɯ'),
('げ', ' ge'),
('ご', ' go'),
('ざ', ' za'),
('じ', ' dʑi'),
('ず', ' zɯ'),
('ぜ', ' ze'),
('ぞ', ' zo'),
('だ', ' da'),
('ぢ', ' dʑi'),
('づ', ' zɯ'),
('で', ' de'),
('ど', ' do'),
('ば', ' ba'),
('び', ' bi'),
('ぶ', ' bɯ'),
('べ', ' be'),
('ぼ', ' bo'),
('ぱ', ' pa'),
('ぴ', ' pi'),
('ぷ', ' pɯ'),
('ぺ', ' pe'),
('ぽ', ' po'),
('や', ' ja'),
('ゆ', ' jɯ'),
('よ', ' jo'),
('わ', ' wa'),
('ゐ', ' i'),
('ゑ', ' e'),
('ん', 'ɴ'), # TODO: was originally ('ん', ' ɴ'), but this way we can avoid an extra replace(' ɴ', 'ɴ') call
# ('っ', ' ʔ'), # TODO: overriden by conflict 9 lines down
('ー', ' ː'),
('ぁ', ' a'),
('ぃ', ' i'),
('ぅ', ' ɯ'),
('ぇ', ' e'),
('ぉ', ' o'),
('ゎ', ' ɯa'),
('っ', '?'), # TODO: overrides conflict 9 lines up
('を', 'o'),
]
assert len(k_mapper) == 277, len(k_mapper)
assert len(k_mapper) == len({a for a, _ in k_mapper}) # DEBUG: assert unique keys

spaces = [
('ɯ ɴ', 'ɯɴ'),
('na ɴ ', 'naɴ '),
(' mina ', ' miɴna '),
('ko ɴ ni tɕi ha', 'konnitɕiwa'),
('ha i', 'hai'),
('boɯtɕama', 'boʔtɕama'),
('i eːi', 'ieːi'),
('taiɕɯtsɯdʑoɯ', 'taiɕitsɯdʑoɯ'),
('soɴna ka ze ni', 'soɴna fɯɯ ni'),
(' i e ', 'ke '),
('�', ''),
('×', ' batsɯ '),
('se ka ɯndo', 'sekaɯndo'),
('i i', 'iː'),
('i tɕi', 'itɕi'),
('ka i', 'kai'),
('naɴ ga', 'nani ga'),
('i eː i', 'ieːi'),
('naɴ koɽe', 'nani koɽe'),
('naɴ soɽe', 'nani soɽe'),
(' ɕeɴ ', ' seɴ '),
('en ', 'eɴ '),
('in ', 'iɴ '),
('an ', 'aɴ '),
('on ', 'oɴ '),
('ɯn ', 'ɯɴ '),
('koɴd o', 'kondo'),
('ko ɴ d o', 'kondo'),
('ko ɴ do', 'kondo'),
('oanitɕaɴ', 'oniːtɕaɴ'),
('oanisaɴ', 'oniːsaɴ'),
('oanisama', 'oniːsama'),
('hoːmɯrɯɴɯ', 'hoːmɯrɯːmɯ'),
('so ɴ na ', 'sonna'),
('  sonna  ', ' sonna '),
('  konna  ', ' konna '),
('ko ɴ na ', 'konna'),
(' ko to  ', ' koto '),
('edʑdʑi', 'eʔtɕi'),
(' edʑdʑ ', ' eʔtɕi '),
(' dʑdʑ ', ' dʑiːdʑiː '),
('secɯnd', 'sekaɯndo'),
('ɴɯ', 'nɯ'),
('ɴe', 'ne'),
('ɴo', 'no'),
('ɴa', 'na'),
('ɴi', 'ni'),
('ɴʲ', 'nʲ'),
('hotond o', 'hotondo'),
('hakoɴd e', 'hakoɴde'),
('gakɯtɕi ɽi', 'gaʔtɕiɽi '),
(' ʔ', 'ʔ'),
('ʔ ', 'ʔ'),
('-', 'ː'),
('- ', 'ː'),
('--', '~ː'),
('~', '—'),
('、', ','),
(' ː', 'ː'),
('ka nade', 'kanade'),
('ohahasaɴ', 'okaːsaɴ'),
('　', ' '),
('viː', 'bɯiː'),
('ːː', 'ː—'),
('d ʑ', 'dʑ'),
('d a', 'da'),
('d e', 'de'),
('d o', 'do'),
('d ɯ', 'dɯ'),
('niːɕiki', 'ni iɕiki'),
('anitɕaɴ', 'niːtɕaɴ'),
('daiːtɕi', 'dai itɕi'),
('naɴ sono', 'nani sono'),
('naɴ kono', 'nani kono'),
('naɴ ano', 'nani ano'),  # Cutlet please fix your shit
(' niːtaɽa', ' ni itaɽa'),
('doɽamaɕiːd', 'doɽama ɕiːdʲi'),
('aɴ ta', 'anta'),
('aɴta', 'anta'),
('naniːʔteɴ', 'nani iʔteɴ'),
('niːkite', 'ni ikite'),
]
assert len(spaces) == 81, len(spaces)
assert len(spaces) == len({a for a, _ in spaces}) # DEBUG: assert unique keys

symbols = [
# with space
('$ ', 'dorɯ'),
('＄ ', 'dorɯ'),
('〇 ', 'marɯ'),
('¥ ', 'eɴ'),
('# ', 'haʔɕɯ tagɯ'),
('＃ ', 'haʔɕɯ tagɯ'),
('& ', 'ando'),
('＆ ', 'ando'),
('% ', 'paːsento'),
('％ ', 'paːsento'),
('@ ', 'aʔto saiɴ'),
('＠ ', 'aʔto saiɴ'),
# no space
('$', 'dorɯ'),
('＄', 'dorɯ'),
('〇', 'marɯ'),
('¥', 'eɴ'),
('#', 'haʔɕɯ tagɯ'),
('＃', 'haʔɕɯ tagɯ'),
('&', 'ando'),
('＆', 'ando'),
('%', 'paːsento'),
('％', 'paːsento'),
('@', 'aʔto saiɴ'),
('＠', 'aʔto saiɴ'),
('～', '—'),
('kʲɯɯdʑɯɯkʲɯɯ.kʲɯɯdʑɯɯ', 'kʲɯɯdʑɯɯ kʲɯɯ teɴ kʲɯɯdʑɯɯ'),
]
assert len(symbols) == 26, len(symbols)
assert len(symbols) == len({a for a, _ in symbols}) # DEBUG: assert unique keys

class Phonemizer:
    def __init__(self):
        self.katsu = cutlet.Cutlet(ensure_ascii=False)
        self.katsu.use_foreign_spelling = False

    def _process_japanese_text(self, text):
        text = text.upper()
        for a, b in pre: # alphabetreading, apply_transformations
            text = text.replace(a, b)
        text = self.katsu.romaji(text, capitalize=False).lower()
        for a, b in [('j', 'dʑ'), ('tt', 'ʔt'), ('t t', 'ʔt'), (' ʔt', 'ʔt'), ('ssh', 'ɕɕ')]:
            text = text.replace(a, b)
        text = convert_numbers_in_string(text)
        for a, b in roma_mapper: # Roma2IPA
            text = text.replace(a, b)
        text = re.sub(r'n(?![aeio])', 'ɴ', text) # TODO: hira2ipa simplifies to this replace statement
        text = re.sub(r'(?<=[brk])j(?=o)', 'ʲ', text) # replace_chars_2
        # text = text.replace('kyu', 'kʲu') # TODO: impossible because u was replaced by roma_mapper
        text = replace_tashdid_2(text)
        ### TODO: was originally 'aiueo' but impossible for 'u' to occur, it was replaced by roma_mapper
        text = re.sub(r'([aeio])\1', r'\1ː', text) # replace_repeated_chars
        ###
        for a, b in nasal_sounds:
            text = text.replace(a, b)
        text = text.replace(' ɴ', 'ɴ')
        text = text.replace(' neɽitai ', 'naɽitai').replace('harɯdʑisama', 'arɯdʑisama')
        text = re.sub(r'(?<!\s)ki ni ɕinai', ' ki ni ɕinai', text)
        # text = re.sub(r'(?<!\s)ʔt', 'ʔt', text) # TODO: does nothing, replaced value is identical
        text = re.sub(r'(?<!\s)de aɽoɯ', ' de aɽoɯ', text)
        return text.lstrip()

    def phonemize(self, text):
        output = self._process_japanese_text(text)
        if text.endswith(' '):
            output += ' '
        for a, b in k_mapper: # post_fix
            output = output.replace(a, b)
        # output = output.replace(' ɴ', 'ɴ') # TODO: does nothing because already covered in _process_japanese_text and we fixed k_mapper
        output = output.replace('y', 'j').replace('ɯa', 'wa')
        output = output.replace('a aː', 'a~').replace('a a', 'a~')
        output = replace_repeating_a(output)
        output = re.sub(r'\s+~', '~', output)

        output = output.replace('oː~o oː~ o', 'oː~~~~~~')
        output = output.replace('aː~aː', 'aː~~~')
        output = output.replace('oɴ naː', 'onnaː')
        output = output.replace('aː~~ aː', 'aː~~~~')
        output = output.replace('oː~o', 'oː~~')
        output = output.replace('oː~~o o', 'oː~~~~')  # yeah I'm too tired to learn regex how did you know
        for a, b in spaces: # random_space_fix
            output = output.replace(a, b)
        for a, b in symbols: # random_sym_fix, random_sym_fix_no_space
            output = output.replace(a, ' '+b+' ')
        output = output.lstrip()
        if text.endswith(' '):
            output += ' '
        return output

