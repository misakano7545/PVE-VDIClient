@echo off
pyinstaller --noconsole --noconfirm --name vdiclient --hidden-import proxmoxer.backends --hidden-import proxmoxer.backends.https --hidden-import proxmoxer.backends.https.AuthenticationError --hidden-import proxmoxer.core --hidden-import proxmoxer.core.ResourceException --hidden-import subprocess.TimeoutExpired --hidden-import subprocess.CalledProcessError --hidden-import requests.exceptions --hidden-import requests.exceptions.ReadTimeout --hidden-import requests.exceptions.ConnectTimeout --hidden-import requests.exceptions.RequestException --add-data "vdi\i18n\locales;vdi\i18n\locales" --noupx -i vdiicon.ico main.py
copy vdiclient.png dist\vdiclient
copy vdiicon.ico dist\vdiclient
cd dist
python createmsi.py vdiclient.json
cd ..
