import utility_and_filters
from wanikani import WaniKaniHandler
from jpdb import JPDBHandler
from config import WANIKANI_API_TOKEN, JPDB_API_TOKEN


def main():
    wk_handler = WaniKaniHandler(WANIKANI_API_TOKEN)
    jpdb_handler = JPDBHandler(JPDB_API_TOKEN)
    # print("Generating Frequency List file from database...")
    # utility_and_filters.generate_frequency_list_file()  # Regenerate file from the database
    # print("Downloading WaniKani user data...")
    # wk_handler.download_all_data()  # Download data from wanikani and write to cache file

    NUM_OF_WORDS = 500
    print("Generating word list of size %d..." % NUM_OF_WORDS)
    words_list = utility_and_filters.generate_frequent_words(NUM_OF_WORDS)

    print("Filtering out unkown kanji...", end="\t")
    words_list = utility_and_filters.filter_out_unknown_kanji(words_list, wk_handler)
    print(len(words_list), "words remaining.")

    print("Filtering out known words... ", end="\t")
    words_list = utility_and_filters.filter_out_known_words(words_list, wk_handler)
    print(len(words_list), "words remaining.")

    print("Generated list:")
    for word in words_list:
        print(word, end=" ")
    print()

    print("Adding words to JPDB deck...")
    jpdb_handler.add_vocabulary_to_waniwords_deck(words_list)

    print("Finished!")


if __name__ == "__main__":
    main()
