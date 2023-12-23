import os
import re
import requests

from daemon import *
from extensions.minecraft import SERVER
from utils import extension_config

class BungeeCordAutoUpdater:
    def __init__(self):
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit, Event.Priority.HIGH)
        self.__config = extension_config.load_config("autoupdate_bungeecord.yml", {
            "file" : "bungeecord.jar"
        })  

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        #if not os.path.exists(os.path.join(SERVER.getDir(), file)):
        #    WARN(f"Skipping BungeeCord autoupdate because {file} does not exist in SERVER.getDir().")
        #    return
        INFO("Checking for BungeeCord updates...")
        BASE_URL = "https://ci.md-5.net/job/BungeeCord/lastStableBuild/artifact/bootstrap/target/BungeeCord.jar"
        try:
            remote_md5 = re.search(r'<a href="/" class>(.*?)</a>', requests.get(f"{BASE_URL}/*fingerprint*/").text).group(1)
            if os.path.exists(os.path.join(SERVER.getDir(), self.__config["file"])):
                local_md5 = hashlib.md5(open(os.path.join(SERVER.getDir(), self.__config["file"]), "rb").read()).hexdigest()
            else:
                local_md5 = None
            if remote_md5 == local_md5:
                INFO("BungeeCord is up to date.")
                return
            INFO("BungeeCord is outdated. Updating to latest version...")
            response = requests.get(BASE_URL)
            if response.status_code != 200:
                WARN(f"Failed to download BungeeCord. Status code: {response.status_code}")
                return
            with open(os.path.join(SERVER.getDir(), self.__config["file"]), "wb") as f:
                f.write(response.content)
            INFO("BungeeCord updated successfully.")
        except Exception as e:
            WARN("Error occured:")
            traceback.print_exc(e)
            return
        
BungeeCordAutoUpdater()