import configparser
import os
import io
import requests
import json
import codecs
import re

languages = []


class FileHandler:
    directory = ""
    file_name = ""
    file_extension = ""
    text = ""
    end_translation_character = ""

    def read_config_file(self):
        config = configparser.ConfigParser()
        config.read("config.ini", encoding="utf-8")
        for language in config["LANGUAGES"]:
            languages.append(language)
        self.end_translation_character = config.get("PROPERTIES", "end_translation_character")

    def get_input_text(self):
        source_file_string = input("Enter full path of file, which needs to be translated: ")
        source_file_string = source_file_string.strip("\"")  # remove double quotes
        self.directory = os.path.dirname(source_file_string)
        self.file_name = os.path.splitext(source_file_string)[0]
        self.file_extension = os.path.splitext(source_file_string)[1]

        try:
            source_file = io.open(source_file_string, mode="r", encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError("Error - File not found: '" + source_file_string + "'")
        except PermissionError:
            raise PermissionError("Error - Not a file or no permission: '" + source_file_string + "'")
        self.text = source_file.read()

    def write_to_file(self, text, language):
        translated_file_path = self.file_name + language.upper() + ".txt"
        if os.path.exists(translated_file_path):
            os.remove(translated_file_path)
        translated_file = codecs.open(translated_file_path, "w", "utf-8")
        translated_file.write(text)
        translated_file.close()



class Translator:
    url = "https://api-free.deepl.com/v2/translate"
    auth_key = "8ce20a2c-0e86-4bba-6773-3be52ea7416e:fx"
    end_translation_character = ""
    music_content = ""

    def __init__(self, end_translation_character):
        self.end_translation_character = end_translation_character

    def extract_music_text(self, text):
        # Don't translate music information (description)
        self.music_content = text.partition(self.end_translation_character)[1] + text.partition(self.end_translation_character)[2]

    def format_input_text(self, text):
        # Don't translate music information (description)
        text = text.partition(self.end_translation_character)[0]

        # Remove line breaks within sentences (translation)
        timestamp_regex = "0:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9],0:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]"
        timestamp_location = re.search(timestamp_regex, text)
        if timestamp_location:
            # Remove all new lines and replace with empty string
            text = text.replace("\n", " ")
            # Add back new line after each timestamp
            text = re.sub(r"(" + timestamp_regex + " " + ")(.)", r"\1\n\2", text)
            # Add back two new lines before each timestamp
            text = re.sub(r"(" + timestamp_regex + " " + ")", r"\n\n\1", text)
            text = text.lstrip("\n")

        return text

    def translate_to_language(self, text, language):
        data = {
            "auth_key": self.auth_key,
            "formality": "prefer_less",
            "target_lang": language,
            "text": text
        }
        request = requests.post(url=self.url, data=data)
        translation = json.loads(request.text)["translations"][0]["text"]

        return translation

    def format_translated_text(self, text, language):
        # No SS!
        if language == "de":
            text = text.replace("ß", "ss")

        # Append music information after translating (description)
        text = text + self.music_content

        return text


def main():
    file_handler = FileHandler()
    file_handler.read_config_file()
    file_handler.get_input_text()

    translator = Translator(file_handler.end_translation_character)
    translator.extract_music_text(file_handler.text)
    formatted_text = translator.format_input_text(file_handler.text)

    print(formatted_text)

    for language in languages:
        print("Translating - language: '" + language + "'")

        translated_text = translator.translate_to_language(formatted_text, language)
        translated_text = translator.format_translated_text(translated_text, language)

        print("Writing to file - language: '" + language + "'")

        file_handler.write_to_file(translated_text, language)

        print("Finished - language: '" + language + "'\n")


if __name__ == "__main__":
    main()
