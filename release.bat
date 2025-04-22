:: filepath: \release.bat
@echo off
setlocal

:: Check if version number is provided
if "%1"=="" (
    echo Usage: release -v version-number
    exit /b 1
)

:: Parse arguments
if "%1"=="-v" (
    set VERSION=%2
) else (
    echo Invalid argument. Use -v to specify the version number.
    exit /b 1
)

:: Tag the version
git tag -a v%VERSION% -m "Release version %VERSION%"
git push origin v%VERSION%

:: Notify user
echo Release v%VERSION% has been tagged and pushed.