import os
import pathlib

def search_directory(target_directory: str) -> list[str] | None:
    # target_directory = str(input('target directory:'))
    try:
        files = os.listdir(f"{target_directory}")
        print(len(files))
        return files
    except FileNotFoundError:
        print(f"cannot found {target_directory}")
        return None
    except OSError:
        print(f'failed to search directory {target_directory}')
        return None

def has_video_file_extension(file: str) -> bool:
    expected_file_ext_list = ['.mp4', '.mov']
    file_ext = pathlib.Path(file).suffix.lower()
    return True if file_ext in expected_file_ext_list else False

def filter_video_file(fileList: list[str]) -> list[str] | None:
    return list(filter(has_video_file_extension, fileList))