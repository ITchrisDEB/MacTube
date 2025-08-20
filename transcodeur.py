#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacTube Transcodeur - Module de conversion audio/vidéo
Gère la conversion cross-platform avec FFmpeg
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import subprocess
from pathlib import Path
import sys

# Imports personnalisés
from mactube_theme import MacTubeTheme
from mactube_ffmpeg import get_ffmpeg_path

class MacTubeTranscoder:
    """Interface de transcodeur pour MacTube"""
    
    def __init__(self, parent, app=None):
        self.parent = parent
        self.app = app
        self.is_transcoding = False
        self.download_path = str(Path.home() / "Downloads")
        
        # Récupérer le chemin FFmpeg
        self.ffmpeg_path = get_ffmpeg_path()
        if not self.ffmpeg_path:
            raise Exception("FFmpeg non trouvé dans le projet")
        
        # Formats cross-platform supportés (lecture + écriture)
        self.supported_video_formats = {
            "mp4": "MP4 (H.264)",
            "mkv": "MKV (Matroska)",
            "avi": "AVI (Audio Video Interleaved)",
            "webm": "WebM (VP8/VP9)"
        }
        
        # Formats audio (réutilisés de mactube_audio.py)
        self.audio_formats = [".mp3", ".aac", ".flac", ".wav", ".m4a", ".ogg"]
        self.audio_qualities = ["128 kbps", "192 kbps", "256 kbps", "320 kbps", "Qualité maximale"]
        
        self.create_transcoder_interface()
        
        # Appliquer le thème
        try:
            self.update_theme()
        except Exception:
            pass
    
    def create_transcoder_interface(self):
        """Crée l'interface du transcodeur"""
        # Frame principal
        self.transcoder_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Carte unique (comme dans mactube_audio.py)
        self.transcoder_card = MacTubeTheme.create_card_frame(self.transcoder_frame)
        self.transcoder_card.pack(fill="x", pady=(0, 20))
        
        # Créer un frame scrollable pour le contenu
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.transcoder_card,
            fg_color="transparent",
            width=800,  # Largeur fixe pour éviter les problèmes de redimensionnement
            height=600   # Hauteur fixe pour activer la scrollbar
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(20, 20))
        
        # Contenu principal (maintenant dans le frame scrollable)
        self.content_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        # Section 1: Conversion Vidéo
        self.create_video_conversion_section()
        
        # Séparateur 1
        separator1_frame = ctk.CTkFrame(self.content_frame, fg_color=MacTubeTheme.get_color('border'), height=1)
        separator1_frame.pack(fill="x", pady=(20, 15))
        
        # Section 2: Extraction Audio depuis Vidéo
        self.create_video_to_audio_section()
        
        # Séparateur 2
        separator2_frame = ctk.CTkFrame(self.content_frame, fg_color=MacTubeTheme.get_color('border'), height=1)
        separator2_frame.pack(fill="x", pady=(20, 15))
        
        # Section 3: Conversion Audio
        self.create_audio_conversion_section()
        
        # Appliquer le thème initial
        self.update_theme()
    
    def create_video_conversion_section(self):
        """Section 1: Conversion Vidéo"""
        # Titre de la section
        section_title = MacTubeTheme.create_label_section(
            self.content_frame,
            "🎬 Conversion Vidéo"
        )
        section_title.pack(pady=(0, 8), anchor="w")
        
        # Frame de contenu pour cette section
        video_section_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        video_section_frame.pack(fill="x", pady=(0, 8))
        
        # Sélection du fichier
        file_frame = ctk.CTkFrame(video_section_frame, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(file_frame, "Fichier vidéo :").pack(side="left")
        
        self.video_file_path = tk.StringVar()
        self.video_file_label = ctk.CTkEntry(
            file_frame,
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary'),
            state="normal"
        )
        self.video_file_label.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.video_file_label.insert(0, "Aucun fichier sélectionné")
        self.video_file_label.configure(state="readonly")
        
        self.select_video_button = MacTubeTheme.create_button_primary(
            file_frame,
            "Sélectionner",
            command=self.select_video_file,
            width=120
        )
        self.select_video_button.pack(side="right")
        
        # Format de sortie
        format_frame = ctk.CTkFrame(video_section_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(format_frame, "Format de sortie :").pack(side="left")
        
        self.video_output_format = ctk.CTkComboBox(
            format_frame,
            values=[f".{ext}" for ext in self.supported_video_formats.keys()],
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary')
        )
        self.video_output_format.pack(side="right")
        self.video_output_format.set(".mp4")
        
        # Dossier de destination
        dest_frame = ctk.CTkFrame(video_section_frame, fg_color="transparent")
        dest_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(dest_frame, "Dossier de destination :").pack(side="left")
        
        self.video_dest_path = tk.StringVar()
        self.video_dest_entry = ctk.CTkEntry(
            dest_frame,
            textvariable=self.video_dest_path,
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary'),
            placeholder_text="Choisir le dossier de destination..."
        )
        self.video_dest_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.video_dest_path.set(self.download_path)  # Pré-remplir avec le chemin par défaut
        
        self.video_dest_button = MacTubeTheme.create_button_primary(
            dest_frame,
            "Choisir...",
            command=self.choose_video_destination,
            width=100
        )
        self.video_dest_button.pack(side="right")
        
        # Bouton de conversion
        self.convert_video_button = MacTubeTheme.create_button_primary(
            video_section_frame,
            "🔄 Convertir Vidéo",
            command=self.convert_video,
            width=200
        )
        self.convert_video_button.pack(pady=(5, 0))
    
    def create_video_to_audio_section(self):
        """Section 2: Extraction Audio depuis Vidéo"""
        # Titre de la section
        section_title = MacTubeTheme.create_label_section(
            self.content_frame,
            "🎵 Extraction Audio depuis Vidéo"
        )
        section_title.pack(pady=(0, 10), anchor="w")
        
        # Frame de contenu pour cette section
        audio_section_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        audio_section_frame.pack(fill="x", pady=(0, 8))
        
        # Sélection du fichier vidéo
        file_frame = ctk.CTkFrame(audio_section_frame, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(file_frame, "Fichier vidéo :").pack(side="left")
        
        self.audio_video_file_path = tk.StringVar()
        self.audio_video_file_label = ctk.CTkEntry(
            file_frame,
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary'),
            state="normal"
        )
        self.audio_video_file_label.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.audio_video_file_label.insert(0, "Aucun fichier sélectionné")
        self.audio_video_file_label.configure(state="readonly")
        
        self.select_audio_video_button = MacTubeTheme.create_button_primary(
            file_frame,
            "Sélectionner",
            command=self.select_audio_video_file,
            width=120
        )
        self.select_audio_video_button.pack(side="right")
        
        # Format audio
        format_frame = ctk.CTkFrame(audio_section_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(format_frame, "Format audio :").pack(side="left")
        
        self.audio_output_format = ctk.CTkComboBox(
            format_frame,
            values=self.audio_formats,
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary'),
            command=self.on_audio_format_change
        )
        self.audio_output_format.pack(side="right")
        self.audio_output_format.set(".mp3")
        
        # Qualité audio
        quality_frame = ctk.CTkFrame(audio_section_frame, fg_color="transparent")
        quality_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(quality_frame, "Qualité audio :").pack(side="left")
        
        self.audio_quality = ctk.CTkComboBox(
            quality_frame,
            values=self.audio_qualities,
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary')
        )
        self.audio_quality.pack(side="right")
        self.audio_quality.set("192 kbps")
        
        # Dossier de destination
        dest_frame = ctk.CTkFrame(audio_section_frame, fg_color="transparent")
        dest_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(dest_frame, "Dossier de destination :").pack(side="left")
        
        self.audio_dest_path = tk.StringVar()
        self.audio_dest_entry = ctk.CTkEntry(
            dest_frame,
            textvariable=self.audio_dest_path,
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary'),
            placeholder_text="Choisir le dossier de destination..."
        )
        self.audio_dest_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.audio_dest_path.set(self.download_path)  # Pré-remplir avec le chemin par défaut
        
        self.audio_dest_button = MacTubeTheme.create_button_primary(
            dest_frame,
            "Choisir...",
            command=self.choose_audio_destination,
            width=100
        )
        self.audio_dest_button.pack(side="right")
        
        # Bouton d'extraction
        self.extract_audio_button = MacTubeTheme.create_button_primary(
            audio_section_frame,
            "🎵 Extraire Audio",
            command=self.extract_audio_from_video,
            width=200
        )
        self.extract_audio_button.pack(pady=(5, 0))
    
    def create_audio_conversion_section(self):
        """Section 3: Conversion Audio"""
        # Titre de la section
        section_title = MacTubeTheme.create_label_section(
            self.content_frame,
            "🎵 Conversion Audio"
        )
        section_title.pack(pady=(0, 10), anchor="w")
        
        # Frame de contenu pour cette section
        audio_conv_section_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        audio_conv_section_frame.pack(fill="x", pady=(0, 8))
        
        # Sélection du fichier audio
        file_frame = ctk.CTkFrame(audio_conv_section_frame, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(file_frame, "Fichier audio :").pack(side="left")
        
        self.audio_input_file_path = tk.StringVar()
        self.audio_input_file_label = ctk.CTkEntry(
            file_frame,
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary'),
            state="normal"
        )
        self.audio_input_file_label.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.audio_input_file_label.insert(0, "Aucun fichier sélectionné")
        self.audio_input_file_label.configure(state="readonly")
        
        self.select_audio_input_button = MacTubeTheme.create_button_primary(
            file_frame,
            "Sélectionner",
            command=self.select_audio_input_file,
            width=120
        )
        self.select_audio_input_button.pack(side="right")
        
        # Format de sortie
        format_frame = ctk.CTkFrame(audio_conv_section_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(format_frame, "Format de sortie :").pack(side="left")
        
        self.audio_output_format_conv = ctk.CTkComboBox(
            format_frame,
            values=self.audio_formats,
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary'),
            command=self.on_audio_conv_format_change
        )
        self.audio_output_format_conv.pack(side="right")
        self.audio_output_format_conv.set(".mp3")
        
        # Qualité audio
        quality_frame = ctk.CTkFrame(audio_conv_section_frame, fg_color="transparent")
        quality_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(quality_frame, "Qualité audio :").pack(side="left")
        
        self.audio_quality_conv = ctk.CTkComboBox(
            quality_frame,
            values=self.audio_qualities,
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary')
        )
        self.audio_quality_conv.pack(side="right")
        self.audio_quality_conv.set("192 kbps")
        
        # Dossier de destination
        dest_frame = ctk.CTkFrame(audio_conv_section_frame, fg_color="transparent")
        dest_frame.pack(fill="x", pady=(0, 8))
        
        MacTubeTheme.create_label_body(dest_frame, "Dossier de destination :").pack(side="left")
        
        self.audio_conv_dest_path = tk.StringVar()
        self.audio_conv_dest_entry = ctk.CTkEntry(
            dest_frame,
            textvariable=self.audio_conv_dest_path,
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary'),
            placeholder_text="Choisir le dossier de destination..."
        )
        self.audio_conv_dest_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.audio_conv_dest_path.set(self.download_path)  # Pré-remplir avec le chemin par défaut
        
        self.audio_conv_dest_button = MacTubeTheme.create_button_primary(
            dest_frame,
            "Choisir...",
            command=self.choose_audio_conv_destination,
            width=100
        )
        self.audio_conv_dest_button.pack(side="right")
        
        # Bouton de conversion
        self.convert_audio_button = MacTubeTheme.create_button_primary(
            audio_conv_section_frame,
            "🔄 Convertir Audio",
            command=self.convert_audio,
            width=200
        )
        self.convert_audio_button.pack(pady=(5, 0))
    
    def execute_transcode_task(self, task):
        """Exécute une tâche de transcodage avec suivi de progression"""
        try:
            print(f"🔄 Exécution de la tâche: {task.task_type}")
            
            # Traiter selon le type de tâche
            if task.task_type == "video_conversion":
                self._execute_video_conversion_with_progress(task)
            elif task.task_type == "audio_extraction":
                self._execute_audio_extraction_with_progress(task)
            elif task.task_type == "audio_conversion":
                self._execute_audio_conversion_with_progress(task)
            else:
                raise Exception(f"Type de tâche inconnu: {task.task_type}")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution: {e}")
            raise e
    
    def select_video_file(self):
        """Sélectionne un fichier vidéo pour la conversion"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier vidéo",
            filetypes=[
                ("Vidéos", "*.mp4 *.avi *.mkv *.mov *.webm *.flv *.m4v *.3gp"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if file_path:
            self.video_file_path.set(file_path)
            filename = os.path.basename(file_path)
            self.video_file_label.configure(state="normal")
            self.video_file_label.delete(0, tk.END)
            self.video_file_label.insert(0, f"📁 {filename}")
            self.video_file_label.configure(state="readonly")
            
            # Détecter le format d'entrée et ajuster les formats de sortie
            self.update_video_output_formats(file_path)
    
    def select_audio_video_file(self):
        """Sélectionne un fichier vidéo pour l'extraction audio"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier vidéo",
            filetypes=[
                ("Vidéos", "*.mp4 *.avi *.mkv *.mov *.webm *.flv *.m4v *.3gp"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if file_path:
            self.audio_video_file_path.set(file_path)
            filename = os.path.basename(file_path)
            self.audio_video_file_label.configure(state="normal")
            self.audio_video_file_label.delete(0, tk.END)
            self.audio_video_file_label.insert(0, f"📁 {filename}")
            self.audio_video_file_label.configure(state="readonly")
    
    def select_audio_input_file(self):
        """Sélectionne un fichier audio pour la conversion"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier audio",
            filetypes=[
                ("Audios", "*.mp3 *.aac *.flac *.wav *.m4a *.ogg"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if file_path:
            self.audio_input_file_path.set(file_path)
            filename = os.path.basename(file_path)
            self.audio_input_file_label.configure(state="normal")
            self.audio_input_file_label.delete(0, tk.END)
            self.audio_input_file_label.insert(0, f"📁 {filename}")
            self.audio_input_file_label.configure(state="readonly")
    
    def choose_video_destination(self):
        """Ouvre le dialogue de sélection de dossier pour la conversion vidéo"""
        folder = filedialog.askdirectory(title="Choisir le dossier de destination pour la vidéo")
        if folder:
            self.video_dest_path.set(folder)
    
    def choose_audio_destination(self):
        """Ouvre le dialogue de sélection de dossier pour l'extraction audio"""
        folder = filedialog.askdirectory(title="Choisir le dossier de destination pour l'audio")
        if folder:
            self.audio_dest_path.set(folder)
    
    def choose_audio_conv_destination(self):
        """Ouvre le dialogue de sélection de dossier pour la conversion audio"""
        folder = filedialog.askdirectory(title="Choisir le dossier de destination pour la conversion audio")
        if folder:
            self.audio_conv_dest_path.set(folder)
    
    def update_video_output_formats(self, input_path):
        """Met à jour les formats de sortie disponibles en excluant le format d'entrée"""
        try:
            # Détecter l'extension du fichier d'entrée
            input_ext = Path(input_path).suffix.lower()
            
            # Créer la liste des formats disponibles (exclure le format d'entrée)
            available_formats = []
            format_descriptions = []
            
            for ext, desc in self.supported_video_formats.items():
                if ext != input_ext.lstrip('.'):
                    available_formats.append(f".{ext}")
                    format_descriptions.append(desc)
            
            # Mettre à jour la combobox des formats de sortie
            if available_formats:
                self.video_output_format.configure(values=available_formats)
                
                # Sélectionner le premier format disponible
                if available_formats[0] != self.video_output_format.get():
                    self.video_output_format.set(available_formats[0])
                
                # Mise à jour silencieuse des formats (sans pop-up)
                input_format = input_ext.lstrip('.') if input_ext else "inconnu"
                print(f"🔍 Format détecté : {input_format.upper()} → Formats disponibles : {', '.join(available_formats).upper()}")
            else:
                messagebox.showwarning(
                    "Format non supporté",
                    f"Le format {input_ext} n'est pas supporté pour la conversion."
                )
                
        except Exception as e:
            print(f"⚠️  Erreur lors de la détection du format: {e}")
    
    def convert_video(self):
        """Convertit une vidéo vers un autre format"""
        if not self.video_file_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier vidéo")
            return
        
        input_path = self.video_file_path.get()
        output_format = self.video_output_format.get()
        dest_path = self.video_dest_path.get() or self.download_path
        
        # Vérifier que le format de sortie est différent du format d'entrée
        input_ext = Path(input_path).suffix.lower().lstrip('.')
        output_ext = output_format.lstrip('.')  # Enlever le point du format de sortie
        if input_ext == output_ext:
            messagebox.showerror(
                "Erreur de format", 
                f"Impossible de convertir un fichier {input_ext.upper()} vers {output_ext.upper()}.\n\n"
                f"Veuillez sélectionner un format de sortie différent du format d'entrée."
            )
            return
        
        # Générer le nom de fichier de sortie (éviter les conflits de nom)
        input_name = Path(input_path).stem
        output_ext = output_format.lstrip('.')  # Enlever le point du format de sortie
        output_path = os.path.join(dest_path, f"{input_name}_converted.{output_ext}")
        
        # Ajouter à la file d'attente au lieu d'exécuter directement
        if self.app and hasattr(self.app, 'add_transcode_to_queue'):
            self.app.add_transcode_to_queue(
                input_path=input_path,
                output_format=output_format,
                quality="N/A",  # Pas de qualité pour la conversion vidéo
                output_path=output_path,
                task_type="video_conversion",
                download_path=dest_path
            )
        else:
            messagebox.showerror("Erreur", "Impossible d'accéder à la file d'attente")
    
    def extract_audio_from_video(self):
        """Extrait l'audio d'une vidéo"""
        if not self.audio_video_file_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier vidéo")
            return
        
        input_path = self.audio_video_file_path.get()
        output_format = self.audio_output_format.get()
        quality = self.audio_quality.get()
        dest_path = self.audio_dest_path.get() or self.download_path
        
        # Générer le nom de fichier de sortie (éviter les conflits de nom)
        input_name = Path(input_path).stem
        output_path = os.path.join(dest_path, f"{input_name}_audio{output_format}")
        
        # Ajouter à la file d'attente au lieu d'exécuter directement
        if self.app and hasattr(self.app, 'add_transcode_to_queue'):
            self.app.add_transcode_to_queue(
                input_path=input_path,
                output_format=output_format,
                quality=quality,
                output_path=output_path,
                task_type="audio_extraction",
                download_path=dest_path
            )
        else:
            messagebox.showerror("Erreur", "Impossible d'accéder à la file d'attente")
    
    def convert_audio(self):
        """Convertit un fichier audio vers un autre format"""
        if not self.audio_input_file_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier audio")
            return
        
        input_path = self.audio_input_file_path.get()
        output_format = self.audio_output_format_conv.get()
        quality = self.audio_quality_conv.get()
        dest_path = self.audio_conv_dest_path.get() or self.download_path
        
        # Générer le nom de fichier de sortie (éviter les conflits de nom)
        input_name = Path(input_path).stem
        output_path = os.path.join(dest_path, f"{input_name}_converted{output_format}")
        
        # Ajouter à la file d'attente au lieu d'exécuter directement
        if self.app and hasattr(self.app, 'add_transcode_to_queue'):
            self.app.add_transcode_to_queue(
                input_path=input_path,
                output_format=output_format,
                quality=quality,
                output_path=output_path,
                task_type="audio_conversion",
                download_path=dest_path
            )
        else:
            messagebox.showerror("Erreur", "Impossible d'accéder à la file d'attente")
    
    def _convert_video_thread(self, input_path, output_path, output_format):
        """Thread de conversion vidéo"""
        try:
            self.is_transcoding = True
            self.convert_video_button.configure(state="disabled", text="🔄 Conversion...")
            
            # Commande FFmpeg pour la conversion vidéo
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c:v', 'libx264',  # Codec H.264 cross-platform
                '-c:a', 'aac',      # Codec audio AAC
                '-y',               # Écraser le fichier existant
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"Vidéo convertie avec succès !\n{output_path}")
            else:
                messagebox.showerror("Erreur", f"Erreur lors de la conversion :\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la conversion : {str(e)}")
        finally:
            self.is_transcoding = False
            self.convert_video_button.configure(state="normal", text="🔄 Convertir Vidéo")
    
    def _execute_video_conversion_with_progress(self, task):
        """Exécute la conversion vidéo avec suivi de progression"""
        import subprocess
        import re
        
        # Obtenir la durée totale de la vidéo d'abord
        probe_cmd = [
            self.ffmpeg_path,
            '-i', task.input_path,
            '-f', 'null', '-'
        ]
        
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        total_duration = self._parse_duration_from_ffmpeg(probe_result.stderr)
        
        # Commande FFmpeg pour la conversion
        cmd = [
            self.ffmpeg_path,
            '-i', task.input_path,
            '-c:v', 'libx264',  # Codec H.264 cross-platform
            '-c:a', 'aac',      # Codec audio AAC
            '-y',               # Écraser le fichier existant
            task.output_path
        ]
        
        # Lancer FFmpeg avec suivi de progression
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
        
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self._parse_ffmpeg_progress(output, task, total_duration)
        
        return_code = process.poll()
        if return_code != 0:
            _, stderr = process.communicate()
            raise Exception(f"FFmpeg error: {stderr}")
    
    def _parse_duration_from_ffmpeg(self, ffmpeg_output):
        """Parse la durée totale depuis la sortie FFmpeg"""
        import re
        # Chercher la ligne "Duration: HH:MM:SS.ss"
        duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', ffmpeg_output)
        if duration_match:
            hours, minutes, seconds, centiseconds = map(int, duration_match.groups())
            total_seconds = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
            return total_seconds
        return None
    
    def _parse_ffmpeg_progress(self, output_line, task, total_duration):
        """Parse la progression depuis une ligne de sortie FFmpeg"""
        import re
        # Chercher la ligne avec "time=HH:MM:SS.ss"
        time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})', output_line)
        if time_match and total_duration:
            hours, minutes, seconds, centiseconds = map(int, time_match.groups())
            current_time = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
            
            # Calculer la progression en pourcentage
            progress = min((current_time / total_duration) * 100, 100)
            task.progress = progress
            
            # Extraire la vitesse si disponible
            speed_match = re.search(r'speed=\s*([0-9.]+)x', output_line)
            if speed_match:
                speed = float(speed_match.group(1))
                task.speed = f"{speed:.1f}x"
            
            # Calculer l'ETA approximative
            if progress > 0 and speed_match:
                remaining_time = (total_duration - current_time) / speed
                task.eta = f"{remaining_time:.0f}s"
            
            print(f"Progression: {progress:.1f}%, Vitesse: {task.speed}, ETA: {task.eta}")
    
    def _extract_audio_thread(self, input_path, output_path, output_format, quality):
        """Thread d'extraction audio depuis vidéo"""
        try:
            self.is_transcoding = True
            self.extract_audio_button.configure(state="disabled", text="🎵 Extraction...")
            
            # Déterminer le codec selon le format
            codec_map = {
                '.mp3': 'libmp3lame',
                '.aac': 'aac',
                '.flac': 'flac',
                '.wav': 'pcm_s16le',
                '.m4a': 'aac',
                '.ogg': 'libvorbis'
            }
            
            codec = codec_map.get(output_format, 'libmp3lame')
            
            # Commande FFmpeg pour l'extraction audio
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-vn',              # Pas de vidéo
                '-c:a', codec,
                '-y',               # Écraser le fichier existant
                output_path
            ]
            
            # Ajouter la qualité pour MP3
            if output_format == '.mp3' and codec == 'libmp3lame':
                cmd.extend(['-b:a', f'{quality}k'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"Audio extrait avec succès !\n{output_path}")
            else:
                messagebox.showerror("Erreur", f"Erreur lors de l'extraction :\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'extraction : {str(e)}")
        finally:
            self.is_transcoding = False
            self.extract_audio_button.configure(state="normal", text="🎵 Extraire Audio")
    
    def _execute_audio_extraction_with_progress(self, task):
        """Exécute l'extraction audio avec suivi de progression"""
        import subprocess
        
        # Déterminer le codec selon le format
        codec_map = {
            '.mp3': 'libmp3lame',
            '.aac': 'aac',
            '.flac': 'flac',
            '.wav': 'pcm_s16le',
            '.m4a': 'aac',
            '.ogg': 'libvorbis'
        }
        
        output_ext = Path(task.output_path).suffix.lower()
        codec = codec_map.get(output_ext, 'aac')
        
        # Obtenir la durée totale de la vidéo d'abord
        probe_cmd = [
            self.ffmpeg_path,
            '-i', task.input_path,
            '-f', 'null', '-'
        ]
        
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        total_duration = self._parse_duration_from_ffmpeg(probe_result.stderr)
        
        cmd = [
            self.ffmpeg_path,
            '-i', task.input_path,
            '-vn',  # Pas de vidéo
            '-c:a', codec,
            '-y',
            task.output_path
        ]
        
        # Lancer FFmpeg avec suivi de progression
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
        
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self._parse_ffmpeg_progress(output, task, total_duration)
        
        return_code = process.poll()
        if return_code != 0:
            _, stderr = process.communicate()
            raise Exception(f"FFmpeg error: {stderr}")
    
    def _convert_audio_thread(self, input_path, output_path, output_format, quality):
        """Thread de conversion audio"""
        try:
            self.is_transcoding = True
            self.convert_audio_button.configure(state="disabled", text="🔄 Conversion...")
            
            # Déterminer le codec selon le format
            codec_map = {
                '.mp3': 'libmp3lame',
                '.aac': 'aac',
                '.flac': 'flac',
                '.wav': 'pcm_s16le',
                '.m4a': 'aac',
                '.ogg': 'libvorbis'
            }
            
            codec = codec_map.get(output_format, 'libmp3lame')
            
            # Commande FFmpeg pour la conversion audio
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c:a', codec,
                '-y',               # Écraser le fichier existant
                output_path
            ]
            
            # Ajouter la qualité pour MP3
            if output_format == '.mp3' and codec == 'libmp3lame':
                cmd.extend(['-b:a', f'{quality}k'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                messagebox.showinfo("Succès", f"Audio converti avec succès !\n{output_path}")
            else:
                messagebox.showerror("Erreur", f"Erreur lors de la conversion :\n{result.stderr}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la conversion : {str(e)}")
        finally:
            self.is_transcoding = False
            self.convert_audio_button.configure(state="normal", text="🔄 Convertir Audio")
    
    def _execute_audio_conversion_with_progress(self, task):
        """Exécute la conversion audio avec suivi de progression"""
        import subprocess
        
        # Déterminer le codec selon le format
        codec_map = {
            '.mp3': 'libmp3lame',
            '.aac': 'aac',
            '.flac': 'flac',
            '.wav': 'pcm_s16le',
            '.m4a': 'aac',
            '.ogg': 'libvorbis'
        }
        
        output_ext = Path(task.output_path).suffix.lower()
        codec = codec_map.get(output_ext, 'aac')
        
        # Obtenir la durée totale du fichier audio d'abord
        probe_cmd = [
            self.ffmpeg_path,
            '-i', task.input_path,
            '-f', 'null', '-'
        ]
        
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        total_duration = self._parse_duration_from_ffmpeg(probe_result.stderr)
        
        cmd = [
            self.ffmpeg_path,
            '-i', task.input_path,
            '-c:a', codec,
            '-y',
            task.output_path
        ]
        
        # Lancer FFmpeg avec suivi de progression
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
        
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self._parse_ffmpeg_progress(output, task, total_duration)
        
        return_code = process.poll()
        if return_code != 0:
            _, stderr = process.communicate()
            raise Exception(f"FFmpeg error: {stderr}")
    
    def on_audio_format_change(self, value):
        """Gère le changement de format audio pour l'extraction depuis vidéo"""
        if value in [".flac", ".wav", ".m4a"]:
            # Formats lossless - griser la qualité et mettre "Qualité maximale"
            self.audio_quality.configure(state="disabled")
            self.audio_quality.set("Qualité maximale")
        else:
            # Formats avec compression - activer la qualité
            self.audio_quality.configure(state="readonly")
            if self.audio_quality.get() == "Qualité maximale":
                self.audio_quality.set("192 kbps")
    
    def on_audio_conv_format_change(self, value):
        """Gère le changement de format audio pour la conversion audio"""
        if value in [".flac", ".wav", ".m4a"]:
            # Formats lossless - griser la qualité et mettre "Qualité maximale"
            self.audio_quality_conv.configure(state="disabled")
            self.audio_quality_conv.set("Qualité maximale")
        else:
            # Formats avec compression - activer la qualité
            self.audio_quality_conv.configure(state="readonly")
            if self.audio_quality_conv.get() == "Qualité maximale":
                self.audio_quality_conv.set("192 kbps")

    def update_theme(self):
        """Met à jour le thème des composants du transcodeur"""
        try:
            # Couleurs de base (comme dans mactube_audio.py)
            bg_primary = MacTubeTheme.get_color('bg_primary')
            bg_secondary = MacTubeTheme.get_color('bg_secondary') 
            bg_card = MacTubeTheme.get_color('bg_card')
            text_primary = MacTubeTheme.get_color('text_primary')
            text_secondary = MacTubeTheme.get_color('text_secondary')
            
            # Fond principal de l'onglet
            if hasattr(self, 'transcoder_frame'):
                self.transcoder_frame.configure(fg_color=bg_primary)
            
            # Carte principale unique
            if hasattr(self, 'transcoder_card'):
                self.transcoder_card.configure(fg_color=bg_card, border_color=text_secondary)
            
            # Frame scrollable
            if hasattr(self, 'scrollable_frame'):
                self.scrollable_frame.configure(fg_color=bg_card)
            
            # Configurer les couleurs des combobox
            for combo in [getattr(self, 'video_output_format', None), 
                         getattr(self, 'audio_output_format', None),
                         getattr(self, 'audio_quality', None),
                         getattr(self, 'audio_output_format_conv', None),
                         getattr(self, 'audio_quality_conv', None)]:
                if combo is not None:
                    try:
                        combo.configure(fg_color=bg_secondary, border_color=text_secondary, text_color=text_primary)
                    except Exception:
                        pass
            
            # Configurer les couleurs des champs de destination
            for entry in [getattr(self, 'video_dest_entry', None),
                         getattr(self, 'audio_dest_entry', None),
                         getattr(self, 'audio_conv_dest_entry', None)]:
                if entry is not None:
                    try:
                        entry.configure(fg_color=bg_secondary, border_color=text_secondary, text_color=text_primary)
                        entry.configure(placeholder_text_color=text_secondary)
                    except Exception:
                        pass
            
            # Configurer les couleurs des boutons
            for button in [getattr(self, 'select_video_button', None),
                          getattr(self, 'select_audio_video_button', None),
                          getattr(self, 'select_audio_input_button', None),
                          getattr(self, 'convert_video_button', None),
                          getattr(self, 'extract_audio_button', None),
                          getattr(self, 'convert_audio_button', None),
                          getattr(self, 'video_dest_button', None),
                          getattr(self, 'audio_dest_button', None),
                          getattr(self, 'audio_conv_dest_button', None)]:
                if button is not None:
                    try:
                        button.configure(text_color=MacTubeTheme.get_color('text_light'))
                    except Exception:
                        pass
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la mise à jour du thème: {e}")
    
    def pack(self, **kwargs):
        """Pack le frame principal"""
        self.transcoder_frame.pack(**kwargs)
    
    def hide(self):
        """Masque le frame principal"""
        self.transcoder_frame.pack_forget()
