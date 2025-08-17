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
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de la création de l'environnement virtuel"
        echo "💡 Vérifiez que python3-venv est installé"
        read -p "Appuyez sur Entrée pour fermer..."
        exit 1
    fi
    echo "✅ Environnement créé"
fi

# Activer l'environnement
echo "🔧 Activation de l'environnement..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'activation de l'environnement"
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances"
    echo "💡 Essayez de supprimer le dossier venv et relancer le script"
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

# Vérifier FFmpeg
if [ ! -f "ffmpeg_binary" ]; then
    echo "❌ FFmpeg non trouvé"
    echo "💡 Téléchargement automatique..."
    chmod +x download_ffmpeg.sh
    ./download_ffmpeg.sh
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors du téléchargement de FFmpeg"
        echo "💡 Vérifiez votre connexion internet"
        read -p "Appuyez sur Entrée pour fermer..."
        exit 1
    fi
else
    echo "✅ FFmpeg trouvé"
    chmod +x ffmpeg_binary
fi

echo ""
echo "🎯 Lancement de MacTube..."
echo ""

# Lancer l'application
python3 mactube.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erreur lors du lancement de MacTube"
    echo "💡 Vérifiez que toutes les dépendances sont installées"
    read -p "Appuyez sur Entrée pour fermer..."
    exit 1
fi

echo ""
echo "👋 MacTube fermé"
echo "Appuyez sur Entrée pour fermer cette fenêtre..."
read
