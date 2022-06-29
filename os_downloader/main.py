#!/usr/bin/env python3
import requests
import argparse
import os

OPENSUBTITLES_API_ADDRESS = "https://api.opensubtitles.com"
if "OPENSUBTITLES_API_KEY" in os.environ:
    OPENSUBTITLES_API_KEY = os.getenv("OPENSUBTITLES_API_KEY")
else:
    HOMEDIR =  os.path.join(os.getenv("HOME"), ".os-downloader")
    f = open(HOMEDIR, "r")
    OPENSUBTITLES_API_KEY = f.read().rstrip("\n")
    
parser = argparse.ArgumentParser("OpenSubtitles Downloader")
parser.add_argument("filename", help="The file which you wanna download subtitles")
parser.add_argument("--language", default="pt-BR", help="Language")
parser.add_argument("--version", action="version", version='%(prog)s v0.0.1')
arguments = parser.parse_args()


def guess_by_filename(filename: str):
    headers = {
        "Content-Type": "application/json",
        "Api-Key": OPENSUBTITLES_API_KEY
    }
    params = {
        "filename": filename
    }
    res = requests.get(f"{OPENSUBTITLES_API_ADDRESS}/api/v1/utilities/guessit", headers=headers, params=params)
    res.raise_for_status()
    video_data = res.json()
    return video_data


def search_for_subtitles(languages:str, query:str, type:str, season_number:int = None, episode_number:int = None) -> list:
    headers = {
        "Content-Type": "application/json", 
        "Api-Key": OPENSUBTITLES_API_KEY
    }
    params = {
        "query": query,
        "languages": languages,
        "type": type
    }

    for k, v in {"season_number": season_number, "episode_number": episode_number}.items():
        if v is not None:
            params[k] = v

    res = requests.get(f"{OPENSUBTITLES_API_ADDRESS}/api/v1/subtitles", headers=headers, params=params)
    res.raise_for_status()
    json_data = res.json()
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
    json_data = res.json()
    return json_data["link"]


def download_subtitle(download_link: str):
    filename = download_link.split("/")[-1]
    absolute_path = os.path.abspath(os.path.curdir)
    subtitle_file = open(os.path.join(absolute_path, filename), "wb")
    res = requests.get(download_link)
    res.raise_for_status()

    for chunk in res.iter_content(100000):
        subtitle_file.write(chunk)

    subtitle_file.close()


def main():
    video_data = guess_by_filename(arguments.filename)

    if video_data["type"] == "episode":
        file_ids = search_for_subtitles(languages=arguments.language, query=video_data["title"], type=video_data["type"], season_number=video_data["season"], episode_number=video_data["episode"])
    else:
        file_ids = search_for_subtitles(languages=arguments.language, query=video_data["title"], type="all")

    for i in file_ids:
        download_link = get_download_link(file_id=i)
        download_subtitle(download_link=download_link)

if __name__ == '__main__':
    main()