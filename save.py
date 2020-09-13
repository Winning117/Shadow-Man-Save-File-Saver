# python3
import os
import sys
import time
import shutil
import datetime
import hashlib


def get_directory_md5_hash(directory):
    """
    Calculates the md5 hash of the specified directory
    """
    md5_sum = hashlib.md5()
    for root, _, files in os.walk(directory):
        for names in files:
            filepath = os.path.join(root,names)
            try:
                f1 = open(filepath, 'rb')
            except:
                # You can't open the file for some reason
                f1.close()
                continue

            while True:
                # Read file in as little chunks
                buf = f1.read(4096)
                if not buf:
                    break
                md5_sum.update(hashlib.md5(buf).digest())
            f1.close()
    return md5_sum.hexdigest()

def zip_folder(folder_location):
    """
    Zips up the specified folder location
    """
    this_file_location = os.path.dirname(os.path.abspath(__file__))
    time_now = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    zip_save_location = this_file_location + "/" + time_now
    shutil.make_archive(zip_save_location, "zip", folder_location)
    print(f"Saved zip file to '{zip_save_location}.zip'")

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
    if not os.path.exists(save_folder_location):
        print(f"ERROR: Unable to find folder '{save_folder_location}'!")
        sys.exit(1)

    initial_hash = get_directory_md5_hash(save_folder_location)
    zip_folder(save_folder_location) # zip up the original folder when this script is launched so the user can revert to the original save

    while True: # check to see if the files have changed every X seconds. If they have, then save a copy of it
        try:
            directory_hash = get_directory_md5_hash(save_folder_location)

            if directory_hash != initial_hash:
                zip_folder(save_folder_location)
                initial_hash = directory_hash # overwrite the hash that we compare against

            time.sleep(poll_rate_in_seconds)
        except KeyboardInterrupt:
            print("\nCtrl-C caught! Exiting...")
            break


if __name__ == "__main__":
    main()
