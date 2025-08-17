# MacTube - YouTube Downloader pour macOS

<div align="center">

![macOS](https://img.shields.io/badge/macOS-10.14+-000000?style=for-the-badge&logo=apple&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

**Une application native macOS élégante et moderne pour télécharger des vidéos YouTube en haute qualité**

</div>

---

## ✨ Fonctionnalités

- **Interface native macOS** avec thèmes clair/sombre automatiques
- **Navigation par onglets** organisée (Télécharger, Historique, File d'attente, Paramètres)
- **Téléchargement HD** jusqu'à 4K avec `yt-dlp`
- **File d'attente** pour téléchargements multiples
- **Historique persistant** des téléchargements
- **Formats multiples** : MP4, MKV, WebM, AVI
- **FFmpeg intégré** pour la conversion automatique
- **Aucune installation système** requise

---

## 🖼️ Aperçu de l'interface

<div align="center">

![Interface MacTube](screenshots/MacTube.png)


</div>

---

## 🚀 Installation

### 🚀 Lancement Rapide (Recommandé pour débutants)
```bash
# Cloner le projet
git clone https://github.com/ITchrisDEB/MacTube.git
cd MacTube

# Double-cliquer sur mactube.sh OU exécuter :
./mactube.sh
```

**Le script `mactube.sh` fait TOUT automatiquement :**
- ✅ Vérifie Python 3
- ✅ Crée l'environnement virtuel
- ✅ Installe les dépendances
- ✅ Configure FFmpeg
- ✅ Lance l'application

### Option 1 : Installateur DMG (Recommandé)
1. Téléchargez `MacTube-Installer.dmg`
2. Ouvrez le DMG et glissez `MacTube.app` vers Applications
3. Lancez depuis Applications

### Option 2 : Build depuis les sources
```bash
# Cloner le projet
git clone https://github.com/ITchrisDEB/mactube.git
cd mactube

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Télécharger FFmpeg
./download_ffmpeg.sh

# Build de l'application
./build_mactube.sh
```

---

## 📋 Prérequis

- **macOS** 10.14+ (Mojave)
- **Python** 3.8+ (pour le build)
- **FFmpeg** (inclus dans le bundle)

---

## 🆘 Dépannage

### Problèmes courants

**❌ "Python 3 non trouvé"**
```bash
# Installer Python depuis https://www.python.org/downloads/
# Redémarrer le terminal puis relancer mactube.sh
```

**❌ "Permission denied" sur mactube.sh**
```bash
chmod +x mactube.sh
```

**❌ Erreurs de dépendances**
```bash
# Supprimer et recréer l'environnement virtuel
rm -rf venv
./mactube.sh
```

**❌ FFmpeg manquant**
```bash
# Le script télécharge automatiquement FFmpeg
# Si problème, exécuter manuellement :
./download_ffmpeg.sh
```

### Support
- **Issues GitHub** : [Signaler un bug](https://github.com/ITchrisDEB/MacTube/issues)
- **Discussions** : [Demander de l'aide](https://github.com/ITchrisDEB/MacTube/discussions)

---

## 🏗️ Architecture

### Structure du projet
```
mactube/
├── mactube.py              # Application principale
├── mactube_theme.py        # Gestion des thèmes
├── mactube_components.py   # Composants UI
├── mactube_ffmpeg.py       # Gestion FFmpeg
├── mactube.spec            # Configuration PyInstaller
├── build_mactube.sh        # Script de build
└── requirements.txt        # Dépendances Python
```

### Technologies
- **Python 3.12** avec environnement virtuel
- **CustomTkinter** pour l'interface moderne
- **yt-dlp** pour le téléchargement YouTube
- **FFmpeg** pour la conversion audio/vidéo
- **PyInstaller** pour le packaging

### FFmpeg intégré
- **FFmpeg portable** inclus dans le projet
- **Aucune dépendance système** requise
- **Conversion automatique** vidéo + audio
- **Support des formats** MP4, MKV, WebM, AVI

---

## 📦 Build et distribution

### Scripts automatisés
```bash
./download_ffmpeg.sh    # Télécharge FFmpeg portable
./build_mactube.sh      # Build complet + DMG
```

### Résultat
- **`dist/MacTube.app`** - Application native (125 MB)
- **`MacTube-Installer.dmg`** - Installateur (99 MB)

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Moteur de téléchargement YouTube
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Interface graphique moderne
- [FFmpeg](https://ffmpeg.org/) - Traitement audio/vidéo

---

<div align="center">

**MacTube** - Téléchargez YouTube en beauté sur macOS

[![GitHub](https://img.shields.io/badge/GitHub-ITchrisDEB-181717?style=for-the-badge&logo=github)](https://github.com/ITchrisDEB)

</div>
