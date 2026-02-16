# newgrounds-tools

### Overview

NGArtist2json.py
```
usage: NGArtist2json.py [-h] [-jl JL] [-hl HL] [-m M] [-ad AD]

Tool to extract metadata from Newgrounds audio artist pages.

options:
  -h, --help            show this help message and exit
  -jl, -json-file-list JL
                        Write generated Newgrounds JSON paths to the givien file.
  -hl, -html-file-list HL
                        List of HTML file paths in a file to process.
  -m, -move-html M      Move HTML files to a location.
  -ad AD                test.
```
NGAudioTagger.py
```
usage: NGAudioTagger.py [-h] [-f] [-jl JSON_FILE_LIST] [-a JSON_FILE] [-ngapl AUDIO_FILE_LIST]

Tool to bulk edit Newgrounds audio's tags.

options:
  -h, --help            show this help message and exit
  -f, -fuzzy-match      Enable fuzzy match. Allow matching audio files using "^(\d+)_.+" pattern.
  -jl, -json-list-file JSON_FILE_LIST
                        Read Newgrounds json paths from the givien file.
  -a, -alias-json JSON_FILE
                        Specifie the json file that storage artists' alias names.
  -ngapl AUDIO_FILE_LIST
                        Specifie the file stores audio file list to process. Items are separated with new line in the
                        list

example:
    normal:
    python3 NGAudioTagger.py -jl JSON_FILE_LIST -ngapl AUDIO_FILE_LIST
    fuzzy:
    python3 NGAudioTagger.py -f -jl JSON_FILE_LIST -ngapl AUDIO_FILE_LIST
```
checkAudioExist.py
```
usage: checkAudioExist.py [-h] [-ef EF] [-ad AD]

Tool to check if Newgrounds audio files extracted from a file contains their urls exist.

options:
  -h, --help  show this help message and exit
  -ef EF      Specifies the file to extract Newgrounds audio urls.
  -ad AD      Specifies the directory to match mp3 files.
```
### Known Issues

NGAudioTagger.py

Custom tags in mp3 may duplicate

