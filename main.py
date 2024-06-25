import utility_and_filters
from wanikani import WaniKaniHandler
from jpdb import JPDBHandler
from config import WANIKANI_API_TOKEN, JPDB_API_TOKEN


def main():
    wk_handler = WaniKaniHandler(WANIKANI_API_TOKEN)
    jpdb_handler = JPDBHandler(JPDB_API_TOKEN)

    # utility_and_filters.generate_frequency_list_file()  # Regenerate file from the database
    # wk_handler.download_all_data()  # Download data from wanikani and write to cache file

    words_list = utility_and_filters.get_common_words_list(1000)
    words_list = utility_and_filters.filter_out_unknown_kanji(words_list, wk_handler)
    words_list = utility_and_filters.filter_out_known_words(words_list, wk_handler)
    print("Filtered out known words down to [%d]:\n" % len(words_list) + str(words_list))

    jpdb_handler.add_vocabulary_to_waniwords_deck(words_list)


if __name__ == "__main__":
    main()
