#!/bin/bash

# MacTube - Script de téléchargement FFmpeg portable
# Télécharge et configure FFmpeg pour le build de l'application
# Compatible macOS 10.14+ (Intel + Apple Silicon)

set -e  # Arrêter en cas d'erreur

echo "MacTube - Téléchargement FFmpeg portable pour macOS"
echo "=================================================="

# Créer le répertoire de travail
mkdir -p ffmpeg_bundle
cd ffmpeg_bundle

# URL de FFmpeg portable pour macOS (version statique)
FFMPEG_URL="https://evermeet.cx/ffmpeg/getrelease/zip"
FFMPEG_ZIP="ffmpeg.zip"

echo "Téléchargement de FFmpeg..."
curl -L -o "$FFMPEG_ZIP" "$FFMPEG_URL"

if [ $? -eq 0 ]; then
    echo "SUCCES: Téléchargement terminé"
    
    echo "Extraction de l'archive..."
    unzip -q "$FFMPEG_ZIP"
    
    if [ $? -eq 0 ]; then
        echo "SUCCES: Extraction terminée"
        
        # Trouver l'exécutable FFmpeg
        FFMPEG_BIN=$(find . -name "ffmpeg" -type f | head -1)
        
        if [ -n "$FFMPEG_BIN" ]; then
            echo "INFO: FFmpeg trouvé: $FFMPEG_BIN"
            
            # Rendre exécutable
            chmod +x "$FFMPEG_BIN"
            
            # Copier vers le répertoire principal
            cp "$FFMPEG_BIN" "../ffmpeg_binary"
            
            echo "SUCCES: FFmpeg copié vers le répertoire principal"
            echo "INFO: Emplacement: $(pwd)/../ffmpeg_binary"
            
            # Nettoyer
            cd ..
            rm -rf ffmpeg_bundle
            
            echo "INFO: Nettoyage terminé"
            echo "SUCCES: FFmpeg portable prêt pour le bundle"
            
        else
            echo "ERREUR: FFmpeg exécutable non trouvé"
            exit 1
        fi
    else
        echo "ERREUR: Échec de l'extraction"
        exit 1
    fi
else
    echo "ERREUR: Échec du téléchargement"
    exit 1
fi
