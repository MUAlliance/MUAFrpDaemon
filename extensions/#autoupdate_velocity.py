import os
import requests

from daemon import *
from extensions.minecraft import SERVER
from utils import extension_config

class VelocityAutoUpdater:
    def __init__(self):
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit, Event.Priority.HIGH)
        self.__config = extension_config.load_config("autoupdate_velocity.yml", {
            "file" : "velocity.jar"
        })  

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        #if not os.path.exists(os.path.join(SERVER.getDir(), self.__config["file"])):
        #    WARN(f"Skipping Velocity autoupdate because {self.__config["file"]} does not exist in SERVER.getDir().")
        #    return
        INFO("Checking for Velocity updates...")
        BASE_URL = "https://api.papermc.io/v2/projects/velocity"
        try:
            version = requests.get(BASE_URL).json()["versions"][-1]
            build = requests.get(f"{BASE_URL}/versions/{version}/builds").json()["builds"][-1]
            remote_sha256 = build["downloads"]["application"]["sha256"]
            if os.path.exists(os.path.join(SERVER.getDir(), self.__config["file"])):
                local_sha256 = hashlib.sha256(open(os.path.join(SERVER.getDir(), self.__config["file"]), "rb").read()).hexdigest()
            else:
                local_sha256 = None
            if remote_sha256 == local_sha256:
                INFO("Velocity is up to date.")
                return
            INFO("Velocity is outdated. Updating to latest version...")
            download_url = BASE_URL + f"/versions/{version}/builds/{build['build']}/downloads/{build['downloads']['application']['name']}"
            response = requests.get(download_url)
            if response.status_code != 200:
                WARN(f"Failed to download Velocity. Status code: {response.status_code}")
                return
            with open(os.path.join(SERVER.getDir(), self.__config["file"]), "wb") as f:
                f.write(response.content)
            INFO("Velocity updated successfully.")
        except Exception as e:
            WARN("Error occured:")
            traceback.print_exc(e)
            return
        
VelocityAutoUpdater()