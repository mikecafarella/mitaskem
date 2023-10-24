import hashlib
import os
import sys

def init_cache_directory(cache_directory):
    path = cache_directory
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("The new directory is created!")


def file_exists_in_cache(file_content, cache_directory):
    md5 = hashlib.md5(file_content).hexdigest()
    for file in os.listdir(cache_directory):
        if file.startswith(f"{md5}"):
            return True
    return False


def save_file_to_cache(file_name, file_content, cache_directory="/tmp/askem"):
    os.makedirs(cache_directory, exist_ok=True)
    md5 = hashlib.md5(file_content).hexdigest()
    cached_file_name = f"{md5}__{file_name}"
    if os.path.exists(os.path.join(cache_directory, cached_file_name)):
        print("File already exists in cache_directory")
        return cached_file_name

    file_path = os.path.join(cache_directory, cached_file_name)
    with open(file_path, "wb") as file:
        file.write(file_content)
        print(f"{file_path} saved in {cache_directory}")
    return cached_file_name

def main():
    # Input: file name and file content
    file_name = input("Enter the file name: ")
    file_content = input("Enter the file content: ").encode("utf-8")

    # Linux caching directory
    cache_directory = "/tmp/askem"

    init_cache_directory(cache_directory)

    # Check if the file matches with any file with md5 under the cache_directory
    if not file_exists_in_cache(file_content, cache_directory):
        # Save the file in the cache_directory
        save_file_to_cache(file_name, file_content, cache_directory)
    else:
        print("File already exists in cache_directory")


if __name__ == "__main__":
    main()