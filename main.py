from waniwords_utility import read_config_file, write_config_file, generate_frequent_words, generate_frequency_list_file, get_time
from wanikani import WaniKaniHandler
from jpdb import JPDBHandler
from tkinter import *
from tkinter import ttk


def main():

    api_keys = read_config_file()
    starting_values = {
        "wanikani_api_key": api_keys["wanikani"],
        "jpdb_api_key": api_keys["jpdb"],
        "word_count": 1000,
        "checkbox_values": [
            True, 
            True, 
            True
        ],
        "checkbox_labels": [
            "Remove WaniKani learned vocab",
            "Remove vocab with unknown kanji",
            "Remove kana-only vocab"
        ],
        "deck_name": "WaniWords",
        "status": "Input both API Keys to begin!"
    }

    def generate_button_function():
        write_config_file({
            "wanikani": wk_key_string.get(),
            "jpdb": jpdb_key_string.get()
        })

        wk_handler = WaniKaniHandler(wk_key_string.get())
        jpdb_handler = JPDBHandler(jpdb_key_string.get())
        
        # print("Generating Frequency List file from database...")
        # generate_frequency_list_file()  # Regenerate file from the database
        try:
            wk_handler.download_all_data()  # Download data from wanikani and write to cache file
        except KeyError as e:
            status_string.set(e.args[0])
            status_label.configure(foreground="#F00")
            return

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
            words_list = wk_handler.filter_out_kana_words(words_list)
            print(len(words_list), "words remaining.")

        print("Generated list:")
        for word in words_list:
            print(word, end="\t")
        print()

        print("Adding words to JPDB deck...")
        try:
            jpdb_handler.add_vocabulary_to_waniwords_deck(words_list, deck_name_string.get())
        except KeyError as e:
            status_string.set(e.args[0])
            status_label.configure(foreground="#F00")
            return
        print("Finished!")
        status_string.set("Finished! Generated JPDB deck of %d words to study!" % len(words_list))
        status_label.configure(foreground="")

    # Window
    window = Tk()
    window.title("WaniWords")
    window.geometry("500x400")

    # API Key widgets
    ttk.Label(master=window, text="API Keys", font="Calibri 30 bold").pack()

    wk_key_frame = ttk.Frame(master=window)
    wk_key_string = StringVar(value=starting_values["wanikani_api_key"])
    ttk.Label(master=wk_key_frame, text="WaniKani", font="Calibri 15").pack(side="left", padx=5)
    ttk.Entry(master=wk_key_frame, textvariable=wk_key_string).pack(side="left")
    wk_key_frame.pack(pady=5)

    jpdb_key_frame = ttk.Frame(master=window)
    jpdb_key_string = StringVar(value=starting_values["jpdb_api_key"])
    ttk.Label(master=jpdb_key_frame, text="JPDB", font="Calibri 15").pack(side="left", padx=5)
    ttk.Entry(master=jpdb_key_frame, textvariable=jpdb_key_string).pack(side="left")
    jpdb_key_frame.pack()

    # Options widgets
    ttk.Label(master=window, text="Filters", font="Calibri 30 bold").pack(pady=5)

    wordcount_frame = ttk.Frame(master=window)
    wordcount_int = IntVar(value=starting_values["word_count"])
    ttk.Label(master=wordcount_frame, text="Words up to frequency", font="Calibri 15").pack(side="left", padx=5)
    ttk.Entry(master=wordcount_frame, textvariable=wordcount_int).pack(side="left")
    wordcount_frame.pack()

    checkbox_variable_list = []
    checkbox_label_list = starting_values["checkbox_labels"]
    for i in range(len(checkbox_label_list)):
        checkbox_label = checkbox_label_list[i]
        checkbox_value = starting_values["checkbox_values"][i]
        checkbox_variable_list.append(BooleanVar(value=checkbox_value))
        ttk.Checkbutton(master=window, text=checkbox_label, variable=checkbox_variable_list[-1]).pack()
    
    deck_name_frame = ttk.Frame(master=window)
    deck_name_string = StringVar(value=starting_values["deck_name"])
    ttk.Label(master=deck_name_frame, text="Name of deck to generate", font="Calibri 15").pack(side="left", padx=5, pady=10)
    ttk.Entry(master=deck_name_frame, textvariable=deck_name_string).pack(side="left")
    deck_name_frame.pack()
    
    ttk.Button(master=window, text="Generate", command=generate_button_function).pack(pady=15)

    # Status widget
    status_string = StringVar(value=starting_values["status"])
    status_label = ttk.Label(master=window, textvariable=status_string)
    status_label.pack()

    # Run
    window.mainloop()

if __name__ == "__main__":
    main()
