import os
import requests
import re
import json
from typing import Union

from daemon import *
from extensions.download_github_release import GitHubDownloader
from extensions.minecraft import MINECRAFT_PROXY_DIR

SPIGET_PLUGINS = [
    (19254, "viaversion.jar"),
    ()
]

GITHUB_PLUGINS = [
    ("CakeDreamer/ProxiedProxy", "ProxiedProxy.jar"),
    ("")
]

STORAGE_FILE = "autoupdate_plugins.txt"

class SpigetPluginAutoUpdater:
    def __init__(self, plugins : list[str]):
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit, Event.Priority.HIGH)
        self.plugins = plugins

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        for resource_id, jar_file in SPIGET_PLUGINS:
            self.download(resource_id, os.path.join(MINECRAFT_PROXY_DIR, "plugins", jar_file))

    def download(self, resource_id : str, save_path : str) -> None:
        BASE_URL = 'https://api.spiget.org/v2/resources'
        DOWNLOAD_URL = '{}/{}/download'.format(BASE_URL, resource_id)
        try:
            response = requests.get(DOWNLOAD_URL, stream=True)

            # Check SHA1 of the local file if it exists
            if os.path.exists(save_path):
                with open(save_path, 'rb') as file:
                    local_sha1 = hashlib.sha1(file.read()).hexdigest()
            else:
                local_sha1 = None
            
            # Check SHA1 of the remote file
            remote_sha1 = response.headers.get('X-Spiget-Resource-SHA1')

            # Continue download if file doesn't exist locally or SHA1 mismatch
            if local_sha1 != remote_sha1:
                if response.status_code == 200:
                    with open(save_path, 'wb') as file:
                        file.write(response.raw.read())
                        
                    INFO('Download completed. File saved to: {}'.format(save_path))
                else:
                    WARN(f'Unable to download the plugin. Status code: {response.status_code}')
            else:
                WARN(f'File already exists locally with matching SHA1: {local_sha1}')
        except Exception as e:
            WARN(f'An error occurred while downloading the plugin: {str(e)}')
        
class GithubPluginAutoUpdater:
    def __init__(self, plugins : list[str]):
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit, Event.Priority.HIGH)
        self.plugins = plugins
        self.downloaded_ids = {}
        self.downloaded_ids_new = {}

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        with open(os.path.join("extensions", STORAGE_FILE), 'r') as f:
            try:
                self.downloaded_ids = json.load(f)
            except:
                self.downloaded_ids = {}
        for item in GITHUB_PLUGINS:
            if len(item) == 2:
                repo, output = item
                keyword = "*.jar"
            elif len(item) == 3:
                repo, output, keyword = item
            else:
                continue
            self.download(repo, keyword, os.path.join(MINECRAFT_PROXY_DIR, "plugins", output))
        with open(os.path.join("extensions", STORAGE_FILE), 'w') as f:
            json.dump(self.downloaded_ids_new, f)

    def download(self, repo : str, keyword : Union[str, re.Pattern, None], output : str) -> None:
        resource = GitHubDownloader(repo).search(keyword)
        if resource.getId() != 0:
            if self.downloaded_ids.get(output, 0) != resource.getId():
                resource.download(output)
            self.downloaded_ids_new[output] = resource.getId()