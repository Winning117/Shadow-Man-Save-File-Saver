# python3
import os
import sys
import time
import shutil
import zipfile
import datetime
import hashlib

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
    with open("settings.txt") as settings_file:
        for line in settings_file:
            if line.startswith("saves_location="):
                save_folder_location = line.split("\"")[1]
                if not save_folder_location.endswith("/"):
                    save_folder_location += "/"
            if line.startswith("convert_windows_to_linux="):
                if line.startswith("convert_windows_to_linux=true"):
                    convert_windows_to_linux = True
                else:
                    convert_windows_to_linux = False
            if line.startswith("poll_rate_in_seconds"):
                try:
                    poll_rate_in_seconds = line.split("poll_rate_in_seconds=")[1].split(" ")[0]
                    poll_rate_in_seconds = int(poll_rate_in_seconds)
                except ValueError:
                    print(f"ERROR: poll_rate_in_seconds in settings.txt should be an integer, not '{poll_rate_in_seconds}'.")
                    sys.exit(1)

    if convert_windows_to_linux:
        save_folder_location = save_folder_location.replace("\\","/") # Linux uses forward slashes instead of backslashes
        drive_name = save_folder_location.split(":")[0].lower()
        path_without_drive = save_folder_location.split(":")[1]
        save_folder_location = "/mnt/" + drive_name + path_without_drive

    print(f"Checking the folder '{save_folder_location}' for Shadow Man saves...")
    if os.path.exists(save_folder_location):
        files_in_save_location = os.listdir(save_folder_location)
    else:
        print(f"Unable to find folder '{save_folder_location}'!")
        sys.exit(1)

    time_now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    this_file_location = os.path.dirname(os.path.abspath(__file__))
    zip_save_location = this_file_location + "/" + time_now + "_initial"
    print(f"Initial files saved to '{zip_save_location}'")
    shutil.make_archive(zip_save_location, "zip", save_folder_location)

    initial_file_hash = md5(zip_save_location + ".zip")
    print(f"The file hash is {initial_file_hash}")

    latest_file_hash = initial_file_hash

    while True:
        try:
            time_now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            this_file_location = os.path.dirname(os.path.abspath(__file__))
            zip_save_location = this_file_location + "/" + time_now
            shutil.make_archive(zip_save_location, "zip", save_folder_location)
            this_file_hash = md5(zip_save_location + ".zip")
            if this_file_hash == latest_file_hash:
                print(f"{this_file_hash} == {latest_file_hash}")
                os.remove(zip_save_location + ".zip")
            else:
                latest_file_hash = this_file_hash

            time.sleep(poll_rate_in_seconds)
        except KeyboardInterrupt:
            print("\nCtrl-C caught! Exiting...")
            break

        # TODO: ONLY ZIP THE FILE IF THE HASH IS DIFFERENT


if __name__ == "__main__":
    main()
