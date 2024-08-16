from json import load, dump, decoder
from datetime import datetime, timezone

KANA_LIST = [
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
_BLACKLISTED_WORD_TYPES = ["助詞", "助動詞", "接尾辞", "数詞", "固有名詞"]
_CONFIG_FILE = "config.json"
_FREQUENCY_LIST_FILE = "Frequency_List.json"
_FREQ_SOURCE_FILE = "BCCWJ_frequencylist_suw_ver1_0.tsv"


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
        dump(
            list_of_words[1:],
            frequency_list_file,
            indent=0
        )
    

def get_api_keys() -> dict:
    api_keys_dict = {}
    try:
        config_file = open(_CONFIG_FILE, "r+", encoding='utf-8')
        api_keys_dict = load(config_file)
        if ("wanikani" not in api_keys_dict) and ("jpdb" not in api_keys_dict):
            raise KeyError("wanikani", "jpdb")
        if "wanikani" not in api_keys_dict:
            raise KeyError("wanikani")
        if "jpdb" not in api_keys_dict:
            raise KeyError("jpdb")

    except KeyError as key_error:
        for missing_key in key_error.args:
            print("Missing %s key from config..." % missing_key)
            api_keys_dict[missing_key] = input("Enter %s API key: " % missing_key)

    except FileNotFoundError:
        print("Creating new config file...")
        config_file = open(_CONFIG_FILE, "x", encoding='utf-8')
        api_keys_dict = {
            "wanikani": input("Enter wanikani API key: "),
            "jpdb":     input("Enter jpdb API key: ")
        }

    except decoder.JSONDecodeError:
        print("Error decoding config file...")
        api_keys_dict = {
            "wanikani": input("Enter wanikani API key: "),
            "jpdb":     input("Enter jpdb API key: ")
        }

    finally:
        config_file.seek(0)
        config_file.truncate()
        dump(
            api_keys_dict,
            config_file,
            indent=3,
            ensure_ascii=False
        )
        config_file.close()
        return api_keys_dict


def remove_key_from_config(key: str):
    with open(_CONFIG_FILE, "r+", encoding='utf-8') as config_file:
        api_keys_dict = load(config_file)
        del api_keys_dict[key]
        config_file.seek(0)
        config_file.truncate()
        dump(
            api_keys_dict,
            config_file,
            indent=3,
            ensure_ascii=False
        )


def generate_frequent_words(num_of_words: int) -> list[str]:
    """
    Generate a list of words from the frequency list file
    :param num_of_words: The number of words to retrieve (e.g. 500 = the 500 most common words)
    :return: List of words in frequency order from the frequency list file
    """
    with open(_FREQUENCY_LIST_FILE, "r", encoding='utf-8') as frequency_list_file:
        words_list = load(frequency_list_file)
        if len(words_list) < num_of_words:  # Cap up_to_frequency to the length of word_list
            print("Frequency list doesn't contain %d words. Could only retrieve %d.", (num_of_words, len(words_list)))
            return words_list
        else:
            return words_list[0:num_of_words]

def get_time():
    return datetime.now(timezone.utc).strftime("%a, %d %m %Y %H:%M:%S GMT")