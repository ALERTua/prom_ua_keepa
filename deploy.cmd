
@echo off
@REM set DOCKER_IMAGE_NAME=my_app_image_name
if not defined DOCKER_IMAGE_NAME (
    echo Please define Docker Image Name with
    echo set DOCKER_IMAGE_NAME=
    exit /b
)

@REM set DOCKER_REGISTRY_IP=192.168.1.3
if not defined DOCKER_REGISTRY_IP (
    echo Please define Docker Registry IP Address with
    echo set DOCKER_REGISTRY_IP=
    exit /b
)

@REM set DOCKER_REGISTRY_PORT=5001
if not defined DOCKER_REGISTRY_PORT (
    echo Please define Docker Registry Port with
    echo set DOCKER_REGISTRY_PORT=
    exit /b
)

if not defined DOCKER_IMAGE_TAG (
    set DOCKER_IMAGE_TAG=latest
    echo You can override Docker Image Tag 'latest' with
    echo set DOCKER_IMAGE_TAG=
)

set BUILD_TAG=%DOCKER_REGISTRY_IP%:%DOCKER_REGISTRY_PORT%/%DOCKER_IMAGE_NAME%:%DOCKER_IMAGE_TAG%
set BUILD_PATH=.

set DOCKER_EXE=docker
if not exist "%DOCKER_EXE%" (
    set "DOCKER_EXE=C:\Program Files\Docker\Docker\resources\bin\docker.exe"
)
if not exist "%DOCKER_EXE%" (
    echo Please add docker.exe to the environment variable PATH
    exit /b
)

call net start com.docker.service >nul 2>nul
call sudo start com.docker.service >nul 2>nul

echo Building
"%DOCKER_EXE%" build -t %BUILD_TAG% %BUILD_PATH% || (
    echo Build Failed
    exit /b
)
echo Uploading
"%DOCKER_EXE%" push %DOCKER_REGISTRY_IP%:%DOCKER_REGISTRY_PORT%/%DOCKER_IMAGE_NAME% || (
    echo Upload Failed
    exit /b
)
echo Done

@REM net start com.docker.service >nul
@REM sudo start com.docker.service >nul