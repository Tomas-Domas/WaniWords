import json

import utility_and_filters
from wanikani import WaniKaniHandler
from config import WANIKANI_API_TOKEN, JPDB_API_TOKEN


def main():
    # # Regenerate file from the database
    utility_and_filters.generate_frequency_list_file()

    wk_handler = WaniKaniHandler(WANIKANI_API_TOKEN)
    # wk_handler.download_all_data()
    # wk_handler.write_cache()

    words_list = utility_and_filters.get_common_words_list(1000)
    print("Generated initial words list of [%d]:\n" % len(words_list) + str(words_list))
    words_list = utility_and_filters.filter_out_unknown_kanji(words_list, wk_handler, invert_filter=False)
    print("Filtered out unknown kanji down to [%d]:\n" % len(words_list) + str(words_list))
    words_list = utility_and_filters.filter_out_known_words(words_list, wk_handler, invert_filter=False)
    print("Filtered out known words down to [%d]:\n" % len(words_list) + str(words_list))


if __name__ == "__main__":
    main()
