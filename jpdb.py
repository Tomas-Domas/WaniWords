import requests

_WANIWORDS_DECK_NAME = "WaniWordsTest"

class JPDBHandler:
    def __init__(self, api_token):
        self._api_token = api_token


    def _get_vocabulary_ids(self, vocabulary_list: list[str]) -> list[list]:
        # Format the vocabulary_list as a newline-separated string for the API call
        text = ""
        for word in vocabulary_list:
            text += word + "\n"


        vocabulary_ids_dictionary = requests.request(
            method="POST",
            url="https://jpdb.io/api/v1/parse",
            headers={
                "Authorization": "Bearer " + self._api_token
            },
            json={
                "text": text[:-1],
                "token_fields": [],
                "vocabulary_fields": [
                    "vid",  # Vocabulary ID
                    "sid"   # Spelling ID - refers to alternative spellings of a single Vocabulary item
                ]
            }
        ).json()

        return vocabulary_ids_dictionary["vocabulary"]


    def _get_decks(self) -> tuple[list, list]:
        decks_dictionary = requests.request(
            method="POST",
            url="https://jpdb.io/api/v1/list-user-decks",
            headers={
                "Authorization": "Bearer " + self._api_token
            },
            json={
                "fields": [
                    "name",
                    "id"
                ]
            }
        ).json()
        deck_names_list = []
        deck_ids_list = []
        for deck_data in decks_dictionary["decks"]:
            deck_names_list.append(deck_data[0])
            deck_ids_list.append(deck_data[1])

        return deck_names_list, deck_ids_list


    def _create_waniwords_deck(self, deck_position: int = 0) -> int:
        deck_json = requests.request(
            method="POST",
            url="https://jpdb.io/api/v1/deck/create-empty",
            headers={
                "Authorization": "Bearer " + self._api_token
            },
            json={
                "name": _WANIWORDS_DECK_NAME,
                "position": deck_position
            }
        ).json()
        return deck_json["id"]


    def _add_vocabulary_to_deck(self, deck_id: int, vocabulary_ids_list: list[list]) -> None:
        requests.request(
            method="POST",
            url="https://jpdb.io/api/v1/deck/add-vocabulary",
            headers={
                "Authorization": "Bearer " + self._api_token
            },
            json={
                "id": deck_id,
                "vocabulary": vocabulary_ids_list,
                "replace_existing_occurences": True,
            }
        ).json()


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
