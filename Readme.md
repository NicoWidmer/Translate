# YouTube translator

The purpose of this project is to utilize DeepL for translating YouTube captions and descriptions.  
The project contains two scripts:
1. translate.py: Translates text files with DeepL
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
$ py translate.py
```
Note: File names should contain one of the following words to identify the type for uploading:
* caption
* description
* title

### Upload
To upload caption or description files, run the upload.py script and follow the instructions displayed on the screen:
```
$ cd /path/to/project-folder 
$ py upload.py
```
Note: File names should contain one of the languages from the `config.ini` file at the end of the name (automatically added in the `translate.py` script). Additionally, file names should contain one of the following words to identify the type for uploading:
* caption
* description
* title

Captions, descriptions and titles can be uploaded together from the same folder or separately.

## Configuration

### Changing languages
You can add or remove languages in the config.ini file

### Changing End Translation Symbol
The script only translates up to the end_translation_character set in the config.ini file

## Unit Tests
To run the unit tests, navigate to the tests folder and run pytest:
```
$ cd /path/to/project-folder/tests
$ pytest
```
