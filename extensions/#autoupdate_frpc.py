import os
import requests
import tarfile
import zipfile
import shutil

import config
import traceback
import platform

from daemon import *
from extensions.download_github_release import GitHubDownloader

VERSION_FILE = "version.txt"

class FrpcAutoUpdater:
    def __init__(self):
        DAEMON.eventMgr.registerHandler(DaemonStartEvent, self.onDaemonInit, Event.Priority.HIGH)

    def onDaemonInit(self, event : DaemonStartEvent) -> None:
        INFO("Checking for Frpc updates...")
        try:
            version = event.frpc_daemon.union_api.queryPublicAPI()["union_entry"]["frp_version"]
            if not os.path.exists(FRPC_DIR):
                os.makedirs(FRPC_DIR)
            vfile_path = os.path.join(FRPC_DIR, VERSION_FILE)
            if not os.path.exists(vfile_path):
                open(vfile_path, 'w').close()
            with open(vfile_path, 'r') as f:
                if f.read() == version:
                    return
            os_python_name = platform.system()
            if os_python_name == "Linux":
                os_name = "linux"
            elif os_python_name == "Windows":
                os_name = "windows"
            elif os_python_name == "Darwin":
                os_name = "darwin"
            elif os_python_name == "FreeBSD":
                os_name = "freebsd"
            else:
                WARN("Unsupported operating system.")
                return
            machine_name = platform.machine().lower()
            if machine_name == "amd64":
                arch = "amd64"
            elif machine_name == "x86_64":
                arch = "amd64"
            elif machine_name == "aarch64":
                arch = "arm64"
            elif machine_name == "arm64":
                arch = "arm64"
            else:
                WARN("Unsupported architecture.")
                return
            self.downloadFrpc(version, os_name, arch, os.path.join(config.FRPC_DIR,"frpc_download"))
        except Exception as e:
            WARN("Error occured:")
            traceback.print_exc(e)
            return

    def downloadFrpc(self, version : str, os_name : str, arch : str, output : str) -> None:
        repo = "fatedier/frp"
        fpath = GitHubDownloader(repo).search("v" + version, f"{os_name}_{arch}").download(output)
        if fpath.endswith('.tar.gz'):
            with tarfile.open(fpath, 'r:gz') as tf:
                subfolder = [m for m in tf.getmembers() if m.isdir()][0].name
                tf.extractall(config.FRPC_DIR)
                for f in os.listdir(os.path.join(config.FRPC_DIR, subfolder)):
                    shutil.move(os.path.join(config.FRPC_DIR, subfolder, f), config.FRPC_DIR)
                os.rmdir(os.path.join(config.FRPC_DIR, subfolder))
            with open(os.path.join(FRPC_DIR, VERSION_FILE), 'w') as f:
                f.write(version)
        elif fpath.endswith('.zip'):
            with zipfile.ZipFile(fpath, 'r') as zf:
                subfolder = [n for n in zf.namelist() if n.endswith('/')][0]
                zf.extractall(config.FRPC_DIR)
                for f in os.listdir(os.path.join(config.FRPC_DIR, subfolder)):
                    shutil.move(os.path.join(config.FRPC_DIR, subfolder, f), config.FRPC_DIR)
                os.rmdir(os.path.join(config.FRPC_DIR, subfolder))
            with open(os.path.join(FRPC_DIR, VERSION_FILE), 'w') as f:
                f.write(version)
        else:
            WARN("Unknown format")

FrpcAutoUpdater()