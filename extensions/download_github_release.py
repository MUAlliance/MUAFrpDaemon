import requests
import traceback
from contextlib import closing
import re
from typing import Union, Optional, Tuple

from daemon import *

GITHUB_MIRROR = "https://github.com"

class Resource:
    def download(self, output_path : str, output_filename : Union[str, None] = None) -> str:
        pass

    def getId(self) -> int:
        pass

class InvalidResource(Resource):
    def __init__(self, error : str):
        self.error = error

    def download(self, output_path : str, output_filename : Union[str, None] = None) -> str:
        WARN(self.error)
        return None

    def getId(self) -> int:
        return 0

class DownloadableResource(Resource):
    def __init__(self, url : str, filename : str, id : int):
        self.url = url
        self.filename = filename
        self.id = id

    def getId(self) -> int:
        return self.id

    def download(self, output_path : str, output_filename : Union[str, None] = None) -> str:
        with closing(requests.get(self.url, stream=True)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            data_count = 0
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            output_filename = self.filename if output_filename is None else output_filename
            with open(os.path.join(output_path, output_filename), "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    data_count = data_count + len(data)
                    progress = (data_count / content_size) * 100
                    print("\r Downloading: %d%%(%d/%d) - %s"
                        % (progress, data_count, content_size, self.url), end=" ")
                print()
        return os.path.join(output_path, output_filename)

class GitHubDownloader:
    def __init__(self, repo : str):
        url = f"https://api.github.com/repos/{repo}/releases"
        response = requests.get(url)
        if response.status_code == 200:
            self.release_info = response.json()
            self.failure_info = None
        else:
            self.release_info = None
            self.failure_info = response.status_code

    def search(self, version : Optional[str], release_keyword : Union[str, re.Pattern, None]) -> Resource:
        if self.release_info is not None:
            try:
                selected_release = None
                if version is None or version.lower() == "latest":
                    selected_release = self.release_info[0]
                else:
                    for release in self.release_info:
                        if release["name"] == version:
                            selected_release = release
                            break
                if selected_release is not None:
                    selected_asset = None
                    if release_keyword is None:
                        selected_asset = selected_release["assets"][0]
                    else:
                        if isinstance(release_keyword, str):
                            release_keyword = re.compile(release_keyword)
                        for asset in selected_release["assets"]:
                            if re.search(release_keyword, asset["name"]) is not None:
                                selected_asset = asset
                                break
                    if selected_asset is not None:
                        return DownloadableResource(selected_asset["browser_download_url"], selected_asset["name"], selected_asset["id"])
                    return InvalidResource("Failed to match a release file.")
                return InvalidResource("Failed to find the version.")
            except Exception as e:
                traceback.print_exc()
                return InvalidResource("Error occured.")
        return InvalidResource("Failed to fetch GitHub API.")