import json

from wanikani import WaniKaniHandler

_FREQUENCY_LIST_FILE = "Frequency_List.json"
_FREQ_SOURCE_FILE = "BCCWJ_frequencylist_suw_ver1_0.tsv"
_BLACKLISTED_WORD_TYPES = ["助詞", "助動詞", "接尾辞", "数詞", "固有名詞"]
_KANA_LIST = [
    'ぁ', 'あ', 'ぃ', 'い', 'ぅ', 'う', 'ゔ', 'ぇ', 'え', 'ぉ', 'お', 'ゕ', 'か', 'が', 'き', 'ぎ', 'く', 'ぐ', 'ゖ', 'け', 'げ',
    'こ', 'ご', 'さ', 'ざ', 'し', 'じ', 'す', 'ず', 'せ', 'ぜ', 'そ', 'ぞ', 'た', 'だ', 'ち', 'ぢ', 'っ', 'つ', 'づ', 'て', 'で',
    'と', 'ど', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ば', 'ぱ', 'ひ', 'び', 'ぴ', 'ふ', 'ぶ', 'ぷ', 'へ', 'べ', 'ぺ', 'ほ', 'ぼ',
    'ぽ', 'ま', 'み', 'む', 'め', 'も', 'ゃ', 'や', 'ゅ', 'ゆ', 'ょ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'ゎ', 'わ', 'ゐ', 'ゑ',
    'を', 'ん', 'ァ', 'ア', 'ィ', 'イ', 'ゥ', 'ウ', 'ヴ', 'ェ', 'エ', 'ォ', 'オ', 'ヵ', 'カ', 'ガ', 'キ', 'ギ', 'ク', 'グ', 'ヶ',
    'ケ', 'ゲ', 'コ', 'ゴ', 'サ', 'ザ', 'シ', 'ジ', 'ス', 'ズ', 'セ', 'ゼ', 'ソ', 'ゾ', 'タ', 'ダ', 'チ', 'ヂ', 'ッ', 'ツ', 'ヅ',
    'テ', 'デ', 'ト', 'ド', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'バ', 'パ', 'ヒ', 'ビ', 'ピ', 'フ', 'ブ', 'プ', 'ベ', 'ペ', 'ホ',
    'ボ', 'ポ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ャ', 'ヤ', 'ュ', 'ユ', 'ョ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ヮ', 'ワ', 'ヷ',
    'ヰ', 'ヸ', 'ヱ', 'ヹ', 'ヲ', 'ヺ', 'ン', '・', 'ー'
]

def generate_frequency_list_file() -> None:
    """
    Generate a Frequency List file from the BCCWJ database file
    Excludes words that fall under a Blacklisted type
    """
    with open(_FREQUENCY_LIST_FILE, "w") as frequency_list_file:
        list_of_words = []
        with open(_FREQ_SOURCE_FILE, "r", encoding='utf-8') as freq_source_file:
            for line in freq_source_file:
                data = line.split('\t')
                word = data[2]
                word_type = data[3]
                word_is_blacklisted = False
                for blacklisted_type in _BLACKLISTED_WORD_TYPES:
                    if blacklisted_type in word_type:
                        word_is_blacklisted = True
                        break
                if not word_is_blacklisted:
                    list_of_words.append(word)
        json.dump(
            list_of_words[1:],
            frequency_list_file,
            indent=0
        )

def generate_frequent_words(num_of_words: int) -> list[str]:
    """
    Generate a list of words from the frequency list file
    :param num_of_words: The number of words to retrieve (e.g. 500 = the 500 most common words)
    :return: List of words in frequency order from the frequency list file
    """
    with open(_FREQUENCY_LIST_FILE, "r", encoding='utf-8') as frequency_list_file:
        words_list = json.load(frequency_list_file)
        if len(words_list) < num_of_words:  # Cap up_to_frequency to the length of word_list
            print("Frequency list doesn't contain %d words. Could only retrieve %d.", (num_of_words, len(words_list)))
            return words_list
        else:
            return words_list[0:num_of_words]

def filter_out_known_words(list_of_words: list[str], wanikani_handler: WaniKaniHandler, invert_filter: bool = False) -> list[str]:
    """
    Removes words from the list that were learned through WaniKani
    :param list_of_words: list of words to be filtered
    :param wanikani_handler: WaniKaniHandler for the user
    :param invert_filter: whether the filter should be inverted (i.e. filter out unknown words)
    :return: list of words that passed the filter
    """
    known_vocabulary = wanikani_handler.get_known_vocabulary_list()
    new_list_of_words = []
    for word in list_of_words:
        if bool(word not in known_vocabulary) ^ invert_filter:  # Flip comparison if invert_filter
            new_list_of_words.append(word)
    return new_list_of_words

def filter_out_unknown_kanji(list_of_words: list[str], wanikani_handler: WaniKaniHandler, invert_filter: bool = False) -> list[str]:
    """
    Removes words from the list that contain kanji not yet learned through WaniKani
    :param list_of_words: list of words to be filtered
    :param wanikani_handler: WaniKaniHandler for the user
    :param invert_filter: whether the filter should be inverted (i.e. filter out words of only known kanji)
    :return: list of words that passed the filter
    """
    known_characters = _KANA_LIST + wanikani_handler.get_known_kanji_list()
    new_list_of_words = []
    if invert_filter is False:
        for word in list_of_words:
            for character in word:
                if character not in known_characters:
                    break
            else:
                new_list_of_words.append(word)
    else:
        for word in list_of_words:
            for character in word:
                if character not in known_characters:
                    break
            else:
                continue  # Continue to the outer loop to skip appending
            new_list_of_words.append(word)
    return new_list_of_words
