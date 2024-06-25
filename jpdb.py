import json
import requests


class JPDBHandler:
    def __init__(self, api_token):
        self._api_token = api_token

    def _get_vocabulary_ids(self, vocabulary_list) -> tuple[list, list]:
        # Format the vocabulary_list as a newline-separated string for the API call
        text = ""
        for word in vocabulary_list:
            text += word + "\n"

        vocabulary_ids_json = requests.request(
            method="POST",
            url="https://jpdb.io/api/v1/parse",
            headers={
                "Authorization": "Bearer " + self._api_token
            },
            json={
                "text": text[:-1],
                "token_fields": [],
                "vocabulary_fields": [
                    "vid",
                    "sid"
                ]
            }
        ).json()
        vids = []
        sids = []
        for word_data in vocabulary_ids_json["vocabulary"]:
            vids.append(word_data[0])
            sids.append(word_data[1])

        vids = [word_data[0] for word_data in vocabulary_ids_json["vocabulary"]]
        return vids, sids
















