@echo off
setlocal

if "%MSI_VERSION%"=="" set MSI_VERSION=0.0.0.0

python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 8) else 1)" || (
  echo Windows 7 builds require Python 3.8.x.
  exit /b 1
)

pip install -r requirements-win7.txt || exit /b 1
python dist\createmsi.py --write-metadata --variant win7 --version %MSI_VERSION% || exit /b 1

pyinstaller --noconsole --noconfirm --name vdiclient --hidden-import proxmoxer.backends --hidden-import proxmoxer.backends.https --hidden-import proxmoxer.backends.https.AuthenticationError --hidden-import proxmoxer.core --hidden-import proxmoxer.core.ResourceException --hidden-import subprocess.TimeoutExpired --hidden-import subprocess.CalledProcessError --hidden-import requests.exceptions --hidden-import requests.exceptions.ReadTimeout --hidden-import requests.exceptions.ConnectTimeout --hidden-import requests.exceptions.RequestException --add-data "vdi\i18n\locales;vdi\i18n\locales" --noupx -i vdiicon.ico main.py || exit /b 1

copy vdiclient.png dist\vdiclient
copy vdiicon.ico dist\vdiclient
pushd dist
python createmsi.py vdiclient-win7.json || exit /b 1
popd
