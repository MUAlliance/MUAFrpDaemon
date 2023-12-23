import os
import requests

from daemon import *
from extensions.minecraft import SERVER
from extensions.download_github_release import GitHubDownloader
from utils import extension_config

class AuthlibAutoUpdater:
    def __init__(self):
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit, Event.Priority.HIGH)
        self.__config = extension_config.load_config("autoupdate_authlib_injector.yml", 
            {
                "file" : "authlib-injector.jar"
            })  

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        #if not os.path.exists(os.path.join(SERVER.getDir(), file)):
        #    WARN(f"Skipping authlib-injector autoupdate because {file} does not exist in SERVER.getDir().")
        #    return
        INFO("Checking for authlib-injector updates...")
        BASE_URL = "https://authlib-injector.yushi.moe/artifact/latest.json"
        try:
            build = requests.get(BASE_URL).json()
            remote_sha256 = build["checksums"]["sha256"]
            if os.path.exists(os.path.join(SERVER.getDir(), self.__config["file"])):
                local_sha256 = hashlib.sha256(open(os.path.join(SERVER.getDir(), self.__config["file"]), "rb").read()).hexdigest()
            else:
                local_sha256 = None
            if remote_sha256 == local_sha256:
                INFO("authlib-injector is up to date.")
                return
            INFO("authlib-injector is outdated. Updating to latest version...")
            download_url = build["download_url"]
            response = requests.get(download_url)
            if response.status_code != 200:
                WARN(f"Failed to download authlib-injector. Status code: {response.status_code}")
                return
            with open(os.path.join(SERVER.getDir(), self.__config["file"]), "wb") as f:
                f.write(response.content)
            INFO("authlib-injector updated successfully.")
        except Exception as e:
            WARN("Error occured:")
            traceback.print_exc(e)
            return
        
AuthlibAutoUpdater()