# YouTube translator

The purpose of this project is to utilize DeepL for translating YouTube captions and descriptions.  
It consists of two scripts:
1. translate.py: Translates captions or description files with DeepL
2. upload.py: Uploads the translated files to YouTube

## Prerequisites

Latest version of [Python](https://www.python.org/downloads/) installed

## Installation

Navigate to the project folder and install the dependencies:
```
$ cd /path/to/project-folder
$ pip install -r requirements.txt
```

## Usage

### Translate
To translate caption or description files, run the translate.py script and follow the instructions displayed on the screen:
```
$ cd /path/to/project-folder 
$ py .\translate.py
```
File names need to contain one of the following words in it to identity the type:
* caption
* description
* title

### Upload
To upload caption or description files, run the upload.py script and follow the instructions displayed on the screen:
```
$ cd /path/to/project-folder 
$ py .\upload.py
```
File names need to contain one of the languages from the config file at the end of the name (automatically added in translate script)

### Changing languages

You can add or remove languages from in the config.ini file