import json
from os import listdir, makedirs, remove
from os.path import isfile, join, exists
from pathlib import Path
from config import *
import zipfile
from ntpath import basename
import shutil


def list_files(path, ext=None):
    files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    if ext:
        return list(filter(lambda x: x.endswith(ext), files))

    return files


def save_zip(out_file_path, files):
    backup = zipfile.ZipFile(out_file_path, "w")

    for file in files:
        name = basename(file)
        backup.write(file, arcname=name, compress_type=zipfile.ZIP_DEFLATED)


def get_backup_path(original_path):
    backup_path = join(Path(original_path).parent, 'backups')

    if not exists(backup_path):
        makedirs(backup_path)

    backup_files = list_files(backup_path)

    if not backup_files:
        return join(backup_path, 'backup_1_.zip')
    else:
        return join(backup_path, f"backup_{ max([int(name.split('_')[-2]) for name in backup_files]) +1 }_.zip")


def unzip(file, out_folder):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(out_folder)


def unzip_song(file, folder):
    sub_folder = join(folder, basename(file).replace('.zip',''))

    if exists(sub_folder):
        remove_folder(sub_folder)

    makedirs(sub_folder)
    unzip(file, sub_folder)
    return sub_folder


def process_song(file, work_folder):
    new_file = unzip_song(file, work_folder)
    all_files = list_files(new_file)
    song_files = [file for file in all_files if file.endswith('.dat')]

    for file in song_files:
        fix_file_with_obstacles(file)

    save_zip(f'{new_file}.zip', all_files)
    remove_folder(new_file)


def process_songs(files, work_folder):
    for file in files:
        process_song(file, work_folder)


def create_temp_folder():
    if not exists('temp'):
        makedirs('temp')
    return 'temp'


def remove_folder(folder):
    shutil.rmtree(folder)


def rewrite_file(file, content):
    remove(file)

    with open(file, 'w') as outfile:
        json.dump(content, outfile)


def fix_file_with_obstacles(file):
    data = {}
    obstacles_copy = []
    is_rewrite_file = False

    with open(file) as json_file:
        data = json.load(json_file)

    if '_obstacles' in data:
        obstacles = data.pop('_obstacles')
        for obstacle in obstacles:
            if obstacle['_type'] == 1:
                is_rewrite_file = True
            else:
                obstacles_copy.append(obstacle)

    if is_rewrite_file:
        data['_obstacles'] = obstacles_copy
        rewrite_file(file, data)


def replace_original_song(src, dst):
    shutil.copyfile(src, dst)


def replace_original_songs(src, dst):
    for file in list_files(src, 'zip'):
        replace_original_song(file, join(dst, basename(file)))


def main():
    files = list_files(SONGS_FILE, 'zip')
    save_zip(get_backup_path(SONGS_FILE), files)
    work_folder = create_temp_folder()

    process_songs(files, work_folder)
    replace_original_songs(work_folder, SONGS_FILE)

    remove_folder(work_folder)


if __name__ == "__main__":
    main()