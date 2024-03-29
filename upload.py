import configparser
import io
import os
from collections import namedtuple
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import secrets

languages = {}

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

File = namedtuple("File", ["Path", "Type", "Language", "Content"])


class FileHandler:
    directory = None
    files = []

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        if "LANGUAGES" in config:
            for key, value in config["LANGUAGES"].items():
                languages[key] = value

    def read_input_directory(self):
        directory = input("Enter full path of directory, of files, to be uploaded to YouTube: ")
        directory = directory.strip("\"")   # remove double quotes
        if self.__check_input_directory_validity(directory):
            self.directory = directory
            return True
        else:
            return False

    @staticmethod
    def __check_input_directory_validity(directory):
        try:
            files = os.listdir(directory)
        except (FileNotFoundError, OSError):
            print("Error - Directory not found: '" + directory + "'")
            return False

        if files is None:
            print("Error - No files found in directory '" + directory + "'")
            return False

        return True

    def load_files(self):
        files = os.listdir(self.directory)
        for file in files:
            print(file)
            if "caption" in file.lower():
                file_type = "caption"
            elif "description" in file.lower():
                file_type = "description"
            elif "title" in file.lower():
                file_type = "title"
            else:
                print("Skipped - Invalid file type of file: '" + file.Path + "' - must contain one of the following: 'caption', 'description', 'title'\n")
                continue

            language = None
            for key, value in languages.items():
                if key.upper() + "." in file:
                    language = value
                    break
            if language is None:
                print("Skipped - File '" + file + "' has no valid language in name\n")
                continue

            path = self.directory + "\\" + file
            source_file = io.open(path, mode="r", encoding="utf-8")
            content = source_file.read()

            if file_type == "title" and len(content) > 100:
                raise ContentLengthException("Error - File '" + file + "' of type: '" + file_type + "' has a too many characters (" + str(len(content)) + ") - Limit is 100")

            if len(content) == 0:
                raise ContentLengthException("Error - File '" + file + "' of type: '" + file_type + "' is empty")

            new_file = File(path, file_type, language, content)
            self.files.append(new_file)


class ContentLengthException(Exception):
    pass


class YoutubeUploader:
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    CLIENT_SECRETS_FILE = "client_secret_543192577520-fkgb1khncn9vmm61t3dnld1rr54pgq1t.apps.googleusercontent.com.json"

    state = None
    video_id = None
    youtube = None
    replace_existing_captions = None
    caption_list = None
    descriptions = {}

    def __init__(self):
        self.state = secrets.token_urlsafe(16)
        self.__authorize()
        valid_video_id = False
        while not valid_video_id:
            valid_video_id = self.__get_input_video_id()
            print()
        self.__generate_caption_list()

    def __generate_caption_list(self):
        self.caption_list = self.youtube.captions().list(
            part="snippet",
            videoId=self.video_id
        ).execute()

    def __get_input_video_id(self):
        video_id = input("Enter YouTube video ID: ")
        if self.__check_video_id_validity(video_id):
            self.video_id = video_id
            return True
        else:
            return False

    def __check_video_id_validity(self, video_id):
        # Check if the video exists
        response = self.youtube.videos().list(part="id", id=video_id).execute()
        if not response.get("items"):
            print("Error - YouTube Video with video ID '" + video_id + "' not found")
            return False

        # Check if the user has modifying rights
        # noinspection PyBroadException
        try:
            response = self.youtube.videos().update(
                part="snippet",
                body={
                    "id": video_id
                }
            ).execute()
        except Exception:
            print("Error - You do not have editing permissions on video ID '" + video_id + "'")
            return False

        return True

    def __authorize(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Get credentials and create an API client
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRETS_FILE, SCOPES, state="state")
            credentials = flow.run_local_server()
        except Exception:
            raise PermissionDeniedException

        self.youtube = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
        print()

    def __caption_exists(self):
        if input("Some captions already exist. Replace existing? <Y/N>: ") == "Y":
            self.replace_existing_captions = True
        else:
            self.replace_existing_captions = False
        print()

    def upload_caption(self, file):
        text_file = MediaFileUpload(file.Path)

        for caption in self.caption_list["items"]:
            if file.Language == caption["snippet"]["language"]:
                if self.replace_existing_captions is None:
                    self.__caption_exists()
                if self.replace_existing_captions:
                    self.youtube.captions().update(
                        part="id",
                        body={"id": caption["id"]},
                        media_body=text_file
                    ).execute()
                    return True
                return False

        body = {
            "snippet": {
                "language": file.Language,
                "name": "",
                "videoId": self.video_id,
                "isDraft": False
            }
        }
        self.youtube.captions().insert(
            part="snippet",
            body=body,
            media_body=text_file
        ).execute()
        return True

    def prepare_description_upload(self, file):
        if file.Language in self.descriptions:
            if self.descriptions[file.Language] is not None:
                self.descriptions[file.Language].update({
                    "description": file.Content
                })
        else:
            self.descriptions[file.Language] = {
                "description": file.Content
            }
        return True

    def prepare_title_upload(self, file):
        if file.Language in self.descriptions:
            if self.descriptions[file.Language] is not None:
                self.descriptions[file.Language].update({
                    "title": file.Content
                })
        else:
            self.descriptions[file.Language] = {
                "title": file.Content
            }
        return True

    def __fill_title_and_descriptions(self):
        request = self.youtube.videos().list(
            part="localizations",
            id=self.video_id
        )
        response = request.execute()

        localizations = response["items"][0]["localizations"]

        for language, description in self.descriptions.items():
            if language in localizations:

                # Use description from YouTube if it doesn't exist in files
                if "description" not in description:
                    description["description"] = localizations[language]["description"]

                # Use description from YouTube if user wants to keep it
                elif localizations[language]["description"] != description["description"] and localizations[language]["description"] != "Description":
                    if input("Video description of language '" + language + "' already exist. Replace existing? <Y/N>: ") == "N":
                        description["description"] = localizations[language]["description"]

                # Use description from YouTube if it doesn't exist in files
                if "title" not in description:
                    description["title"] = localizations[language]["title"]

                # Use title from YouTube if user wants to keep it
                if localizations[language]["title"] != description["title"] and localizations[language]["title"] != "Title":
                    if input("Video title of language '" + language + "' already exist. Replace existing? <Y/N>: ") == "N":
                        description["title"] = localizations[language]["title"]

            else:
                # Set default values if no other exists
                if "description" not in description:
                    description["description"] = "Description"
                if "title" not in description:
                    description["title"] = "Title"

        #  Fill in missing languages to not delete them when doing the update API request
        for language, localization in localizations.items():
            if language not in self.descriptions:
                self.descriptions[language] = {
                    "description": localization["description"],
                    "title": localization["title"]
                }

    def upload_titles_and_descriptions(self):
        self.__fill_title_and_descriptions()
        if not self.descriptions:
            return False
        body = {
            "id": self.video_id,
            "localizations": self.descriptions
        }
        self.youtube.videos().update(
            part="localizations",
            body=body,
        ).execute()
        return True


class PermissionDeniedException(Exception):
    """Error - All requested permissions are necessary for the script to run"""


def main():
    file_handler = FileHandler()
    valid_directory = False
    while not valid_directory:
        valid_directory = file_handler.read_input_directory()
        print()
    file_handler.load_files()

    youtube_uploader = YoutubeUploader()

    for file in file_handler.files:
        prepared = None
        uploaded = None

        print("Processing - File of type: '" + file.Type + "' and language: '" + file.Language + "'")

        if file.Type == "caption":
            uploaded = youtube_uploader.upload_caption(file)
        elif file.Type == "description":
            prepared = youtube_uploader.prepare_description_upload(file)
        elif file.Type == "title":
            prepared = youtube_uploader.prepare_title_upload(file)

        if uploaded:
            print("Successfully uploaded - File of type: '" + file.Type + "' and language: '" + file.Language + "'")
        elif uploaded is False:
            print("Skipped - File of type: '" + file.Type + "' and language: '" + file.Language + "'")

        if prepared:
            print("Prepared for upload - File of type: '" + file.Type + "' and language: '" + file.Language + "'")

        print()

    uploaded = youtube_uploader.upload_titles_and_descriptions()
    if uploaded:
        print("Successfully uploaded - Description files")


if __name__ == "__main__":
    main()
