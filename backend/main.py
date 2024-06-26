import asyncio
import threading
import Millennium
import json, os
import platform

from ipc.socket import serve_websocket, start_websocket_server

# get runtime platform
_platform = platform.system()

if _platform == "Windows":
    from _win32.colors import get_accent_color
elif _platform == "Linux":
    from _posix.colors import get_accent_color

from api.themes_store import find_all_themes
from api.plugins_store import find_all_plugins
from api.user_data import Config, cfg
from webkit.stack import WebkitStack, add_browser_css, add_browser_js
from ipc.socket import uninstall_theme

from updater.git import Updater

updater = Updater()

def get_steam_path():
    return Millennium.steam_path()

def get_load_config():

    config = cfg.get_config()

    query = {
        "accent_color": json.loads(get_accent_color()), 
        "conditions": config["conditions"] if "conditions" in config else None, 
        "active_theme": json.loads(cfg.get_active_theme()),
        "settings": config
    }
    return json.dumps(query)


def update_plugin_status(plugin_name: str, enabled: bool):
    Millennium.change_plugin_status(plugin_name, enabled)

class Plugin:
    def _front_end_loaded(self):
        print("loaded millennium frontend")

    def _load(self):     
        try:
            print(f"loaded millennium v{Millennium.version()}")
            print("setting up settings store...")

            theme = json.loads(cfg.get_active_theme())
            name = cfg.get_active_theme_name()

            if "failed" not in theme and "Steam-WebKit" in theme["data"] and isinstance(theme["data"]["Steam-WebKit"], str):
                print("pre-initiliazing browser css module")
                add_browser_css(os.path.join(Millennium.steam_path(), "skins", name, theme["data"]["Steam-WebKit"]))

        except Exception as excep:
            print(f"exception thrown @ _load -> {excep}")

        websocket_thread = threading.Thread(target=start_websocket_server)
        websocket_thread.start()

    def _unload(self):
        print("unloading")
