"""
Deriving version information from the package metadata.
this information is used in the GUI and CLI
"""

from importlib.metadata import version, metadata


meta = metadata("Sberbank2Excel") 

NAME =  meta["Summary"]

AUTHOR = meta["Author-email"] 

urls = {label: url for label, url in
        (line.split(", ", 1) for line in meta.get_all("Project-URL") or [])}

HOMEPAGE = urls.get("Homepage")

VERSION = version("Sberbank2Excel")

def main():

    print(f"NAME =  {NAME}")
    print(f"AUTHOR: {AUTHOR}")
    print(f"HOMEPAGE: {HOMEPAGE}")
    print(f"VERSION: {VERSION}")
    
if __name__ == "__main__":
    main()