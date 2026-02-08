@echo off
echo Nettoyage...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
for /d %%i in (*.egg-info) do rmdir /s /q "%%i" 2>nul

echo.
echo Construction du package...
python -m build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Construction reussie!
    echo.
    echo Options:
    echo 1. Upload vers TestPyPI
    echo 2. Upload vers PyPI
    echo 3. Arreter ici
    echo.
    set /p choice="Votre choix: "
    
    if "%choice%"=="1" (
        echo Upload vers TestPyPI...
        python -m twine upload --repository testpypi dist/*
    ) else if "%choice%"=="2" (
        set /p confirm="Confirmer upload vers PyPI ? (oui/non): "
        if "%confirm%"=="oui" (
            echo Upload vers PyPI...
            python -m twine upload dist/*
        )
    ) else (
        echo Package pret dans dist/
    )
) else (
    echo Erreur de construction
)

pause