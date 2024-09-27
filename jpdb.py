from requests import request
from waniwords_utility import print_list

class JPDBHandler:
    def __init__(self, api_token):
        self._api_token = api_token

    def _call_api(self, endpoint: str, json: dict):
        try:
            response_json = request(
                method="POST",
                url="https://jpdb.io/api/v1/" + endpoint,
                headers={
                    "Authorization": "Bearer " + self._api_token
                },
                json=json,
            ).json()
        except:  # I know, I know... I am sorry
                print("JDPB Request error!")
                raise ConnectionError("Error! JDPB API Connection failed. Check your internet connection?")

        if "error" in response_json:
            match response_json["error"]:
                case "bad_key":
                    print("JPDB API Error! JPDB API Key is invalid.")
                    raise KeyError("Error! JPDB API Key is invalid.")
                case _:
                    print("JPDB API Error! Error Message: %s." % response_json["error_message"])
                    raise KeyError("JPDB API Error! Error Message: %s." % response_json["error_message"])
                

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


    def _create_deck(self, deck_name: str, deck_position: int = 0) -> int:
        deck_dictionary = self._call_api(
            endpoint="deck/create-empty",
            json={
                "name": deck_name,
                "position": deck_position
            }
        )
        return deck_dictionary["id"]


    def _get_differences(self, deck_id: int, new_vocab_ids_list: list[list]) -> tuple[list, list]:
        old_vocab_ids_list = self._get_deck_vocabulary(deck_id)
        word_ids_only_in_new = []
        for word_ids in new_vocab_ids_list:
            if word_ids not in old_vocab_ids_list:
                word_ids_only_in_new.append(word_ids)
        
        word_ids_only_in_old = []
        for word_ids in old_vocab_ids_list:
            if word_ids not in new_vocab_ids_list:
                word_ids_only_in_old.append(word_ids)
        
        return (word_ids_only_in_new, word_ids_only_in_old)
        

    def _get_deck_vocabulary(self, deck_id: int) -> list[int]:
        vocabulary_ids_dictionary = self._call_api(
            endpoint="deck/list-vocabulary",
            json={
                "id": deck_id,
                "fetch_occurences": False
            }
        )
        return vocabulary_ids_dictionary["vocabulary"]


    def _get_vocabulary_spellings(self, vocabulary_ids_list) -> list[str]:
        vocabulary_spellings_dictionary = self._call_api(
            endpoint="lookup-vocabulary",
            json={
                "list": vocabulary_ids_list,
                "fields": ["spelling"]
            }
        )
        vocabulary_spellings_list = []
        for vocabulary_data in vocabulary_spellings_dictionary["vocabulary_info"]:
            vocabulary_spellings_list.append(vocabulary_data[0])
        return vocabulary_spellings_list


    def _add_vocabulary_to_deck(self, deck_id: int, vocabulary_ids_list: list[list]) -> None:
        self._call_api(
            endpoint="deck/add-vocabulary",
            json={
                "id": deck_id,
                "vocabulary": vocabulary_ids_list,
                "replace_existing_occurences": True,
            }
        )


    def add_vocabulary_to_waniwords_deck(self, words_list: list[str], deck_name: str = "WaniWords") -> None:
        vocabulary_ids_list = self._get_vocabulary_ids(words_list)
        deck_names_list, deck_ids_list = self._get_decks()
        try:  # Get the deck id of the WaniWords deck from the list of decks
            waniwords_deck_index = deck_names_list.index(deck_name)
            print("Existing \"%s\" deck found!" % deck_name)
            waniwords_deck_id = deck_ids_list[waniwords_deck_index]
            found_waniwords_deck = True
        except ValueError:
            print("Existing \"%s\" deck NOT found! Creating Deck..." % deck_name)
            waniwords_deck_id = self._create_deck(deck_name=deck_name)
            found_waniwords_deck = False
        
        new_word_ids, obsolete_word_ids = self._get_differences(waniwords_deck_id, vocabulary_ids_list)
        if found_waniwords_deck:
            print("Added Vocabulary Words:")
            print_list(self._get_vocabulary_spellings(new_word_ids))
            print("Obsolete Vocabulary Words:")
            print_list(self._get_vocabulary_spellings(obsolete_word_ids))

        self._add_vocabulary_to_deck(waniwords_deck_id, new_word_ids)
