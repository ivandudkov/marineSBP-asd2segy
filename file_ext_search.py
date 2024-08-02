import os


# Define a function that searches for files with defined extension
# and returns a list of full paths for these files

# If function doesn't find any file in the parent directory,
# it will search for one directory up

# August 2021
# Author: Ivan Dudkov
# Affiliations:
# P.P Shirshov's Institute of Oceanography, Atlantic Branch, Kaliningrad, Russia. (2018 - 2023)
# Center for Coastal and Ocean Mapping, University of New Hampshire. Durham, USA. (2020-2021)

def file_ext_search(extension: str, path=os.getcwd(), search_up=False, recursive=False) -> list:
    """
    extension
    path
    recursive
    """
    
    # Check the top path existence
    if os.path.exists(path):
        print(('Searching *%s files in directory:' + path) % extension)
    else:  # Raise a meaningful error
        raise RuntimeError('Path either not exists or not correct ' + path)

    paths = []
    count = 0
    for dirpath, dirnames, filenames in os.walk(path):
        if recursive is True:
            for filename in filenames:
                fextension = os.path.splitext(filename)[1]
                if fextension == extension:
                    paths.append(os.path.abspath(os.path.join(dirpath, filename)))
                    count += 1
        else:
            if dirpath == path:
                for filename in filenames:
                    fextension = os.path.splitext(filename)[1]
                    if fextension == extension:
                        paths.append(os.path.abspath(os.path.join(dirpath, filename)))

                        count += 1

    count = 0
    if len(paths) == 0 and search_up == True:
        os.chdir(os.path.dirname(path))
        path_up = os.getcwd()
        print("Searching was unsuccessful. Trying to search in one directory up:\n%s" % path_up)

        for dirpath, dirnames, filenames in os.walk(path_up):
            for filename in filenames:
                fextension = os.path.splitext(filename)[1]
                if fextension == extension:
                    paths.append(os.path.abspath(os.path.join(dirpath, filename)))
                    count += 1
    elif len(paths) == 0 and search_up == False:
        raise RuntimeError(f'Searching was unsuccessful. There are no {extension} files in {path} folder')
    
    if len(paths) == 0:
        raise RuntimeError(f'Searching was unsuccessful. There are no {extension} files in {path} folder')
    
    return paths


def select_file(selection_list):
    """Selection list should contain paths"""
    for num, item in enumerate(selection_list):
        item_name = os.path.basename(item)
        print(f'{num} {item_name}')
    print()
    
    print("Please, select track table")
    selected_item = int(input())

    item = selection_list[selected_item]
    print(f'Selected file: {selected_item} {item}')
    
    return item