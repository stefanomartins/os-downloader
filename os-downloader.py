import requests
import json
import argparse
import os

OPENSUBTITLES_API_ADDRESS = "https://api.opensubtitles.com"
OPENSUBTITLES_API_KEY = os.getenv("OPENSUBTITLES_API_KEY")

parser = argparse.ArgumentParser("OpenSubtitles Downloader")
parser.add_argument("filename", help="The file which you wanna download subtitles")
parser.add_argument("--language", default="pt-BR", help="Language")
arguments = parser.parse_args()

def search_for_subtitles(languages: str, query: str) -> list:
    headers = {
        "Content-Type": "application/json", 
        "Api-Key": OPENSUBTITLES_API_KEY
    }
    params = {
        "query": query,
        "languages": languages
    }
    res = requests.get(f"{OPENSUBTITLES_API_ADDRESS}/api/v1/subtitles", headers=headers, params=params)
    res.raise_for_status()
    json_data = json.loads(res.text)
    file_ids = []

    for i in json_data["data"]:
        file_ids.append(i["attributes"]["files"][0]["file_id"])

    return file_ids


def get_download_link(file_id: int) -> list:
    headers = {
        "Content-Type": "application/json",
        "Api-Key": OPENSUBTITLES_API_KEY
    }
    data = {
        "file_id": file_id
    }
    res = requests.post(f"{OPENSUBTITLES_API_ADDRESS}/api/v1/download", headers=headers, params=data)
    res.raise_for_status()
    
    json_data = json.loads(res.text)
    return json_data["link"]


def download_subtitle(download_link: str):
    filename = download_link.split("/")[-1]
    subtitle_file = open(filename, "wb")
    res = requests.get(download_link)
    res.raise_for_status()

    for chunk in res.iter_content(100000):
        subtitle_file.write(chunk)

    subtitle_file.close()


def main():
    file_ids = search_for_subtitles(languages=arguments.language, query=arguments.filename)

    for i in file_ids:
        download_link = get_download_link(file_id=i)
        download_subtitle(download_link=download_link)

if __name__ == '__main__':
    main()