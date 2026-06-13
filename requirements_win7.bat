@echo off
python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 8) else 1)" || (
  echo Windows 7 builds require Python 3.8.x.
  exit /b 1
)
pip install -r requirements-win7.txt
