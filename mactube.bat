@echo off
REM MacTube - Lancement par double-clic pour Windows
REM Ce fichier peut être double-cliqué pour lancer MacTube

REM Aller dans le répertoire du script
cd /d "%~dp0"

echo 🚀 MacTube - YouTube Downloader pour Windows
echo ============================================
echo.

REM Python est supposé être installé sur la machine
echo ✅ Python détecté
echo.

REM Créer l'environnement virtuel si nécessaire
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Erreur lors de la création de l'environnement virtuel
        echo 💡 Vérifiez que python-venv est installé
        pause
        exit /b 1
    )
    echo ✅ Environnement créé
)

REM Activer l'environnement
echo 🔧 Activation de l'environnement...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de l'activation de l'environnement
    pause
    exit /b 1
)

REM Installer les dépendances
echo 📥 Installation des dépendances...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de l'installation des dépendances
    echo 💡 Essayez de supprimer le dossier venv et relancer le script
    pause
    exit /b 1
)

REM Vérifier FFmpeg
if not exist "ffmpeg.exe" (
    echo ❌ FFmpeg non trouvé
    echo 💡 Téléchargement automatique...
    call download_ffmpeg.bat
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Erreur lors du téléchargement de FFmpeg
        echo 💡 Vérifiez votre connexion internet
        pause
        exit /b 1
    )
) else (
    echo ✅ FFmpeg trouvé
)

echo.
echo 🎯 Lancement de MacTube...
echo.

REM Lancer l'application
python mactube.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erreur lors du lancement de MacTube
    echo 💡 Vérifiez que toutes les dépendances sont installées
    pause
    exit /b 1
)

echo.
echo 👋 MacTube fermé
echo Appuyez sur une touche pour fermer cette fenêtre...
pause >nul
