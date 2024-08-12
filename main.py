from waniwords_utility import get_api_keys, generate_frequent_words, generate_frequency_list_file
from wanikani import WaniKaniHandler
from jpdb import JPDBHandler


def main():

    api_keys = get_api_keys()
    wk_handler = WaniKaniHandler(api_keys["wanikani"])
    jpdb_handler = JPDBHandler(api_keys["jpdb"])

    # print("Generating Frequency List file from database...")
    # generate_frequency_list_file()  # Regenerate file from the database
    print("Downloading WaniKani user data...")
    wk_handler.download_all_data()  # Download data from wanikani and write to cache file

    NUM_OF_WORDS = 1000
    print("Generating word list of size %d..." % NUM_OF_WORDS)
    words_list = generate_frequent_words(NUM_OF_WORDS)

    # print("Filtering out kana-only words...", end="\t") TODO: Add kana filter function
    # words_list = filter_out_unknown_symbols(words_list, None, invert_filter=True)
    # print(len(words_list), "words remaining.")

    print("Filtering out unkown kanji...", end="\t")
    words_list = wk_handler.filter_out_unknown_kanji(words_list)
    print(len(words_list), "words remaining.")

    print("Filtering out known words... ", end="\t")
    words_list = wk_handler.filter_out_known_words(words_list)
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
