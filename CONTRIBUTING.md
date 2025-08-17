# Guide de Contribution

Merci de votre intérêt pour contribuer à MacTube !

## Comment Contribuer

### Signaler un Bug
- Créez une issue avec une description claire du problème
- Incluez votre version de macOS et de MacTube
- Ajoutez des captures d'écran si applicable

### Demander une Fonctionnalité
- Décrivez le problème que cette fonctionnalité résoudrait
- Proposez une solution
- Considérez les alternatives

### Contribuer au Code
1. Fork le repository
2. Clone votre fork localement
3. Créez une branche pour votre fonctionnalité
4. Faites vos modifications
5. Testez vos changements
6. Commitez avec des messages clairs
7. Créez une Pull Request

## Standards de Code

- Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Testez sur macOS 10.14+
- Respectez les guidelines de design macOS
- Maintenez la compatibilité Intel + Apple Silicon

## Configuration de l'Environnement

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

# Tester l'application
python mactube.py
```

## Messages de Commit

Utilisez des messages clairs et descriptifs :
```
feat: ajouter support pour les playlists YouTube
fix: corriger le problème de téléchargement en 4K
docs: mettre à jour la documentation
style: améliorer la lisibilité du code
```

## Support

Pour toute question, créez une issue sur GitHub ou consultez la documentation existante.

---

**Ensemble, créons la meilleure application de téléchargement YouTube pour macOS !**
