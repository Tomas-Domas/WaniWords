import json
import requests

WANIKANI_CACHE_FILE = "WaniKani_Cache.json"

class WaniKaniHandler:
    def __init__(self, api_token):
        """
        Creates a WaniKaniHandler that interfaces with the WaniKani API and takes care of the user's data.
        Takes data from the cache file.
        :param api_token: the user's WaniKani API Token. Only needs read permissions
        """
        self._api_token = api_token
        with open(WANIKANI_CACHE_FILE, "r", encoding='utf-8') as cache_file:
            self._data_dictionary = json.load(cache_file)

    def _get_data_from_api(self, endpoint: str, parameters: dict[str, str]) -> list[dict]:
        """
        Wrapper for calling the WaniKani API. Packages the received data into a list
        :param endpoint: URL endpoint for the API request
        :param parameters: Parameters and Filters for the initial API request
        :return: List of JSON objects received from the request
        """
        data_array = []
        next_page = "https://api.wanikani.com/v2/" + endpoint
        while next_page is not None:
            response_json = requests.request(
                method="GET",
                url=next_page,
                headers={
                    "Authorization": "Bearer " + self._api_token
                },
                params=parameters
            ).json()
            data_array += response_json["data"]
            parameters = None
            next_page = response_json["pages"]["next_url"]
        return data_array

    def download_all_data(self) -> None:
        """
        Downloads the subjects and assignments for both vocabulary and kanji.
        Writes the downloaded data to the cache file
        """
        self.download_wanikani_vocabulary()
        self.download_wanikani_kanji()
        self.download_user_known_vocabulary()
        self.download_user_known_kanji()
        self.write_cache()

    def download_wanikani_kanji(self) -> None:
        """
        Downloads all the WaniKani kanji subjects.
        Stored in a dictionary as a (subject_id : kanji_string) pair
        Does not write the downloaded data to the cache file. For this, use write_cache()
        """
        kanji_subjects_list = self._get_data_from_api(
            endpoint="subjects",
            parameters={
                "types": "kanji"
            }
        )
        id_to_kanji_dictionary = {}
        for kanji in kanji_subjects_list:
            id_to_kanji_dictionary[kanji["id"]] = kanji["data"]["characters"]

        self._data_dictionary["all_kanji_subjects"] = id_to_kanji_dictionary
        print("Wanikani Kanji Subjects have been updated")

    def download_wanikani_vocabulary(self) -> None:
        """
        Downloads all the WaniKani vocabulary subjects
        Stored in a dictionary as a (subject_id : vocabulary_string) pair
        Does not write the downloaded data to the cache file. For this, use write_cache()
        """
        vocabulary_subjects_list = self._get_data_from_api(
            endpoint="subjects",
            parameters={
                "types": "vocabulary,kana_vocabulary"
            }
        )
        id_to_vocabulary_dictionary = {}
        for vocabulary in vocabulary_subjects_list:
            id_to_vocabulary_dictionary[vocabulary["id"]] = vocabulary["data"]["characters"]

        self._data_dictionary["all_vocabulary_subjects"] = id_to_vocabulary_dictionary
        print("Wanikani Vocabulary Subjects have been updated")

    def download_user_known_kanji(self) -> None:
        """
        Downloads user's kanji assignments that are Guru level or higher
        Stored in a dictionary as a (subject_id : srs_stage) pair
        Does not write the downloaded data to the cache file. For this, use write_cache()
        """
        kanji_assignments_list = self._get_data_from_api(
            endpoint="assignments",
            parameters={
                "subject_types": "kanji",
                "srs_stages": "5,6,7,8,9"
            }
        )
        id_to_srs_dictionary = {}
        for kanji in kanji_assignments_list:
            id_to_srs_dictionary[kanji["data"]["subject_id"]] = kanji["data"]["srs_stage"]

        self._data_dictionary["user_kanji_assignments"] = id_to_srs_dictionary
        print("User Kanji Assignments have been updated")

    def download_user_known_vocabulary(self) -> None:
        """
        Downloads user's vocabulary assignments that are Apprentice level or higher
        Stored in a dictionary as a (subject_id : srs_stage) pair
        Does not write the downloaded data to the cache file. For this, use write_cache()
        """
        vocabulary_assignments_list = self._get_data_from_api(
            endpoint="assignments",
            parameters={
                "subject_types": "vocabulary,kana_vocabulary",
                "srs_stages": "1,2,3,4,5,6,7,8,9"
            }
        )
        id_to_srs_dictionary = {}
        for vocabulary in vocabulary_assignments_list:
            id_to_srs_dictionary[vocabulary["data"]["subject_id"]] = vocabulary["data"]["srs_stage"]

        self._data_dictionary["user_vocabulary_assignments"] = id_to_srs_dictionary
        print("User Vocabulary Assignments have been updated")

    def write_cache(self) -> None:
        """
        Writes the currently held data to the cache file
        """
        with open(WANIKANI_CACHE_FILE, "w", encoding='utf-8') as cache_file:
            json.dump(
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
