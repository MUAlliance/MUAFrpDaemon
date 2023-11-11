import os
import re
import requests

from daemon import *
from extensions.minecraft import MINECRAFT_PROXY_DIR

JAR_NAME = "BungeeCord.jar"

class BungeeCordAutoUpdater:
    def __init__(self):
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit, Event.Priority.HIGH)

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        if not os.path.exists(os.path.join(MINECRAFT_PROXY_DIR, JAR_NAME)):
            WARN(f"Skipping BungeeCord autoupdate because {JAR_NAME} does not exist in MINECRAFT_PROXY_DIR.")
            return
        INFO("Checking for BungeeCord updates...")
        BASE_URL = "https://ci.md-5.net/job/BungeeCord/lastStableBuild/artifact/bootstrap/target/BungeeCord.jar"
        try:
            remote_md5 = re.search(r'<a href="/" class>(.*?)</a>', requests.get(f"{BASE_URL}/*fingerprint*/").text).group(1)
            local_md5 = hashlib.md5(open(os.path.join(MINECRAFT_PROXY_DIR, JAR_NAME), "rb").read()).hexdigest()
            if remote_md5 == local_md5:
                INFO("BungeeCord is up to date.")
                return
            INFO("BungeeCord is outdated. Updating to latest version...")
            response = requests.get(BASE_URL)
            if response.status_code != 200:
                WARN(f"Failed to download BungeeCord. Status code: {response.status_code}")
                return
            with open(os.path.join(MINECRAFT_PROXY_DIR, JAR_NAME), "wb") as f:
                f.write(response.content)
            INFO("BungeeCord updated successfully.")
        except Exception as e:
            WARN("Error occured:")
            traceback.print_exc(e)
            return
        
BungeeCordAutoUpdater()