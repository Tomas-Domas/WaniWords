import requests
import json

from config import WANIKANI_API_TOKEN, JPDB_API_TOKEN

DATA_CACHE_FILE = "Data_Cache.json"
FREQUENCY_LIST_FILE = "Frequency_List.json"
FREQ_SOURCE_FILE = "BCCWJ_frequencylist_suw_ver1_0.tsv"
BLACKLISTED_WORD_TYPES = ["助詞", "助動詞", "接尾辞", "数詞"]
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


def main():
    # === Regenerate Frequency List File
    # generate_frequency_list()

    # USE TO UPDATE THE CACHED WK_Kanji.json FILE
    with open(DATA_CACHE_FILE, "r", encoding='utf-8') as data_cache_file:
        data_cache_json = json.load(data_cache_file)

    # === Update cached WK Subjects and User Assignments
    # download_all_kanji_subjects(data_cache_json)
    # download_all_vocabulary_subjects(data_cache_json)
    # download_user_kanji_assignments(data_cache_json)
    # download_user_vocabulary_assignments(data_cache_json)
    with open(DATA_CACHE_FILE, "w", encoding='utf-8') as data_cache_file:
        json.dump(
            data_cache_json,
            data_cache_file,
            indent=3,
            ensure_ascii=False
        )

    known_kanji_list = get_known_kanji_list(data_cache_json)
    known_vocabulary_list = get_known_vocabulary_list(data_cache_json)

    candidate_words_list = get_candidate_words_list(known_kanji_list, 5000)
    print("Generated list of %d candidate words:\n" % len(candidate_words_list) + str(candidate_words_list))
    filtered_words_list = filter_out_known_vocabulary(candidate_words_list, known_vocabulary_list)
    print("Generated list of %d filtered words:\n" % len(filtered_words_list) + str(filtered_words_list))

def download_all_kanji_subjects(data_cache_json: dict[str, dict]) -> None:
    """
    :param data_cache_json: Object to cache the WaniKani Kanji Subjects
    """
    kanji_subjects_list = get_data_from_wanikani_api(
        endpoint="subjects",
        parameters={
            "types": "kanji"
        }
    )
    id_to_kanji_dictionary = {}
    for kanji in kanji_subjects_list:
        id_to_kanji_dictionary[kanji["id"]] = kanji["data"]["characters"]

    data_cache_json["all_kanji_subjects"] = id_to_kanji_dictionary
    print("Wanikani Kanji Subjects have been updated")

def download_all_vocabulary_subjects(data_cache_json: dict[str, dict]) -> None:
    """
    :param data_cache_json: Object to cache the WaniKani Vocabulary Subjects
    """
    vocabulary_subjects_list = get_data_from_wanikani_api(
        endpoint="subjects",
        parameters={
            "types": "vocabulary,kana_vocabulary"
        }
    )
    id_to_vocabulary_dictionary = {}
    for vocabulary in vocabulary_subjects_list:
        id_to_vocabulary_dictionary[vocabulary["id"]] = vocabulary["data"]["characters"]

    data_cache_json["all_vocabulary_subjects"] = id_to_vocabulary_dictionary
    print("Wanikani Vocabulary Subjects have been updated")

def download_user_kanji_assignments(data_cache_json: dict[str, dict]) -> None:
    """
    :param data_cache_json: Object to cache the User's Kanji Assignments
    """
    kanji_assignments_list = get_data_from_wanikani_api(
        endpoint="assignments",
        parameters={
            "subject_types": "kanji",
            "srs_stages": "5,6,7,8,9"
        }
    )
    id_to_srs_dictionary = {}
    for kanji in kanji_assignments_list:
        id_to_srs_dictionary[kanji["data"]["subject_id"]] = kanji["data"]["srs_stage"]

    data_cache_json["user_kanji_assignments"] = id_to_srs_dictionary
    print("User Kanji Assignments have been updated")

def download_user_vocabulary_assignments(data_cache_json: dict[str, dict]) -> None:
    """
    :param data_cache_json: Object to cache the User's Vocabulary Assignments
    """
    vocabulary_assignments_list = get_data_from_wanikani_api(
        endpoint="assignments",
        parameters={
            "subject_types": "vocabulary,kana_vocabulary",
            "srs_stages": "1,2,3,4,5,6,7,8,9"
        }
    )
    id_to_srs_dictionary = {}
    for vocabulary in vocabulary_assignments_list:
        id_to_srs_dictionary[vocabulary["data"]["subject_id"]] = vocabulary["data"]["srs_stage"]

    data_cache_json["user_vocabulary_assignments"] = id_to_srs_dictionary
    print("User Vocabulary Assignments have been updated")

def generate_frequency_list() -> None:
    """
    Populate Frequency List file from the BCCWJ database file
    Filters out words that are categorized as any of the Blacklisted Types
    """
    with open(FREQUENCY_LIST_FILE, "w") as frequency_list_file:
        list_of_words = []
        with open(FREQ_SOURCE_FILE, "r", encoding='utf-8') as freq_source_file:
            for line in freq_source_file:
                data = line.split('\t')
                word = data[2]
                word_type = data[3]
                word_is_blacklisted = False
                for blacklisted_type in BLACKLISTED_WORD_TYPES:
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

def get_known_kanji_list(data_cache_json: dict[str, dict]) -> list[str]:
    """
    :param data_cache_json: Object containing entries "user_kanji_assignments" and "all_kanji_subjects" as generated by the download functions
    :return: All the user's known kanji in Unicode
    """
    user_kanji_assignments = data_cache_json["user_kanji_assignments"]
    all_kanji_subjects = data_cache_json["all_kanji_subjects"]
    known_kanji_list = []
    for lesson_id in user_kanji_assignments:
        known_kanji_list.append(all_kanji_subjects[lesson_id])
    return known_kanji_list

def get_known_vocabulary_list(data_cache_json: dict[str, dict]) -> list[str]:
    """
    :param data_cache_json: Object containing entries "user_vocabulary_assignments" and "all_vocabulary_subjects" as generated by the download functions
    :return: All the user's known vocabulary in Unicode
    """
    user_vocabulary_assignments = data_cache_json["user_vocabulary_assignments"]
    all_vocabulary_subjects = data_cache_json["all_vocabulary_subjects"]
    known_vocabulary_list = []
    for lesson_id in user_vocabulary_assignments:
        known_vocabulary_list.append(all_vocabulary_subjects[lesson_id])
    return known_vocabulary_list

def get_candidate_words_list(known_kanji_list: list[str], up_to_frequency: int) -> list[str]:
    """
    :param known_kanji_list: All the known kanji to a user
    :param up_to_frequency: The number of words to be searched (e.g. 500 = the 500 most common words are searched)
    :return: Words that only contain known kanji (and kana)
    """
    known_character_list = KANA_LIST + known_kanji_list  # Append hiragana/katakana to known kanji for filtering
    with open(FREQUENCY_LIST_FILE, "r", encoding='utf-8') as frequency_list_file:
        words_list = json.load(frequency_list_file)
        if len(words_list) < up_to_frequency:  # Cap up_to_frequency to the length of word_list
            print("Frequency list doesn't contain %d items. Only searching %d.", (up_to_frequency, len(words_list)))
            up_to_frequency = len(words_list)

        candidate_words_list = []
        for i in range(up_to_frequency):
            current_word = words_list[i]

            is_candidate_word = True  # Check if word is composed only of known kanji TODO: this is janky
            for current_kanji in current_word:
                if current_kanji not in known_character_list:
                    is_candidate_word = False
                    break

            if is_candidate_word:
                candidate_words_list.append(current_word)
        return candidate_words_list

def filter_out_known_vocabulary(candidate_words_list: list[str], known_vocabulary_list: list[str]) -> list[str]:
    """
    :param candidate_words_list: Words to be checked
    :param known_vocabulary_list: Words to be filtered out of candidate_words_list
    :return: New list containing words that passed the filter
    """
    filtered_candidate_words_list = []
    for word in candidate_words_list:
        if word not in known_vocabulary_list:
            filtered_candidate_words_list.append(word)
    return filtered_candidate_words_list

def get_data_from_wanikani_api(endpoint: str, parameters: dict[str, str]) -> list[dict]:
    """
    :param endpoint: URL endpoint for the API request
    :param parameters: Parameters and Filters for the API request
    :return: JSON objects received from the request. Handles pagination by combining all returned pages
    """
    response = requests.request(
        method="GET",
        url="https://api.wanikani.com/v2/" + endpoint,
        headers={
            "Authorization": "Bearer " + WANIKANI_API_TOKEN
        },
        params=parameters
    ).json()

    data_array = []
    while True:
        data_array += response["data"]
        next_page = response["pages"]["next_url"]
        if next_page is None:
            break
        else:
            response = requests.request(
                method="GET",
                url=next_page,
                headers={
                    "Authorization": "Bearer " + WANIKANI_API_TOKEN
                }
            ).json()

    return data_array

if __name__ == "__main__":
    main()
