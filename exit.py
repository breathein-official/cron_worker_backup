import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def get_youtube_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title="Test Upload", description="Uploaded via API", tags=None, categoryId="22"):
    youtube = get_youtube_service()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["motivation", "cronWorker"],
            "categoryId": categoryId
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media = MediaFileUpload(file_path, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )
    response = request.execute()
    print("✅ Video uploaded! Video ID:", response["id"])
    return response["id"]
