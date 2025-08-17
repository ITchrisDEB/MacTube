#!/bin/bash

# MacTube - Lancement par double-clic
# Ce fichier peut être double-cliqué pour lancer MacTube

# Aller dans le répertoire du script
cd "$(dirname "$0")"

echo "🚀 MacTube - YouTube Downloader pour macOS"
echo "=========================================="
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trouvé sur votre Mac"
    echo ""
    echo "💡 INSTALLATION AUTOMATIQUE :"
    echo "1. Installez Python depuis https://www.python.org/downloads/"
    echo "2. Redémarrez ce script"
    echo ""
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo "✅ Python 3 trouvé"
echo ""

# Créer l'environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✅ Environnement créé"
fi

# Activer l'environnement
echo "🔧 Activation de l'environnement..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier FFmpeg
if [ ! -f "ffmpeg_binary" ]; then
    echo "❌ FFmpeg non trouvé"
    echo "💡 Téléchargement automatique..."
    chmod +x download_ffmpeg.sh
    ./download_ffmpeg.sh
else
    echo "✅ FFmpeg trouvé"
    chmod +x ffmpeg_binary
fi

echo ""
echo "🎯 Lancement de MacTube..."
echo ""

# Lancer l'application
python3 mactube.py

echo ""
echo "👋 MacTube fermé"
echo "Appuyez sur Entrée pour fermer cette fenêtre..."
read
