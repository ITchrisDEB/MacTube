@echo off
REM MacTube - Lancement par double-clic pour Windows
REM Ce fichier peut être double-cliqué pour lancer MacTube

REM Aller dans le répertoire du script
cd /d "%~dp0"

echo [INFO] MacTube - YouTube Downloader pour Windows
echo ============================================
echo.

REM Python est supposé etre installe sur la machine
echo [OK] Python detecte
echo.

REM Créer l'environnement virtuel si nécessaire
if not exist "venv" (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERREUR] Erreur lors de la creation de l'environnement virtuel
        echo [ASTUCE] Verifiez que python-venv est installe
        pause
        exit /b 1
    )
    echo [OK] Environnement cree
)

REM Activer l'environnement
echo [INFO] Activation de l'environnement...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Erreur lors de l'activation de l'environnement
    pause
    exit /b 1
)

REM Installer les dependances
echo [INFO] Installation des dependances...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Erreur lors de l'installation des dependances
    echo [ASTUCE] Essayez de supprimer le dossier venv et relancer le script
    pause
    exit /b 1
)

REM Verifier FFmpeg
if not exist "ffmpeg.exe" (
    echo [ERREUR] FFmpeg non trouve
    echo [ASTUCE] Telechargement automatique...
    call download_ffmpeg.bat
    if %ERRORLEVEL% NEQ 0 (
        echo [ERREUR] Erreur lors du telechargement de FFmpeg
        echo [ASTUCE] Verifiez votre connexion internet
        pause
        exit /b 1
    )
) else (
    echo [OK] FFmpeg trouve
)

echo.
echo [INFO] Lancement de MacTube...
echo.

REM Lancer l'application
python mactube.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Erreur lors du lancement de MacTube
    echo [ASTUCE] Verifiez que toutes les dependances sont installees
    pause
    exit /b 1
)

echo.
echo [INFO] MacTube ferme
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul
