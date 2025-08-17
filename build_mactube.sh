#!/bin/bash

# MacTube - Script de build complet
# Crée l'application .app native et l'installateur DMG
# Compatible macOS 10.14+ (Intel + Apple Silicon)

set -e  # Arrêter en cas d'erreur

echo "MacTube - Build de l'application YouTube Downloader pour macOS"
echo "=============================================================="

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "mactube.py" ]; then
    echo "ERREUR: mactube.py non trouvé. Exécutez ce script depuis le répertoire du projet."
    exit 1
fi

# Vérifier que FFmpeg est présent
if [ ! -f "ffmpeg_binary" ]; then
    echo "ERREUR: FFmpeg non trouvé. Exécutez d'abord download_ffmpeg.sh"
    exit 1
fi

# Vérifier que les icônes sont présentes
if [ ! -f "mactube.icns" ]; then
    echo "ERREUR: mactube.icns non trouvé"
    exit 1
fi

if [ ! -f "mactube.jpeg" ]; then
    echo "ERREUR: mactube.jpeg non trouvé"
    exit 1
fi

echo "SUCCES: Vérifications terminées"

# Nettoyer les builds précédents
echo "INFO: Nettoyage des builds précédents..."
rm -rf build/ dist/ __pycache__/
echo "SUCCES: Nettoyage terminé"

# Activer l'environnement virtuel
echo "INFO: Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "ERREUR: PyInstaller non installé. Installez-le avec: pip install pyinstaller"
    exit 1
fi

echo "SUCCES: PyInstaller disponible"

# Build de l'application
echo "INFO: Build de l'application MacTube..."
pyinstaller mactube.spec

if [ $? -eq 0 ]; then
    echo "SUCCES: Build PyInstaller réussi"
else
    echo "ERREUR: Échec du build PyInstaller"
    exit 1
fi

# Vérifier que l'app a été créée
if [ ! -d "dist/MacTube.app" ]; then
    echo "ERREUR: MacTube.app non créé"
    exit 1
fi

echo "SUCCES: Application MacTube.app créée"

# Afficher la taille de l'application
APP_SIZE=$(du -sh "dist/MacTube.app" | cut -f1)
echo "INFO: Taille de l'application: $APP_SIZE"

# Créer le DMG
echo "INFO: Création de l'installateur DMG..."

# Vérifier create-dmg
if ! command -v create-dmg &> /dev/null; then
    echo "ERREUR: create-dmg non installé. Installez-le avec: brew install create-dmg"
    exit 1
fi

# Créer le DMG
create-dmg \
    --volname "MacTube Installer" \
    --volicon "mactube.icns" \
    --window-pos 200 120 \
    --window-size 800 500 \
    --icon-size 100 \
    --icon "MacTube.app" 200 190 \
    --hide-extension "MacTube.app" \
    --app-drop-link 600 185 \
    --background "mactube.jpeg" \
    "MacTube-Installer.dmg" \
    "dist/"

if [ $? -eq 0 ]; then
    echo "SUCCES: DMG créé"
    
    # Afficher la taille du DMG
    DMG_SIZE=$(du -sh "MacTube-Installer.dmg" | cut -f1)
    echo "INFO: Taille du DMG: $DMG_SIZE"
    
    echo ""
    echo "SUCCES: BUILD TERMINÉ AVEC SUCCÈS"
    echo "=================================="
    echo "Application: dist/MacTube.app"
    echo "Installateur: MacTube-Installer.dmg"
    echo ""
    echo "INFO: Vous pouvez maintenant distribuer MacTube-Installer.dmg"
    echo "INFO: L'application inclut toutes les dépendances (FFmpeg inclus)"
    
else
    echo "ERREUR: Échec de la création du DMG"
    exit 1
fi
