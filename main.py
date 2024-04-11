import os
import time
import shutil
import winreg
import configparser

from rich.console import Console

console = Console()


def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    steamid3 = config.get("Settings", "steamid3")
    gameids = config.get("Settings", "gameids").split(",")
    userdatapath = config.get("Settings", "userdataPath")
    console.log(f"Reading configuration from: {config_file}")
    console.log(f"Configured GameID: {gameids}")
    console.log(f"Configured SteamID3: {steamid3}")
    console.log(f"Userdata Path: {userdatapath}")
    return steamid3, gameids, userdatapath


def get_steamid3_from_registry():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam\ActiveProcess")
        steamid3, _ = winreg.QueryValueEx(key, "ActiveUser")
        steamid3 = str(steamid3)
        console.log(f"Current SteamID3 from registry: {steamid3}")
        return steamid3
    except Exception as e:
        console.log(f"Failed to get SteamID3 from registry: {e}")
        return ""


def copy_game_folders(source_path, target_path):
    try:
        if not os.path.exists(source_path):
            console.log(f"Source path does not exist: {source_path}")
            return False

        if not os.path.exists(target_path):
            console.log(f"Target path does not exist, creating: {target_path}")
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
        else:
            console.log(f"Target path exists, removing existing files: {target_path}")
            shutil.rmtree(target_path)

        console.log(f"Copying files from: {source_path} to: {target_path}")
        shutil.copytree(source_path, target_path)
        console.log("Successfully copied files.")
        return True
    except Exception as e:
        console.log(f"Error copying folders: {e}")
        return False


def main():
    configured_steamid3, gameids, base_userdata_path = read_config("./configs/config.ini")
    processed_steamids = set()

    while True:
        current_steamid3 = get_steamid3_from_registry()
        if current_steamid3 == "0":
            console.log("Current SteamID3 is 0, indicating no user is logged in. Skipping...")
            time.sleep(10)
            continue

        if (
            current_steamid3
            and current_steamid3 != configured_steamid3
            and current_steamid3 not in processed_steamids
        ):
            console.log("Detected new SteamID3, proceeding with copy operation.")
            for gameid in gameids:
                source_path = os.path.join(base_userdata_path, configured_steamid3, gameid)
                target_path = os.path.join(base_userdata_path, current_steamid3, gameid)
                if copy_game_folders(source_path, target_path):
                    console.log(f"Successfully copied game folder for gameID: {gameid}")
                else:
                    console.log(f"Failed to copy game folder for gameID: {gameid}")
            processed_steamids.add(current_steamid3)
        else:
            console.log("No new SteamID3 detected or already processed.")

        time.sleep(5)


if __name__ == "__main__":
    main()
