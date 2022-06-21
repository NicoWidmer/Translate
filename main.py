import os
import io
import requests
import json
import codecs
import re

source_file_string = input("Enter full path of file, which needs to be translated: ")
# directory = os.path.dirname(source_file_string)
file_name = os.path.splitext(source_file_string)[0]
#file_extension = os.path.splitext(source_file_string)[1]

source_file = io.open(source_file_string, mode="r", encoding="utf-8")
source_content = source_file.read()

# Don't translate music information (description)
content = source_content.partition("🎵")[0]
music_content = source_content.partition("🎵")[1] + source_content.partition("🎵")[2]

#print(content)

# Remove line breaks within sentences (translation)
timestamp_regex = "0:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9],0:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]"
timestamp_location = re.search(timestamp_regex, content)
if timestamp_location:
    print(timestamp_location)
    content = content.replace("\n", " ")      # Remove all new lines and replace with empty string
    content = re.sub(r"(" + timestamp_regex + " " + ")(.)", r"\1\n\2", content)   # Add back new line after each timestamp
    content = re.sub(r"(" + timestamp_regex + " " + ")", r"\n\n\1", content)      # Add back two new lines before each timestamp
    content = content.lstrip("\n")

print(content)

url = "https://api-free.Translate.com/v2/translate"
auth_key = "8ce20a2c-0e86-4bba-6773-3be52ea7416e:fx"

languages = ["DE", "ES", "FR", "IT", "JA", "PT-BR", "TR"]
for language in languages:
    if language == "JA" or language == "TR":
        data = {
            "auth_key": auth_key,
            "target_lang": language,
            "text": content
        }
    else:
        data = {
            "auth_key": auth_key,
            "formality": "less",
            "target_lang": language,
            "text": content
        }

    request = requests.post(url=url, data=data)
    translation = json.loads(request.text)["translations"][0]["text"]

    # No SS!
    if language == "DE":
        translation = translation.replace("ß", "ss")

    # Append music information after translating (description)
    translation = translation + music_content

    print(translation)

    translated_file_path = file_name + language + ".txt"
    if os.path.exists(translated_file_path):
        os.remove(translated_file_path)
    translated_file = codecs.open(translated_file_path, "w", "utf-8")
    translated_file.write(translation)
    translated_file.close()
