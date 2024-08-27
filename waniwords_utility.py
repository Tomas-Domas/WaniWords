from json import load, dump, decoder
from datetime import datetime, timezone

_NLT_BLACKLISTED_WORD_TYPES = ["助詞", "助動詞", "動詞-接尾", "記号"]
_NLT_DATABASE_FILE = "NLT1.40_freq_list.csv"
_BCCWJ_BLACKLISTED_WORD_TYPES = ["接尾辞"]
_BCCWJ_DATABASE_FILE = "BCCWJ_frequencylist_suw_ver1_0.tsv"
_BLACKLISTED_SYMBOLS = ["*", "％", "ｍ", "ｇ", "8", "【"]
_FREQUENCY_LIST_FILE = "Frequency_List.json"

_API_CONFIG_FILE = "config.json"
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


def generate_frequency_list_file() -> None:
    """
    Generate a Frequency List file from the NLT database, and refine it with the BCCWJ database 
    Excludes words of a blacklisted type or that contain a blacklisted symbol 
    """
    # Generate initial list from NLT
    list_of_entries = []
    with open(_NLT_DATABASE_FILE, "r", encoding='utf-8') as nlt_database_file:
        word_count = 0
        for line in nlt_database_file:
            data = line.split(',')
            word_lemma = data[0].strip()
            word_type = data[1].strip()
            word_reading = data[2].strip()
            # Remove blacklisted word types
            if word_type in _NLT_BLACKLISTED_WORD_TYPES or word_lemma == "": 
                continue
            # Remove blacklisted symbols
            for symbol in _BLACKLISTED_SYMBOLS:
                if symbol in word_lemma:
                    break  
            else:
                word_count += 1
                list_of_entries.append((word_lemma, word_reading))
            # Stop at ~50,000 words so it's not a huge file
            if word_count == 51000:
                break
    
    # Generate blacklist from BCCWJ
    list_of_blacklisted_entries = []
    with open(_BCCWJ_DATABASE_FILE, "r", encoding='utf-8') as bccwj_database_file:
        word_count = 0
        for line in bccwj_database_file:
            word_count += 1
            data = line.split('\t')
            word_lemma = data[2].strip()
            word_type = data[3].strip()
            word_reading = data[1].strip()
            # Add blacklisted words to list
            for blacklisted_type in _BCCWJ_BLACKLISTED_WORD_TYPES:
                if blacklisted_type in word_type:
                    list_of_blacklisted_entries.append((word_lemma, word_reading))
                    break
            if word_count == 70000:
                break
    
    # Only add words to final list if they don't match the blacklist from BCCWJ
    list_of_words = []
    for entry in list_of_entries:
        for blacklisted_entry in list_of_blacklisted_entries:
            if entry[0] == blacklisted_entry[0] and entry[1] == blacklisted_entry[1]:
                break
        else:
            list_of_words.append(entry[0])

    # Write output database file
    with open(_FREQUENCY_LIST_FILE, "w", encoding='utf-8') as frequency_list_file:
        dump(
            list_of_words[1:],
            frequency_list_file,
            indent=0
        )
    

def get_api_keys() -> dict:
    api_keys_dict = {}
    try:
        config_file = open(_API_CONFIG_FILE, "r+", encoding='utf-8')
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
        config_file = open(_API_CONFIG_FILE, "x", encoding='utf-8')
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
    with open(_API_CONFIG_FILE, "r+", encoding='utf-8') as config_file:
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
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
