from waniwords_utility import get_api_keys, generate_frequent_words, generate_frequency_list_file
from wanikani import WaniKaniHandler
from jpdb import JPDBHandler
from tkinter import *
from tkinter import ttk


def main():
    def generate_button_function():
        wk_handler = WaniKaniHandler(api_keys["wanikani"])
        jpdb_handler = JPDBHandler(api_keys["jpdb"])
        
        # print("Generating Frequency List file from database...")
        # generate_frequency_list_file()  # Regenerate file from the database
        print("Downloading WaniKani user data...")
        wk_handler.download_all_data()  # Download data from wanikani and write to cache file

        words_list = generate_frequent_words(wordcount_int.get())

        if checkbox_variable_list[0].get() == True:
            print("Filtering out known words... ", end="\t")
            words_list = wk_handler.filter_out_known_words(words_list)
            print(len(words_list), "words remaining.")

        if checkbox_variable_list[1].get() == True:
            print("Filtering out unkown kanji...", end="\t")
            words_list = wk_handler.filter_out_unknown_kanji(words_list)
            print(len(words_list), "words remaining.")

        if checkbox_variable_list[2].get() == True:
            print("Filtering out kana-only words...", end="\t")
            # TODO: implement function
            # words_list = filter_out_kana_words(words_list)
            print(len(words_list), "words remaining.")

        print("Generated list:")
        for word in words_list:
            print(word, end=" ")
        print()

        # print("Adding words to JPDB deck...")
        # jpdb_handler.add_vocabulary_to_waniwords_deck(words_list)

        print("Finished!")


    api_keys = get_api_keys()


    # Window
    window = Tk()
    window.title("WaniWords")
    window.geometry("500x500")


    # API Key widgets
    ttk.Label(master=window, text="API Keys", font="Calibri 30 bold").pack()

    wk_key_frame = ttk.Frame(master=window)
    wk_key_string = StringVar(value=api_keys["wanikani"])
    ttk.Label(master=wk_key_frame, text="WaniKani", font="Calibri 15").pack(side="left", padx=5)
    ttk.Entry(master=wk_key_frame, textvariable=wk_key_string).pack(side="left")
    wk_key_frame.pack(pady=5)

    jpdb_key_frame = ttk.Frame(master=window)
    jpdb_key_string = StringVar(value=api_keys["jpdb"])
    ttk.Label(master=jpdb_key_frame, text="JPDB", font="Calibri 15").pack(side="left", padx=5)
    ttk.Entry(master=jpdb_key_frame, textvariable=jpdb_key_string).pack(side="left")
    jpdb_key_frame.pack()


    # Options widgets
    ttk.Label(master=window, text="Filters", font="Calibri 30 bold").pack(pady=5)

    wordcount_frame = ttk.Frame(master=window)
    wordcount_int = IntVar(value=1000)
    ttk.Label(master=wordcount_frame, text="Words up to frequency", font="Calibri 15").pack(side="left", padx=5)
    ttk.Entry(master=wordcount_frame, textvariable=wordcount_int).pack(side="left")
    wordcount_frame.pack()

    checkbox_label_list = [
        "Remove WaniKani learned vocab",
        "Remove vocab with unknown kanji",
        "Remove kana-only vocab"
    ]
    checkbox_variable_list = []
    for checkbox_label in checkbox_label_list:
        checkbox_variable_list.append(BooleanVar(value=False))
        ttk.Checkbutton(master=window, text=checkbox_label, variable=checkbox_variable_list[-1]).pack()
    
    ttk.Button(master=window, text="Generate", command=generate_button_function).pack(pady=30)


    # Run
    window.mainloop()


if __name__ == "__main__":
    main()
