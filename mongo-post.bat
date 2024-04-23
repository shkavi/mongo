@echo off
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%selene_mongodb.py
python "%PYTHON_SCRIPT%" %*
