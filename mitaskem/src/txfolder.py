import os
import shutil
from contextlib import contextmanager
import warnings

@contextmanager
def transactional_folder(folder_path, force=False):
    '''
        Example usage
        folder_path = "/path/to/folder"
        with transactional_folder(folder_path) as temp_folder:
            Perform file modifications inside the 'with' block
            You can use temp_folder to create, modify, or delete files

        If everything was successful, the changes are now committed as a single folder
        If an exception occurred, no changes have been applied
        force means we overwrite an existing folder if it exists, but only if successful
    '''
    if os.path.exists(folder_path):
        if force:
            warnings.warn(
                f'folder {folder_path} already exists. overwriting due to force=True'
            )
        else:
            raise Exception(f'folder {folder_path} already exists. use "force=True" to allow overwrite')

    
    folder_path = folder_path.rstrip('/')
    prepath = os.path.dirname(folder_path)
    name = os.path.basename(folder_path)
    temp_folder = os.path.join(prepath, '.temp_' + name)
    
    try:
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        
        # Create a temporary folder to store the changes
        os.makedirs(temp_folder)

        # Yield the temporary folder to the code inside the 'with' block
        yield temp_folder

        # If everything succeeds, commit the changes by moving the temporary folder
        shutil.rmtree(folder_path, ignore_errors=True)
        shutil.move(temp_folder, folder_path)
    except Exception as e:
        # If an exception occurs, clean up the temporary folder
        shutil.rmtree(temp_folder, ignore_errors=True)
        raise e
