
# WaniWords

This project is designed for WaniKani users to maximize their kanji learning by discovering commonly used words that WaniKani doesn't cover. Often, WaniKani introduces a kanji with only a few associated words, leaving gaps in vocabulary. This project identifies commonly used words made up of kanji the user already knows, providing a list of easily learnable, high-value words. This way, users can efficiently expand their vocabulary by focusing on these "low-hanging fruit."
## Features

- GUI!
- Locally cache user's API Keys and WaniKani user data for repeated use
- Create lists of words, filtered with various criteria
    - Database is sourced from [tsukubawebcorpus](https://tsukubawebcorpus.jp/en/) and [NINJAL](https://repository.ninjal.ac.jp/records/3234)
- Generate a vocabulary deck on jpdb.io for studying

## How To Use

- Requirements: requests (install using "pip install requests")
- Download source code and run main.py ("python3 main.py")
- Enter API Keys for WaniKani (User Icon -> API Tokens) and JPDB (Settings -> Account information)
- Customize and generate a study deck!
