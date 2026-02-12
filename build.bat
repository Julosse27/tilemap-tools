@echo off
echo Nettoyage...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
for /d %%i in (*.egg-info) do rmdir /s /q "%%i" 2>nul

echo.
echo Construction du package...
python -m build

if errorlevel 1 (
    echo Erreur de construction
    pause
    exit /b 1
)

echo.
echo Construction reussie!
echo.
echo Options:
echo 1. Upload vers TestPyPI
echo 2. Upload vers PyPI
echo 3. Arreter ici
echo.

set choice=
set /p choice=Votre choix: 

if "%choice%"=="1" (
    echo Upload vers TestPyPI...
    python -m twine upload --repository testpypi dist/*
    if errorlevel 0 (
        echo.
        echo Ok - Upload reussi sur TestPyPI !
        echo.
        echo Installation du package dans 2 minutes
        ping 127.0.0.1 -n 121 > nul
        pip uninstall -y tilemap-tools
        pip install -i https://test.pypi.org/simple/ tilemap-tools
    )
)

if "%choice%"=="2" (
    set /p confirm=Confirmer upload vers PyPI ? (oui/non): 
    if "!confirm!"=="oui" (
        echo Upload vers PyPI...
        python -m twine upload dist/*
        if errorlevel 0 (
            echo.
            echo Ok - Upload reussi sur PyPI !
            echo.
            echo Installation du package dans 2 minutes
            ping 127.0.0.1 -n 121 > nul
            pip uninstall -y tilemap-tools
            pip install tilemap-tools
        )
    )
)

if "%choice%"=="3" (
    echo Package pret dans dist/
)

pause