#!/usr/bin/env python3
"""
Module de gestion FFmpeg pour MacTube
Gère la détection et l'utilisation de FFmpeg dans le bundle
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def get_ffmpeg_path():
    """
    Retourne le chemin vers FFmpeg
    Priorité: Bundle > Système > Erreur
    """
    # Vérifier si nous sommes dans un bundle PyInstaller
    if getattr(sys, 'frozen', False):
        # Application est "frozen" (bundle PyInstaller)
        bundle_dir = Path(sys._MEIPASS)
        
        # Essayer d'abord dans le répertoire courant du bundle
        ffmpeg_path = bundle_dir / "ffmpeg_binary"
        if ffmpeg_path.exists() and os.access(ffmpeg_path, os.X_OK):
            print(f"✅ FFmpeg trouvé dans le bundle (MEIPASS): {ffmpeg_path}")
            return str(ffmpeg_path)
        
        # Essayer dans Frameworks (structure .app)
        frameworks_path = Path(sys.executable).parent.parent / "Frameworks" / "ffmpeg_binary"
        if frameworks_path.exists() and os.access(frameworks_path, os.X_OK):
            print(f"✅ FFmpeg trouvé dans Frameworks: {frameworks_path}")
            return str(frameworks_path)
    
    # Essayer le répertoire courant (pour le développement)
    current_ffmpeg = Path.cwd() / "ffmpeg_binary"
    if current_ffmpeg.exists() and os.access(current_ffmpeg, os.X_OK):
        print(f"✅ FFmpeg trouvé dans le répertoire courant: {current_ffmpeg}")
        return str(current_ffmpeg)
    
    # Essayer le système
    try:
        result = subprocess.run(['which', 'ffmpeg'], 
                              capture_output=True, text=True, check=True)
        system_ffmpeg = result.stdout.strip()
        if system_ffmpeg and os.access(system_ffmpeg, os.X_OK):
            print(f"✅ FFmpeg trouvé dans le système: {system_ffmpeg}")
            return system_ffmpeg
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Essayer Homebrew
    try:
        homebrew_ffmpeg = "/usr/local/bin/ffmpeg"
        if os.path.exists(homebrew_ffmpeg) and os.access(homebrew_ffmpeg, os.X_OK):
            print(f"✅ FFmpeg trouvé via Homebrew: {homebrew_ffmpeg}")
            return homebrew_ffmpeg
    except:
        pass
    
    # FFmpeg non trouvé
    print("❌ FFmpeg non trouvé")
    return None


def test_ffmpeg():
    """
    Teste si FFmpeg fonctionne correctement
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return False, "FFmpeg non trouvé"
    
    try:
        result = subprocess.run([ffmpeg_path, '-version'], 
                              capture_output=True, text=True, check=True)
        version_line = result.stdout.split('\n')[0]
        print(f"✅ FFmpeg test réussi: {version_line}")
        return True, version_line
    except subprocess.CalledProcessError as e:
        error_msg = f"Erreur FFmpeg: {e.stderr}"
        print(f"❌ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Erreur inattendue: {e}"
        print(f"❌ {error_msg}")
        return False, error_msg


def get_ffmpeg_info():
    """
    Retourne les informations détaillées sur FFmpeg
    """
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return None
    
    info = {
        'path': ffmpeg_path,
        'type': 'bundle' if ('MEIPASS' in ffmpeg_path or 'Frameworks' in ffmpeg_path) else 'system',
        'platform': platform.system(),
        'architecture': platform.machine(),
    }
    
    # Tester les fonctionnalités
    try:
        # Test de base
        result = subprocess.run([ffmpeg_path, '-version'], 
                              capture_output=True, text=True, check=True)
        info['version'] = result.stdout.split('\n')[0]
        
        # Test des codecs
        result = subprocess.run([ffmpeg_path, '-codecs'], 
                              capture_output=True, text=True, check=True)
        info['codecs_available'] = True
        
        # Test des formats
        result = subprocess.run([ffmpeg_path, '-formats'], 
                              capture_output=True, text=True, check=True)
        info['formats_available'] = True
        
    except Exception as e:
        info['error'] = str(e)
    
    return info


if __name__ == "__main__":
    print("🔍 Test de FFmpeg pour MacTube")
    print("=" * 40)
    
    success, message = test_ffmpeg()
    if success:
        print(f"✅ FFmpeg fonctionne: {message}")
        
        info = get_ffmpeg_info()
        if info:
            print("\n📋 Informations FFmpeg:")
            for key, value in info.items():
                print(f"  {key}: {value}")
    else:
        print(f"❌ FFmpeg échoue: {message}")
        print("\n💡 Solutions possibles:")
        print("  1. Vérifiez que FFmpeg est installé")
        print("  2. Exécutez download_ffmpeg.sh")
        print("  3. Installez FFmpeg via Homebrew: brew install ffmpeg")
