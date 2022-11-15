import glob
import os
import shutil
from typing import Final

program_name: Final[str] = "auto-print"
p = os.path.join(
    os.path.expandvars("%userprofile%"), "AppData/Local/pypoetry/Cache/virtualenvs"
)
folder_path = f"{p}/{program_name}*/Lib/site-packages/{program_name.replace('-', '_')}-*.dist-info"
print(folder_path)
for folder in glob.glob(folder_path):
    print(folder)
    shutil.rmtree(folder)
