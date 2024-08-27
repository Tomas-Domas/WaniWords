from sys import exit
from requests import request

_WANIWORDS_DECK_NAME = "WaniWords"

class JPDBHandler:
    def __init__(self, api_token):
        self._api_token = api_token

    def _call_api(self, endpoint: str, json: dict):
        response_json = request(
            method="POST",
            url="https://jpdb.io/api/v1/" + endpoint,
            headers={
                "Authorization": "Bearer " + self._api_token
            },
            json=json,
        ).json()

        if "error" in response_json:
            match response_json["error"]:
                case "bad_key":
                    print("JPDB API Error! JPDB API Key is invalid.")
                case _:
                    print("JPDB API Error! Error Message: %s." % response_json["error_message"])
            exit(1)

        return response_json


    def _get_vocabulary_ids(self, vocabulary_list: list[str]) -> list[list]:
        # Format the vocabulary_list as a newline-separated string for the API call
        text = ""
        for word in vocabulary_list:
            text += word + "\n"

        vocabulary_ids_dictionary = self._call_api(
            endpoint="parse",
            json={
                "text": text[:-1],
                "token_fields": [],
                "vocabulary_fields": [
                    "vid",  # Vocabulary ID
                    "sid"   # Spelling ID - refers to alternative spellings of a single Vocabulary item
                ]
            }
        )

        return vocabulary_ids_dictionary["vocabulary"]


    def _get_decks(self) -> tuple[list, list]:
        decks_dictionary = self._call_api(
            endpoint="list-user-decks",
            json={
                "fields": [
                    "name",
                    "id"
                ]
            }
        )
        deck_names_list = []
        deck_ids_list = []
        for deck_data in decks_dictionary["decks"]:
            deck_names_list.append(deck_data[0])
            deck_ids_list.append(deck_data[1])

        return deck_names_list, deck_ids_list


    def _create_waniwords_deck(self, deck_position: int = 0) -> int:
        deck_dictionary = self._call_api(
            endpoint="deck/create-empty",
            json={
                "name": _WANIWORDS_DECK_NAME,
                "position": deck_position
            }
        )
        return deck_dictionary["id"]


    def _add_vocabulary_to_deck(self, deck_id: int, vocabulary_ids_list: list[list]) -> None:
        self._call_api(
            endpoint="deck/add-vocabulary",
            json={
                "id": deck_id,
                "vocabulary": vocabulary_ids_list,
                "replace_existing_occurences": True,
            }
        )


    def add_vocabulary_to_waniwords_deck(self, words_list):
        deck_names_list, deck_ids_list = self._get_decks()

        try:
            waniwords_deck_index = deck_names_list.index(_WANIWORDS_DECK_NAME)
            waniwords_deck_id = deck_ids_list[waniwords_deck_index]
            print("Existing %s deck found!" % _WANIWORDS_DECK_NAME)
        except ValueError:
            print("Existing %s deck NOT found! Creating Deck..." % _WANIWORDS_DECK_NAME)
            waniwords_deck_id = self._create_waniwords_deck(len(deck_names_list)) 

        vocabulary_ids_list = self._get_vocabulary_ids(words_list)
        self._add_vocabulary_to_deck(waniwords_deck_id, vocabulary_ids_list)
