# python-webcrawler

## Installation/How to Use
`$ pip install -r requirements.txt`

Rename `Config.py.example` to `Config.py` and enter the sites you want to search and the words/phrases you want to search for.

`$ python App.py`

Sites/pages you want to blacklist copy their directory structure from the `cache` directory to the `blacklist` directory (if you are concerned about space you can empty the file of it's contents, just don't delete it)

Pages that match the querys will be in the `matched` directory which is purged at the beginning of each run.
