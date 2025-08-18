#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacTube Audio - Module d'extraction audio pour MacTube
Interface dédiée à l'extraction audio depuis YouTube
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import yt_dlp
from pathlib import Path

# Imports personnalisés
from mactube_theme import MacTubeTheme
from mactube_ffmpeg import get_ffmpeg_path

# Pas d'imports spéciaux nécessaires

class MacTubeAudioExtractor:
    """Interface d'extraction audio pour MacTube"""
    
    def __init__(self, parent, app=None):
        self.parent = parent
        # Référence optionnelle vers l'application principale pour accéder à la file d'attente
        self.app = app
        self.is_extracting = False
        self.download_path = str(Path.home() / "Downloads")
        # Récupérer le chemin FFmpeg depuis l'app si disponible
        self.ffmpeg_path = getattr(app, 'ffmpeg_path', None) if app else None
        self.create_audio_interface()
        # Appliquer le thème courant dès la création
        try:
            self.update_theme()
        except Exception:
            pass
    
    def create_audio_interface(self):
        """Crée l'interface d'extraction audio"""
        # Frame principal
        self.audio_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Carte d'extraction audio
        self.audio_card = MacTubeTheme.create_card_frame(self.audio_frame)
        self.audio_card.pack(fill="x", pady=(0, 20))
        
        # Titre de la carte
        MacTubeTheme.create_label_section(
            self.audio_card,
            "Extraction Audio YouTube"
        ).pack(pady=(20, 15), padx=20, anchor="w")
        
        # Contenu de la carte
        content_frame = ctk.CTkFrame(self.audio_card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # URL YouTube
        url_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        url_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(url_frame, "URL YouTube :").pack(side="left")
        
        self.url_entry = MacTubeTheme.create_entry_modern(
            url_frame,
            "Collez l'URL de la vidéo YouTube ici..."
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        self.analyze_button = MacTubeTheme.create_button_primary(
            url_frame,
            "Analyser",
            command=self.analyze_audio,
            width=100
        )
        self.analyze_button.pack(side="right")
        
        # Options d'extraction
        options_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 15))
        
        # Format audio
        format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(format_frame, "Format audio :").pack(side="left")
        
        self.format_combo = ctk.CTkComboBox(
            format_frame,
            values=[".mp3", ".aac", ".flac", ".wav", ".m4a", ".ogg"],
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=200
        )
        self.format_combo.pack(side="right")
        self.format_combo.set(".mp3")
        self.format_combo.configure(command=self.on_format_change)
        
        # Qualité audio
        quality_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        quality_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(quality_frame, "Qualité audio :").pack(side="left")
        
        self.quality_combo = ctk.CTkComboBox(
            quality_frame,
            values=["128 kbps", "192 kbps", "320 kbps"],
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=200
        )
        self.quality_combo.pack(side="right")
        self.quality_combo.set("192 kbps")
        
        # Nom du fichier
        filename_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        filename_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(filename_frame, "Nom du fichier :").pack(side="left")
        
        self.filename_entry = MacTubeTheme.create_entry_modern(
            filename_frame,
            "Nom personnalisé (optionnel)"
        )
        self.filename_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        # Dossier de destination
        dest_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        dest_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(dest_frame, "Dossier de destination :").pack(side="left")
        
        self.dest_entry = ctk.CTkEntry(
            dest_frame,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            height=35,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary')
        )
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.dest_entry.insert(0, self.download_path)
        
        self.choose_button = MacTubeTheme.create_button_secondary(
            dest_frame,
            "Choisir...",
            command=self.choose_destination,
            width=100
        )
        self.choose_button.pack(side="right")
        
        # Bouton d'extraction
        extract_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        extract_frame.pack(fill="x", pady=(20, 0))
        
        self.extract_button = MacTubeTheme.create_button_success(
            extract_frame,
            "Extraire l'audio",
            command=self.extract_audio,
            width=200
        )
        self.extract_button.pack(expand=True)
        
        # Séparateur
        separator_frame = ctk.CTkFrame(content_frame, fg_color=MacTubeTheme.get_color('border'), height=1)
        separator_frame.pack(fill="x", pady=(30, 20))
        
        # Section Upload en Bulk
        bulk_title = MacTubeTheme.create_label_section(
            content_frame,
            "📁 Extraction Audio en Bulk"
        )
        bulk_title.pack(pady=(0, 10), anchor="w")
        
        # Interface pour l'upload bulk
        upload_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        upload_frame.pack(fill="x", pady=(0, 15))
        
        # Bouton d'upload principal
        self.upload_button = MacTubeTheme.create_button_primary(
            upload_frame,
            "📁 Sélectionner un fichier",
            command=self.browse_bulk_file,
            width=250
        )
        self.upload_button.pack(pady=(10, 15))
        
        # Label d'information du fichier sélectionné (sans cadre)
        self.file_info_label = MacTubeTheme.create_label_body(
            upload_frame,
            "Aucun fichier sélectionné"
        )
        self.file_info_label.pack(pady=(0, 15))
        
        # Contrôles de format et qualité pour le bulk
        bulk_controls_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        bulk_controls_frame.pack(fill="x", pady=(0, 15))
        
        # Format audio pour le bulk
        format_frame = ctk.CTkFrame(bulk_controls_frame, fg_color="transparent")
        format_frame.pack(side="left", padx=(0, 20))
        
        format_label = MacTubeTheme.create_label_body(format_frame, "Format:")
        format_label.pack(side="left", padx=(0, 10))
        
        self.bulk_format_combo = ctk.CTkComboBox(
            format_frame,
            values=[".mp3", ".m4a", ".aac", ".flac", ".wav", ".ogg"],
            command=self.on_bulk_format_change,
            width=80
        )
        self.bulk_format_combo.set(".mp3")
        self.bulk_format_combo.pack(side="left")
        
        # Qualité audio pour le bulk
        quality_frame = ctk.CTkFrame(bulk_controls_frame, fg_color="transparent")
        quality_frame.pack(side="left")
        
        quality_label = MacTubeTheme.create_label_body(quality_frame, "Qualité:")
        quality_label.pack(side="left", padx=(0, 10))
        
        self.bulk_quality_combo = ctk.CTkComboBox(
            quality_frame,
            values=["128 kbps", "192 kbps", "256 kbps", "320 kbps", "Qualité maximale"],
            width=100
        )
        self.bulk_quality_combo.set("192 kbps")
        self.bulk_quality_combo.pack(side="left")
        
        # Bouton de traitement
        self.process_bulk_button = MacTubeTheme.create_button_success(
            upload_frame,
            "🚀 Traiter le fichier",
            command=self.process_bulk_file,
            width=200
        )
        self.process_bulk_button.pack(pady=(0, 20))
        
        # Variables pour le bulk
        self.bulk_file_path = None
        self.bulk_urls = []
        
        # Barre de progression
        self.progress_bar = MacTubeProgressBar(extract_frame)
        self.progress_bar.hide()
        
        # Label de statut
        self.status_label = MacTubeTheme.create_label_body(
            extract_frame,
            "Prêt à extraire l'audio d'une vidéo YouTube"
        )
        self.status_label.pack(pady=(10, 0))
    
    def on_format_change(self, value):
        """Gère le changement de format audio"""
        if value in [".flac", ".wav", ".m4a"]:
            # Formats lossless - griser la qualité
            self.quality_combo.configure(state="disabled")
            self.quality_combo.set("Qualité maximale")
        else:
            # Formats avec compression - activer la qualité
            self.quality_combo.configure(state="readonly")
            if self.quality_combo.get() == "Qualité maximale":
                self.quality_combo.set("192 kbps")
    
    def on_bulk_format_change(self, value):
        """Gère le changement de format audio pour le bulk"""
        if value in [".flac", ".wav", ".m4a"]:
            # Formats lossless - griser la qualité
            self.bulk_quality_combo.configure(state="disabled")
            self.bulk_quality_combo.set("Qualité maximale")
        else:
            # Formats avec compression - activer la qualité
            self.bulk_quality_combo.configure(state="readonly")
            if self.bulk_quality_combo.get() == "Qualité maximale":
                self.bulk_quality_combo.set("192 kbps")
    
    def choose_destination(self):
        """Ouvre le dialogue de sélection de dossier"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)
    
    def analyze_audio(self):
        """Analyse la vidéo pour l'extraction audio"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Erreur", "Veuillez saisir une URL YouTube")
            return
        
        if not self.validate_youtube_url(url):
            messagebox.showerror("Erreur", "URL YouTube invalide")
            return
        
        # Nettoyer l'URL avant l'analyse
        clean_url = self.clean_youtube_url(url)
        print(f"🔧 URL originale: {url}")
        print(f"🔧 URL nettoyée: {clean_url}")
        
        # Désactiver le bouton pendant l'analyse
        self.analyze_button.configure(state="disabled", text="Analyse...")
        self.status_label.configure(text="Analyse de la vidéo en cours...")
        
        # Lancer l'analyse dans un thread avec l'URL nettoyée
        threading.Thread(target=self._analyze_audio_thread, args=(clean_url,), daemon=True).start()

    def update_theme(self):
        """Applique les couleurs du thème aux composants audio"""
        try:
            # Couleurs de base
            bg_primary = MacTubeTheme.get_color('bg_primary')
            bg_secondary = MacTubeTheme.get_color('bg_secondary')
            bg_card = MacTubeTheme.get_color('bg_card')
            text_primary = MacTubeTheme.get_color('text_primary')
            text_secondary = MacTubeTheme.get_color('text_secondary')

            # Fond principal de l'onglet
            if hasattr(self, 'audio_frame'):
                self.audio_frame.configure(fg_color=bg_primary)

            # Carte principale
            if hasattr(self, 'audio_card'):
                self.audio_card.configure(fg_color=bg_card, border_color=text_secondary)

            # Entrées
            for entry in [getattr(self, 'url_entry', None), getattr(self, 'filename_entry', None), getattr(self, 'dest_entry', None)]:
                if entry is not None:
                    try:
                        entry.configure(fg_color=bg_secondary, border_color=text_secondary, text_color=text_primary)
                        # Certains widgets supportent placeholder_text_color
                        entry.configure(placeholder_text_color=text_secondary)
                    except Exception:
                        pass

            # Combobox
            for combo in [getattr(self, 'format_combo', None), getattr(self, 'quality_combo', None)]:
                if combo is not None:
                    try:
                        combo.configure(fg_color=bg_secondary, border_color=text_secondary, text_color=text_primary)
                    except Exception:
                        pass

            # Boutons
            for button in [getattr(self, 'analyze_button', None), getattr(self, 'choose_button', None), getattr(self, 'extract_button', None)]:
                if button is not None:
                    try:
                        button.configure(text_color=MacTubeTheme.get_color('text_light'))
                    except Exception:
                        pass

            # Texte de statut
            if hasattr(self, 'status_label'):
                try:
                    self.status_label.configure(text_color=text_primary)
                except Exception:
                    pass

            # Barre de progression
            if hasattr(self, 'progress_bar') and hasattr(self.progress_bar, 'update_theme'):
                self.progress_bar.update_theme()
        except Exception:
            # Ne jamais bloquer l'UI sur une mise à jour de thème
            pass
    
    def _analyze_audio_thread(self, url):
        """Thread pour l'analyse audio avec yt-dlp"""
        try:
            # Obtenir le chemin FFmpeg du projet
            ffmpeg_path = get_ffmpeg_path()
            if not ffmpeg_path:
                print("⚠️ FFmpeg non trouvé dans le projet, utilisation du système")
            else:
                print(f"🔧 Utilisation de FFmpeg: {ffmpeg_path}")
            
            # Configuration yt-dlp pour l'audio
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            # Ajouter FFmpeg du projet si disponible
            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extraire les informations
                info = ydl.extract_info(url, download=False)
                
                # Récupérer les informations de base
                title = info.get('title', 'Titre inconnu')
                duration = info.get('duration', 0)
                channel = info.get('uploader', 'Chaîne inconnue')
                
                # Mettre à jour l'interface
                self.parent.after(0, self._update_audio_info, title, duration, channel)
                
        except Exception as e:
            self.parent.after(0, self._show_error, f"Erreur lors de l'analyse : {str(e)}")
    
    def _update_audio_info(self, title, duration, channel):
        """Met à jour l'interface avec les informations audio"""
        self.analyze_button.configure(state="normal", text="Analyser")
        self.status_label.configure(text=f"✅ Audio analysé - {title}")
        
        # Activer le bouton d'extraction
        self.extract_button.configure(state="normal")
    
    def extract_audio(self):
        """Lance l'extraction audio"""
        if self.is_extracting:
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erreur", "Veuillez d'abord analyser une vidéo")
            return
        
        self.is_extracting = True
        self.extract_button.configure(state="disabled", text="Extraction...")
        self.progress_bar.show()
        
        # Nettoyer l'URL pour enlever les paramètres (playlist, start_radio, etc.)
        clean_url = self.clean_youtube_url(url)
        print(f"🔧 URL originale: {url}")
        print(f"🔧 URL nettoyée: {clean_url}")

        # Au lieu d'exécuter directement, ajouter à la file d'attente commune si l'app est disponible
        try:
            app = getattr(self, 'app', None)
            if app is None or not hasattr(app, 'add_to_queue'):
                # Fallback: thread direct si pas de file d'attente disponible
                quality = self.quality_combo.get()
                threading.Thread(target=self._extract_audio_thread, args=(clean_url, quality), daemon=True).start()
                return

            # Construire les paramètres de tâche
            quality = self.quality_combo.get()
            output_format = self.format_combo.get()
            filename = self.filename_entry.get().strip() or "%(title)s"
            download_path = self.dest_entry.get().strip() or self.download_path

            # Ajouter la tâche à la file (type audio)
            app.add_to_queue(clean_url, quality, output_format, filename, download_path, task_type="audio")
            self.status_label.configure(text="✅ Ajouté à la file d'attente audio")
            self.extract_button.configure(text="🎵 Ajouté à la file")
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout à la file d'attente: {e}")
            # En cas d'échec, continuer en thread direct
            quality = self.quality_combo.get()
            threading.Thread(target=self._extract_audio_thread, args=(clean_url, quality), daemon=True).start()
    
    def _extract_audio_thread(self, url, quality=None):
        """Thread pour l'extraction audio"""
        try:
            # Sécuriser la qualité si non fournie (anciens appels / fallback)
            if not quality:
                try:
                    quality = self.quality_combo.get()
                except Exception:
                    quality = "192"  # défaut

            # Utiliser le chemin FFmpeg stocké ou le récupérer si nécessaire
            ffmpeg_path = self.ffmpeg_path or get_ffmpeg_path()
            
            # Configuration yt-dlp pour l'audio
            format_selector = self._get_audio_format_selector()
            output_format = self.format_combo.get().lstrip('.')
            
            # Chemin de sortie avec nom de fichier (sans ID)
            filename = self.filename_entry.get().strip()
            if not filename or filename == "Nom personnalisé (optionnel)":
                filename = "%(title)s"
            
            # Construire le chemin de sortie sécurisé
            output_path = os.path.join(self.download_path, filename)
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': output_path + '.%(ext)s',
                'quiet': False,  # Activer les logs pour debug
                'no_warnings': False,
                'ignoreerrors': False,
                # Post-processeur audio avec gestion d'erreur
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    # Mapper ".ogg" vers le codec FFmpeg 'vorbis'
                    'preferredcodec': ('vorbis' if output_format == 'ogg' else output_format),
                    'preferredquality': self._get_ffmpeg_quality(quality),
                }],
                'keepvideo': False,
                # Gestion des erreurs de fichier
                'nopart': True,  # Éviter les fichiers .part
                'writethumbnail': False,
                # Garder les caractères usuels du titre (macOS ok)
                'trim_file_name': 180,
            }
            
            # Ajouter FFmpeg du projet si disponible
            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path
            
            # Hook de progression
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes']:
                        percent = d['downloaded_bytes'] / d['total_bytes']
                        self.parent.after(0, self.progress_bar.update_progress, "Téléchargement...", percent)
                elif d['status'] == 'finished':
                    self.parent.after(0, self.progress_bar.update_progress, "Conversion audio...", 0.9)
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            # Mettre à jour le statut
            self.parent.after(0, self.progress_bar.update_progress, "Début de l'extraction...", 0)
            
            # Nettoyer les fichiers potentiellement existants avant de commencer
            self._cleanup_temp_files(output_path)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Nettoyer les fichiers temporaires après téléchargement
            self._cleanup_temp_files(output_path)
            
            # Terminé
            self.parent.after(0, self._extraction_complete, output_path)
            
        except Exception as e:
            # Nettoyer en cas d'erreur
            try:
                self._cleanup_temp_files(output_path)
            except:
                pass
            
            # Gérer spécifiquement l'erreur de renommage
            error_msg = str(e)
            if "Unable to rename file" in error_msg:
                error_msg = "Erreur de fichier temporaire - Tentative de nettoyage..."
                # Nettoyer et réessayer une fois
                try:
                    self._cleanup_temp_files(output_path)
                    print("🧹 Nettoyage des fichiers temporaires effectué")
                except:
                    pass
            
            self.parent.after(0, self._show_error, f"Erreur lors de l'extraction : {error_msg}")
    
    def _get_audio_format_selector(self):
        """Retourne le sélecteur de format yt-dlp pour l'audio"""
        format_type = self.format_combo.get().lstrip('.')
        quality = self.quality_combo.get()
        
        # Toujours télécharger le meilleur format audio disponible
        # La conversion sera faite par FFmpeg vers le format demandé
        if '128' in quality:
            return "bestaudio[abr<=128]/bestaudio"
        elif '192' in quality:
            return "bestaudio[abr<=192]/bestaudio"
        elif '320' in quality:
            return "bestaudio[abr<=320]/bestaudio"
        else:
            return "bestaudio"
    
    def _extraction_complete(self, output_path):
        """Appelé quand l'extraction est terminée"""
        self.is_extracting = False
        self.extract_button.configure(state="normal", text="Extraire l'audio")
        self.progress_bar.hide()
        self.status_label.configure(text="✅ Extraction audio terminée avec succès !")
        
        # Notification
        messagebox.showinfo("Extraction terminée", f"Audio extrait avec succès !\n\nEmplacement: {output_path}")
    
    def _show_error(self, error_msg):
        """Affiche une erreur"""
        self.is_extracting = False
        self.extract_button.configure(state="normal", text="Extraire l'audio")
        self.progress_bar.hide()
        self.status_label.configure(text="❌ Erreur lors de l'extraction")
        messagebox.showerror("Erreur d'extraction", error_msg)
    
    def clean_youtube_url(self, url):
        """Nettoie l'URL YouTube en supprimant les paramètres de playlist"""
        import re
        
        # Solution simple et efficace : couper avant &list=
        if '&list=' in url:
            clean_url = url.split('&list=')[0]
            print(f"🔧 URL nettoyée (suppression playlist): {url} → {clean_url}")
            return clean_url
        
        # Si pas de &list=, vérifier s'il y a d'autres paramètres problématiques
        if '&start_radio=' in url or '&feature=' in url or '&ab_channel=' in url:
            # Extraire l'ID de la vidéo et reconstruire une URL propre
            match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})', url)
            if match:
                video_id = match.group(1)
                clean_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"🔧 URL nettoyée (suppression paramètres): {url} → {clean_url}")
                return clean_url
        
        # Si l'URL est déjà propre, la retourner telle quelle
        print(f"✅ URL déjà propre: {url}")
        return url
    
    def _get_ffmpeg_quality(self, quality_str):
        """Convertit la qualité en paramètre FFmpeg"""
        if '128' in quality_str:
            return '128'
        elif '192' in quality_str:
            return '192'
        elif '320' in quality_str:
            return '320'
        else:
            return '192'  # Qualité par défaut
    
    def _cleanup_temp_files(self, base_path):
        """Nettoie les fichiers temporaires et .part de manière agressive"""
        try:
            # Chercher et supprimer les fichiers .part
            for ext in ['.webm.part', '.mp3.part', '.m4a.part', '.aac.part', '.ogg.part', '.part']:
                part_file = base_path + ext
                if os.path.exists(part_file):
                    os.remove(part_file)
                    print(f"🧹 Fichier temporaire supprimé: {part_file}")
            
            # Chercher et supprimer les fichiers sans extension
            no_ext_file = base_path
            if os.path.exists(no_ext_file):
                os.remove(no_ext_file)
                print(f"🧹 Fichier sans extension supprimé: {no_ext_file}")
            
            # Chercher et supprimer les fichiers avec des noms problématiques
            problematic_patterns = [
                base_path + '.webm',
                base_path + '.mp3',
                base_path + '.m4a',
                base_path + '.aac',
                base_path + '.ogg'
            ]
            
            for pattern in problematic_patterns:
                if os.path.exists(pattern):
                    try:
                        os.remove(pattern)
                        print(f"🧹 Fichier problématique supprimé: {pattern}")
                    except:
                        pass
                
        except Exception as e:
            print(f"⚠️  Erreur lors du nettoyage: {e}")
    
    def validate_youtube_url(self, url):
        """Valide l'URL YouTube avec une validation robuste"""
        import re
        
        # Nettoyer d'abord l'URL
        clean_url = self.clean_youtube_url(url)
        
        # Vérifier que c'est une URL YouTube valide
        patterns = [
            r'youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}',  # ID exactement 11 caractères
            r'youtu\.be/[a-zA-Z0-9_-]{11}',              # ID exactement 11 caractères
            r'youtube\.com/embed/[a-zA-Z0-9_-]{11}',      # ID exactement 11 caractères
            r'youtube\.com/v/[a-zA-Z0-9_-]{11}',         # Ancien format
            r'youtube\.com/attribution_link\?.*v=[a-zA-Z0-9_-]{11}'  # Liens de partage
        ]
        
        for pattern in patterns:
            if re.search(pattern, clean_url):
                return True
        
        # Si l'URL n'est pas reconnue, essayer de la valider directement
        if 'youtube.com' in url or 'youtu.be' in url:
            print(f"⚠️ URL YouTube détectée mais format non reconnu: {url}")
            return True  # Accepter pour permettre le nettoyage
        
        return False
    
    def pack(self, **kwargs):
        """Pack l'interface audio"""
        self.audio_frame.pack(**kwargs)
    
    def hide(self):
        """Cache l'interface audio"""
        self.audio_frame.pack_forget()
    
    def browse_bulk_file(self):
        """Ouvre le dialogue de sélection de fichier .txt"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier .txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
            initialdir=self.download_path
        )
        
        if file_path:
            self.bulk_file_path = file_path
            self.update_file_info(file_path)
    
    def update_file_info(self, file_path):
        """Met à jour l'affichage du fichier sélectionné sans confirmation pop-up"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Formater la taille du fichier
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        # Mettre à jour l'affichage avec confirmation visuelle
        self.file_info_label.configure(
            text=f"✅ Fichier chargé avec succès !\n📄 {filename}\n📊 Taille: {size_str}\n\nCliquez sur 'Traiter le fichier' pour continuer"
        )
        
        # Afficher un message dans la console pour confirmation
        print(f"✅ Fichier chargé: {filename} ({size_str})")
    
    def process_bulk_file(self):
        """Traite le fichier .txt et valide les URLs"""
        if not self.bulk_file_path:
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner un fichier .txt")
            return
        
        try:
            # Lire le fichier
            with open(self.bulk_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Nettoyer et valider les URLs
            valid_urls = []
            invalid_urls = []
            
            for line_num, line in enumerate(lines, 1):
                url = line.strip()
                if url and not url.startswith('#'):  # Ignorer les lignes vides et commentaires
                    # Nettoyer l'URL
                    clean_url = self.clean_youtube_url(url)
                    
                    # Valider l'URL
                    if self.validate_youtube_url(clean_url):
                        valid_urls.append(clean_url)
                    else:
                        invalid_urls.append(f"Ligne {line_num}: {url}")
            
            # Afficher les résultats
            if valid_urls:
                # Confirmation avec nom du fichier
                filename = os.path.basename(self.bulk_file_path)
                result = messagebox.askyesno(
                    "Confirmation",
                    f"Fichier: {filename}\n\n"
                    f"✅ URLs valides: {len(valid_urls)}\n"
                    f"❌ URLs invalides: {len(invalid_urls)}\n\n"
                    f"Voulez-vous ajouter les URLs valides à la file d'attente ?"
                )
                
                if result:
                    self.add_bulk_urls_to_queue(valid_urls)
            else:
                messagebox.showwarning("Aucune URL valide", "Aucune URL YouTube valide trouvée dans le fichier.")
            
            # Afficher les URLs invalides si il y en a
            if invalid_urls:
                self.show_invalid_urls_popup(invalid_urls)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du traitement du fichier:\n{str(e)}")
    
    def add_bulk_urls_to_queue(self, urls):
        """Ajoute les URLs valides à la file d'attente"""
        if not self.app:
            messagebox.showerror("Erreur", "Impossible d'accéder à la file d'attente")
            return
        
        try:
            added_count = 0
            for url in urls:
                # Créer une tâche audio pour chaque URL avec les paramètres bulk
                task = self.app.add_to_queue(
                    url=url,
                    quality=self.bulk_quality_combo.get(),
                    output_format=self.bulk_format_combo.get(),
                    filename="%(title)s",  # Utiliser le nom par défaut, évite les collisions
                    download_path=self.dest_entry.get(),
                    task_type="audio",
                    silent=True  # éviter toutes les pop-ups en mode bulk
                )
                added_count += 1
            
            # Mettre à jour l'interface avec le résultat
            self.file_info_label.configure(
                text=f"✅ {added_count} tâches audio ajoutées à la file d'attente !\n\n"
                f"📋 Les URLs seront traitées une par une.\n"
                f"🔍 Vérifiez l'onglet 'File d\'attente' pour suivre le progrès."
            )
            
            # Indiquer le succès (pas de changement de couleur de bordure car plus de cadre)
            
            # Afficher un message dans la console
            print(f"✅ {added_count} tâches audio ajoutées à la file d'attente")
            
            # Réinitialiser l'interface après un délai
            self.parent.after(3000, self.reset_bulk_interface)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout à la file d'attente:\n{str(e)}")
    
    def show_invalid_urls_popup(self, invalid_urls):
        """Affiche une pop-up avec les URLs invalides"""
        # Créer une fenêtre personnalisée pour afficher les URLs invalides
        popup = ctk.CTkToplevel()
        popup.title("❌ URLs Invalides Détectées")
        popup.geometry("600x400")
        popup.resizable(True, True)
        
        # Titre
        title_label = MacTubeTheme.create_label_section(
            popup,
            "❌ URLs YouTube Invalides"
        )
        title_label.pack(pady=(20, 15), padx=20)
        
        # Zone de texte avec scrollbar
        text_frame = ctk.CTkFrame(popup)
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        text_widget = ctk.CTkTextbox(
            text_frame,
            wrap="word",
            font=ctk.CTkFont(size=12)
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Insérer les URLs invalides
        for invalid_url in invalid_urls:
            text_widget.insert("end", f"{invalid_url}\n")
        
        text_widget.configure(state="disabled")  # Lecture seule
        
        # Bouton de fermeture
        close_button = MacTubeTheme.create_button_primary(
            popup,
            "Fermer",
            command=popup.destroy,
            width=120
        )
        close_button.pack(pady=(0, 20))
        
        # Centrer la fenêtre
        popup.transient(self.parent)
        popup.grab_set()
    
    def reset_bulk_interface(self):
        """Réinitialise l'interface bulk"""
        self.bulk_file_path = None
        self.bulk_urls = []
        self.file_info_label.configure(text="Aucun fichier sélectionné")
        # Réinitialiser les contrôles bulk aux valeurs par défaut
        self.bulk_format_combo.set(".mp3")
        self.bulk_quality_combo.set("192 kbps")
        self.bulk_quality_combo.configure(state="readonly")
    
    # Les méthodes de gestion des événements ne sont plus nécessaires


class MacTubeProgressBar:
    """Barre de progression pour l'extraction audio"""
    
    def __init__(self, parent):
        self.parent = parent
        self.create_progress_bar()
    
    def create_progress_bar(self):
        """Crée la barre de progression"""
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Barre de progression
        self.progress = ctk.CTkProgressBar(
            self.frame,
            height=8,
            corner_radius=4,
            progress_color=MacTubeTheme.get_color('primary'),
            bg_color=MacTubeTheme.get_color('bg_secondary')
        )
        self.progress.pack(fill="x", pady=(0, 10))
        self.progress.set(0)
        
        # Label de statut
        self.status_label = MacTubeTheme.create_label_body(
            self.frame,
            ""
        )
        self.status_label.pack()

    def update_theme(self):
        """Applique les couleurs du thème à la barre de progression"""
        try:
            self.progress.configure(progress_color=MacTubeTheme.get_color('primary'),
                                    bg_color=MacTubeTheme.get_color('bg_secondary'))
            self.status_label.configure(text_color=MacTubeTheme.get_color('text_primary'))
        except Exception:
            pass
    
    def update_progress(self, status, progress):
        """Met à jour la progression"""
        self.status_label.configure(text=status)
        self.progress.set(progress)
    
    def show(self):
        """Affiche la barre de progression"""
        self.frame.pack(fill="x", pady=(10, 0))
    
    def hide(self):
        """Cache la barre de progression"""
        self.frame.pack_forget()
