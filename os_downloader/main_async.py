import httpx
import os
import argparse
import asyncio
from __init__ import __version__

OPENSUBTITLES_API_ADDRESS = "https://api.opensubtitles.com"
if "OPENSUBTITLES_API_KEY" in os.environ:
    OPENSUBTITLES_API_KEY = os.getenv("OPENSUBTITLES_API_KEY")
else:
    f = open(os.path.expanduser("~/.os-downloader"))
    OPENSUBTITLES_API_KEY = f.read().rstrip("\n")

parser = argparse.ArgumentParser("OpenSubtitles Downloader")
parser.add_argument("filename", help="The file which you wanna download subtitles")
parser.add_argument("--language", default="pt-BR", help="Language")
parser.add_argument("--version", help="Print version")
arguments = parser.parse_args()


async def get_subtitles(filename: str, language: str = "pt-BR"):
    async with httpx.AsyncClient(base_url="https://api.opensubtitles.com") as client:
        # Primeira requisição
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"os-downloader {__version__}",
            "Api-Key": OPENSUBTITLES_API_KEY,
        }
        params = {"filename": filename}
        result = await client.get(
            "/api/v1/utilities/guessit",
            headers=headers,
            params=params,
            follow_redirects=True,
        )
        result.raise_for_status()

        if result.json().get("type") == "episode":
            params = {
                "query": result.json().get("title"),
                "type": result.json().get("type"),
                "season_number": result.json().get("season"),
                "episode_number": result.json().get("episode"),
                "languages": language,
            }
        else:
            params = {
                "query": result.json().get("title"),
                "type": result.json().get("type"),
                "languages": "pt-BR",
            }

        # Segunda requisição
        result = await client.get(
            "/api/v1/subtitles", headers=headers, params=params, follow_redirects=True
        )
        result.raise_for_status()
        file_ids = [
            i["attributes"]["files"][0]["file_id"] for i in result.json().get("data")
        ]

        # Terceira requisição
        for file_id in file_ids:
            params = {"file_id": file_id}
            result = await client.post(
                "/api/v1/download",
                headers=headers,
                params=params,
                follow_redirects=True,
            )
            result.raise_for_status()

            return_data = result.json().get("link")

            filename = return_data.split("/")[-1]
            print(f"Downloading file: {filename}")
            absolute_path = os.path.abspath(os.path.curdir)
            subtitle_file = open(os.path.join(absolute_path, filename), "wb")
            result = await client.get(return_data)
            for chunk in result.iter_bytes(100000):
                subtitle_file.write(chunk)

            subtitle_file.close()


async def main():
    tasks = []
    tasks.append(
        get_subtitles(filename=arguments.filename, language=arguments.language)
    )
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
