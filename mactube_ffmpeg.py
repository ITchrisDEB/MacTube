#!/usr/bin/env python3
"""
Module de gestion FFmpeg pour MacTube
Gère la détection et l'utilisation de FFmpeg dans le bundle
"""

import os
import sys
import subprocess
from pathlib import Path


def get_ffmpeg_path(verbose: bool = False):
    """
    Retourne le chemin vers FFmpeg selon l'OS
    Priorité: Bundle > Répertoire courant > Système
    """
    # Déterminer le nom du binaire selon l'OS
    if sys.platform == "win32":
        binary_name = "ffmpeg.exe"
    elif sys.platform == "darwin":
        binary_name = "ffmpeg_binary"
    else:
        binary_name = "ffmpeg"  # Linux
    
    # Vérifier si nous sommes dans un bundle PyInstaller
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
        ffmpeg_path = bundle_dir / binary_name
        if ffmpeg_path.exists() and os.access(ffmpeg_path, os.X_OK):
            if verbose:
                print(f"✅ FFmpeg trouvé dans le bundle: {ffmpeg_path}")
            return str(ffmpeg_path)
        
        frameworks_path = Path(sys.executable).parent.parent / "Frameworks" / binary_name
        if frameworks_path.exists() and os.access(frameworks_path, os.X_OK):
            if verbose:
                print(f"✅ FFmpeg trouvé dans Frameworks: {frameworks_path}")
            return str(frameworks_path)
    
    # Répertoire courant (développement)
    current_ffmpeg = Path.cwd() / binary_name
    if current_ffmpeg.exists() and os.access(current_ffmpeg, os.X_OK):
        if verbose:
            print(f"✅ FFmpeg trouvé dans le répertoire courant: {current_ffmpeg}")
        return str(current_ffmpeg)
    
    # Fallback système (optionnel)
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True, check=True)
        system_ffmpeg = result.stdout.strip()
        if system_ffmpeg and os.access(system_ffmpeg, os.X_OK):
            if verbose:
                print(f"✅ FFmpeg trouvé dans le système: {system_ffmpeg}")
            return system_ffmpeg
    except:
        pass
    
    if verbose:
        print("❌ FFmpeg non trouvé")
    return None


if __name__ == "__main__":
    print("🔍 Test de FFmpeg pour MacTube")
    print("=" * 40)
    
    ffmpeg_path = get_ffmpeg_path(verbose=True)
    if ffmpeg_path:
        print(f"✅ FFmpeg trouvé: {ffmpeg_path}")
    else:
        print("❌ FFmpeg non trouvé")
        print("\n💡 Solutions possibles:")
        print("  1. Vérifiez que ffmpeg_binary est présent dans le projet")
        print("  2. Exécutez download_ffmpeg.sh")
