import io
import os
from collections import namedtuple
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import secrets

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/youtube.force-ssl"]

File = namedtuple("File", ["Path", "Type", "Language", "Content"])


class FileHandler:
    directory = None
    files = []

    def get_input_directory(self):
        self.directory = input("Enter full path of directory, of files, which need to be uploaded to Youtube: ")

    def load_files(self):
        files = os.listdir(self.directory)
        for file in files:
            if "caption" in file:
                file_type = "caption"
            elif "description" in file:
                file_type = "description"
            else:
                continue

            if "DE." in file:
                language = "de"
            elif "FR." in file:
                language = "fr"
            else:
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

    def __authorize(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Get credentials and create an API client
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRETS_FILE, SCOPES, state="state")
            credentials = flow.run_local_server()
        except Exception:
            raise "Error - All requested permissions are necessary for the script to run"

        self.youtube = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)

    def __caption_exists(self, language):
        if input("Some captions already exist. Replace existing? <Y/N>: ") == "Y":
            self.replace_existing = True
        else:
            self.replace_existing = False

    def upload(self, file):

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
                return

        body = {
            "snippet": {
                "language": file.Language,
                "name": "Captions",
                "videoId": self.video_id,
                "isDraft": False
            }
        }
        self.youtube.captions().insert(
            part="snippet",
            body=body,
            media_body=text_file
        ).execute()


def main():
    file_handler = FileHandler()
    file_handler.get_input_directory()
    file_handler.load_files()

    youtube_uploader = YoutubeUploader()

    for file in file_handler.files:

        print("Processing file type: " + file.Type + " with language: " + file.Language)

        youtube_uploader.upload(file)


if __name__ == "__main__":
    main()
