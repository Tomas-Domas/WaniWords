from sys import exit
from json import load, dump, decoder
from requests import request

from waniwords_utility import remove_key_from_config, get_time, KANA_LIST

_WANIKANI_CACHE_FILE = "WaniKani_Cache.json"

class WaniKaniHandler:
    def __init__(self, api_token):
        """
        Creates a WaniKaniHandler that interfaces with the WaniKani API and takes care of the user's data.
        Takes data from the cache file.
        :param api_token: the user's WaniKani API Token. Only needs read permissions
        """
        self._api_token = api_token
        try:
            cache_file = open(_WANIKANI_CACHE_FILE, "r", encoding='utf-8')
            self._data_dictionary = load(cache_file)
        except FileNotFoundError:
            print("Creating new cache file...")
            cache_file = open(_WANIKANI_CACHE_FILE, "x", encoding='utf-8')
            self._data_dictionary = {}
        except decoder.JSONDecodeError:
            print("Error decoding cache file. Ignoring cache contents.")
            self._data_dictionary = {}
        finally:
            cache_file.close()


    def _call_api(self, endpoint: str, parameters: dict[str, str]) -> list[dict]:
        """
        Wrapper for calling the WaniKani API. Packages the received data into a list
        :param endpoint: URL endpoint for the API request
        :param parameters: Parameters and Filters for the initial API request
        :return: List of JSON objects received from the request
        """
        data_array = []
        next_page = "https://api.wanikani.com/v2/" + endpoint
        if "timestamp" in self._data_dictionary:
            next_page += "?updated_after=" + self._data_dictionary["timestamp"]

        while next_page is not None:
            response_json = request(
                method="GET",
                url=next_page,
                headers={
                    "Authorization": "Bearer " + self._api_token
                },
                params=parameters
            ).json()
            try:
                data_array += response_json["data"]
                parameters = None
                next_page = response_json["pages"]["next_url"]
            except KeyError:
                response_code = response_json["code"]
                match response_code:
                    case 401:
                        print("WaniKani API Error! WaniKani API Key is invalid.")
                        remove_key_from_config("wanikani")
                    case _:
                        print("WaniKani API Error! Response Code: %d." % response_code)
                exit(1)

        return data_array


    def download_all_data(self) -> None:
        """
        Downloads the subjects and assignments for both vocabulary and kanji.
        Writes the downloaded data to the cache file
        """
        self._download_user_known_kanji()
        self._download_user_known_vocabulary()
        self._download_wanikani_kanji()
        self._download_wanikani_vocabulary()

        self._write_cache()
    

    def _update_data_dictionary(self, key, new_data):
        if key in self._data_dictionary:
            self._data_dictionary[key] |= new_data
        else:
            self._data_dictionary[key] = new_data



    def _download_wanikani_kanji(self) -> None:
        """
        Downloads all the WaniKani kanji subjects.
        Stored in a dictionary as a (subject_id : kanji_string) pair
        """
        kanji_subjects_list = self._call_api(
            endpoint="subjects",
            parameters={
                "types": "kanji"
            }
        )
        id_to_kanji_dictionary = {}
        for kanji in kanji_subjects_list:
            id = str(kanji["id"])
            id_to_kanji_dictionary[id] = kanji["data"]["characters"]

        self._update_data_dictionary(key="all_kanji_subjects", new_data=id_to_kanji_dictionary)
        print("Wanikani Kanji Subjects have been updated")


    def _download_wanikani_vocabulary(self) -> None:
        """
        Downloads all the WaniKani vocabulary subjects
        Stored in a dictionary as a (subject_id : vocabulary_string) pair
        """
        vocabulary_subjects_list = self._call_api(
            endpoint="subjects",
            parameters={
                "types": "vocabulary,kana_vocabulary"
            }
        )
        id_to_vocabulary_dictionary = {}
        for vocabulary in vocabulary_subjects_list:
            id = str(vocabulary["id"])
            id_to_vocabulary_dictionary[id] = vocabulary["data"]["characters"]

        self._update_data_dictionary(key="all_vocabulary_subjects", new_data=id_to_vocabulary_dictionary)
        print("Wanikani Vocabulary Subjects have been updated")


    def _download_user_known_kanji(self) -> None:
        """
        Downloads user's kanji assignments that are Guru level or higher
        Stored in a dictionary as a (subject_id : srs_stage) pair
        """
        kanji_assignments_list = self._call_api(
            endpoint="assignments",
            parameters={
                "subject_types": "kanji",
                "srs_stages": "5,6,7,8,9"
            }
        )
        id_to_srs_dictionary = {}
        for kanji in kanji_assignments_list:
            id = str(kanji["data"]["subject_id"])
            id_to_srs_dictionary[id] = kanji["data"]["srs_stage"]
        self._update_data_dictionary(key="user_kanji_assignments", new_data=id_to_srs_dictionary)
        print("User Kanji Assignments have been updated")


    def _download_user_known_vocabulary(self) -> None:
        """
        Downloads user's vocabulary assignments that are Apprentice level or higher
        Stored in a dictionary as a (subject_id : srs_stage) pair
        """
        vocabulary_assignments_list = self._call_api(
            endpoint="assignments",
            parameters={
                "subject_types": "vocabulary,kana_vocabulary",
                "srs_stages": "1,2,3,4,5,6,7,8,9"
            }
        )
        id_to_srs_dictionary = {}
        for vocabulary in vocabulary_assignments_list:
            id = str(vocabulary["data"]["subject_id"])
            id_to_srs_dictionary[id] = vocabulary["data"]["srs_stage"]
        
        self._update_data_dictionary(key="user_vocabulary_assignments", new_data=id_to_srs_dictionary)
        print("User Vocabulary Assignments have been updated")


    def _write_cache(self) -> None:
        """
        Writes the currently held data to the cache file, timestamped
        """
        self._data_dictionary["timestamp"] = get_time()
        with open(_WANIKANI_CACHE_FILE, "w", encoding='utf-8') as cache_file:
            dump(
                self._data_dictionary,
                cache_file,
                indent=3,
                ensure_ascii=False
            )


    def get_known_kanji_list(self) -> list[str]:
        """
        Cross-references the user and wanikani data to produce a list of known kanji
        :return: List containing unicode strings of kanji
        """
        known_kanji_list = []
        for lesson_id in self._data_dictionary["user_kanji_assignments"]:
            known_kanji_list.append(self._data_dictionary["all_kanji_subjects"][lesson_id])
        return known_kanji_list


    def get_known_vocabulary_list(self) -> list[str]:
        """
        Cross-references the user and wanikani data to produce a list of known vocabulary words
        :return: List containing unicode strings of vocabulary words
        """
        known_vocabulary_list = []
        for lesson_id in self._data_dictionary["user_vocabulary_assignments"]:
            known_vocabulary_list.append(self._data_dictionary["all_vocabulary_subjects"][lesson_id])
        return known_vocabulary_list


    def filter_out_known_words(self, list_of_words: list[str]) -> list[str]:
        """
        Removes words from the list that were learned through WaniKani
        :param list_of_words: list of words to be filtered
        :return: list of words that passed the filter
        """
        known_vocabulary = self.get_known_vocabulary_list()
        new_list_of_words = []
        for word in list_of_words:
            if word not in known_vocabulary:
                new_list_of_words.append(word)
        return new_list_of_words


    def filter_out_unknown_kanji(self, list_of_words: list[str]) -> list[str]:
        """
        Removes words from the list that contain kanji not yet learned through WaniKani.
        :param list_of_words: list of words to be filtered
        :return: list of words that passed the filter
        """
        new_list_of_words = []
        known_characters = KANA_LIST + self.get_known_kanji_list()

        for word in list_of_words:
            for character in word:
                if character not in known_characters:
                    break
            else:
                new_list_of_words.append(word)    
        return new_list_of_words
    
    def filter_out_kana_words(self, list_of_words: list[str]) -> list[str]:
        """
        Removes words from the list that contain kana-only words.
        :param list_of_words: list of words to be filtered
        :return: list of words that passed the filter
        """
        new_list_of_words = []
        known_characters = KANA_LIST

        for word in list_of_words:
            for character in word:
                if character not in known_characters:
                    break
            else:
                continue  # Continue to the outer loop to skip appending
            new_list_of_words.append(word)                
        return new_list_of_words