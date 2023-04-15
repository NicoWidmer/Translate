import io
import os
from collections import namedtuple
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import secrets

'''
Add more entries to support additional languages to upload
Key: Language code in file name (DeepL language code)
Value: Youtube language code
'''
LANGUAGES = {
    "DE": "de",
    "ES": "es",
    "FR": "fr",
    "IT": "it",
    "JA": "ja",
    "PT-BR": "pt-Br",
    "TR": "tr",
    "ZH": "zh-Hans"
}

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

File = namedtuple("File", ["Path", "Type", "Language", "Content"])


class FileHandler:
    directory = None
    files = []

    def get_input_directory(self):
        self.directory = input("Enter full path of directory, of files, which need to be uploaded to Youtube: ")
        print()

    def load_files(self):
        files = os.listdir(self.directory)
        for file in files:
            if "caption" in file.lower():
                file_type = "caption"
            elif "description" in file.lower():
                file_type = "description"
            else:
                print("File '" + file + "' skipped because it has no type (caption or description) in name\n")
                continue

            language = None
            for key, value in LANGUAGES.items():
                if key + "." in file:
                    language = value
                    break
            if language is None:
                print("File '" + file + "' skipped because it has no valid language in name\n")
                continue

            path = self.directory + "\\" + file
            source_file = io.open(path, mode="r", encoding="utf-8")
            content = source_file.read()

            new_file = File(path, file_type, language, content)
            self.files.append(new_file)


class YoutubeUploader:
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    CLIENT_SECRETS_FILE = "client_secret_543192577520-fkgb1khncn9vmm61t3dnld1rr54pgq1t.apps.googleusercontent.com.json"

    state = None
    video_id = None
    youtube = None
    replace_existing = None
    caption_list = None
    descriptions = {}

    def __init__(self):
        self.state = secrets.token_urlsafe(16)
        self.__get_input_video_id()
        self.__authorize()
        self.__generate_caption_list()

    def __generate_caption_list(self):
        self.caption_list = self.youtube.captions().list(
            part="snippet",
            videoId=self.video_id
        ).execute()

    def __get_input_video_id(self):
        self.video_id = input("Enter Youtube video ID: ")
        print()

    def __authorize(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Get credentials and create an API client
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRETS_FILE, SCOPES, state="state")
            credentials = flow.run_local_server()
        except Exception:
            raise "Error - All requested permissions are necessary for the script to run"

        self.youtube = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
        print()

    def __caption_exists(self):
        if input("Some captions already exist. Replace existing? <Y/N>: ") == "Y":
            self.replace_existing = True
        else:
            self.replace_existing = False
        print()

    def upload_caption(self, file):
        text_file = MediaFileUpload(file.Path)

        for caption in self.caption_list["items"]:
            if file.Language == caption["snippet"]["language"]:
                if self.replace_existing is None:
                    self.__caption_exists(file.Language)
                if self.replace_existing:
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
        self.descriptions[file.Language] = {
            "title": "TITLE",
            "description": file.Content
        }
        return True

    def upload_descriptions(self):
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


def main():
    file_handler = FileHandler()
    file_handler.get_input_directory()
    file_handler.load_files()

    youtube_uploader = YoutubeUploader()

    for file in file_handler.files:
        uploaded = None
        prepared = None

        print("Processing file type: '" + file.Type + "' with language: '" + file.Language + "'")

        if file.Type == "caption":
            uploaded = youtube_uploader.upload_caption(file)
        elif file.Type == "description":
            prepared = youtube_uploader.prepare_description_upload(file)
        else:
            raise("Error - Invalid file type: '" + file.Type + "' of file: '" + file.Path + "'")

        if uploaded:
            print("File with type: '" + file.Type + "' and language: '" + file.Language + "' successfully uploaded")
        elif uploaded is False:
            print("File with type: '" + file.Type + "' and language: '" + file.Language + "' not uploaded")

        if prepared:
            print("File with type: '" + file.Type + "' and language: '" + file.Language + "' prepared for upload")

        print()

    uploaded = youtube_uploader.upload_descriptions()
    if uploaded:
        print("Description files successfully uploaded")


if __name__ == "__main__":
    main()
