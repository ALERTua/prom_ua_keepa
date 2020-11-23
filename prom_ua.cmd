
@echo off
set PYTHONIOENCODING=UTF-8
set PYTHONWARNINGS=ignore:DEPRECATION::pip._internal.cli.base_command
set PYTHONPATH=%~dp0
rem pushd %~dp0source
%~dp0venv.cmd main.py %*
