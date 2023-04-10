"""
Deletes the version number from auto-print
"""

import glob
import os
import shutil
from typing import Final

PROGRAMM_NAME: Final[str] = "auto-print"
p = os.path.join(
    os.path.expandvars("%userprofile%"), "AppData/Local/pypoetry/Cache/virtualenvs"
)
folder_path = f"{p}/{PROGRAMM_NAME}*/Lib/site-packages/{PROGRAMM_NAME.replace('-', '_')}-*.dist-info"
print(folder_path)
for folder in glob.glob(folder_path):
    print(folder)
    shutil.rmtree(folder)
