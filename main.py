import os
import io
import requests
import json
import codecs
import re

file_name = ""


def get_input_text():
    source_file_string = input("Enter full path of file, which needs to be translated: ")
    # directory = os.path.dirname(source_file_string)
    global file_name
    file_name = os.path.splitext(source_file_string)[0]
    # file_extension = os.path.splitext(source_file_string)[1]

    source_file = io.open(source_file_string, mode="r", encoding="utf-8")
    source_content = source_file.read()

    return source_content


class Translator:
    music_content = ""

    def extract_music_text(self, text):
        # Don't translate music information (description)
        self.music_content = text.partition("🎵")[1] + text.partition("🎵")[2]

    def format_input_text(self, text):
        # Don't translate music information (description)
        text = text.partition("🎵")[0]

        # Remove line breaks within sentences (translation)
        timestamp_regex = "0:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9],0:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]"
        timestamp_location = re.search(timestamp_regex, text)
        if timestamp_location:
            print(timestamp_location)
            text = text.replace("\n", " ")  # Remove all new lines and replace with empty string
            text = re.sub(r"(" + timestamp_regex + " " + ")(.)", r"\1\n\2",
                          text)  # Add back new line after each timestamp
            text = re.sub(r"(" + timestamp_regex + " " + ")", r"\n\n\1",
                          text)  # Add back two new lines before each timestamp
            text = text.lstrip("\n")

        return text

    def translate_to_language(self, text, language):
        url = "https://api-free.deepl.com/v2/translate"
        auth_key = "8ce20a2c-0e86-4bba-6773-3be52ea7416e:fx"
        if language == "JA" or language == "TR" or language == "ZH":
            data = {
                "auth_key": auth_key,
                "target_lang": language,
                "text": text
            }
        else:
            data = {
                "auth_key": auth_key,
                "formality": "less",
                "target_lang": language,
                "text": text
            }
        request = requests.post(url=url, data=data)
        translation = json.loads(request.text)["translations"][0]["text"]

        return translation

    def format_translated_text(self, text, language):
        # No SS!
        if language == "DE":
            text = text.replace("ß", "ss")

        # Append music information after translating (description)
        text = text + self.music_content

        return text

    def write_to_file(self, text, language):
        translated_file_path = file_name + language + ".txt"
        if os.path.exists(translated_file_path):
            os.remove(translated_file_path)
        translated_file = codecs.open(translated_file_path, "w", "utf-8")
        translated_file.write(text)
        translated_file.close()


def main():
    translator = Translator()
    unformatted_text = get_input_text()
    translator.extract_music_text(unformatted_text)
    formatted_text = translator.format_input_text(unformatted_text)
    print(formatted_text)

    languages = ["DE", "ES", "FR", "IT", "JA", "PT-BR", "TR", "ZH"]
    for language in languages:
        translated_text = translator.translate_to_language(formatted_text, language)
        translated_text = translator.format_translated_text(translated_text, language)

        print(translated_text)

        translator.write_to_file(translated_text, language)




if __name__ == "__main__":
    main()
