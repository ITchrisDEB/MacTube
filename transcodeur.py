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
        self.audio_qualities = ["128", "192", "256", "320"]
        
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
        
        # Titre principal
        title_label = MacTubeTheme.create_label_section(
            self.transcoder_frame,
            "🔄 Transcodeur Audio/Video"
        )
        title_label.pack(pady=(20, 30), padx=20, anchor="w")
        
        # Section 1: Conversion Vidéo
        self.create_video_conversion_section()
        
        # Section 2: Extraction Audio depuis Vidéo
        self.create_video_to_audio_section()
        
        # Section 3: Conversion Audio
        self.create_audio_conversion_section()
        
        # Appliquer le thème initial
        self.update_theme()
    
    def create_video_conversion_section(self):
        """Section 1: Conversion Vidéo"""
        # Carte de conversion vidéo
        video_card = MacTubeTheme.create_card_frame(self.transcoder_frame)
        video_card.pack(fill="x", pady=(0, 20), padx=20)
        
        # Titre de la section
        MacTubeTheme.create_label_section(
            video_card,
            "🎬 Conversion Vidéo"
        ).pack(pady=(20, 15), padx=20, anchor="w")
        
        # Contenu
        content_frame = ctk.CTkFrame(video_card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sélection du fichier
        file_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(file_frame, "Fichier vidéo :").pack(side="left")
        
        self.video_file_path = tk.StringVar()
        self.video_file_label = MacTubeTheme.create_label_body(
            file_frame,
            "Aucun fichier sélectionné"
        )
        self.video_file_label.pack(side="left", padx=(10, 10))
        
        self.select_video_button = MacTubeTheme.create_button_primary(
            file_frame,
            "Sélectionner",
            command=self.select_video_file,
            width=120
        )
        self.select_video_button.pack(side="right")
        
        # Format de sortie
        format_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(format_frame, "Format de sortie :").pack(side="left")
        
        self.video_output_format = ctk.CTkComboBox(
            format_frame,
            values=list(self.supported_video_formats.keys()),
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150
        )
        self.video_output_format.pack(side="right")
        self.video_output_format.set("mp4")
        
        # Bouton de conversion
        self.convert_video_button = MacTubeTheme.create_button_primary(
            content_frame,
            "🔄 Convertir Vidéo",
            command=self.convert_video,
            width=200
        )
        self.convert_video_button.pack(pady=(10, 0))
    
    def create_video_to_audio_section(self):
        """Section 2: Extraction Audio depuis Vidéo"""
        # Carte d'extraction audio
        audio_card = MacTubeTheme.create_card_frame(self.transcoder_frame)
        audio_card.pack(fill="x", pady=(0, 20), padx=20)
        
        # Titre de la section
        MacTubeTheme.create_label_section(
            audio_card,
            "🎵 Extraction Audio depuis Vidéo"
        ).pack(pady=(20, 15), padx=20, anchor="w")
        
        # Contenu
        content_frame = ctk.CTkFrame(audio_card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sélection du fichier vidéo
        file_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(file_frame, "Fichier vidéo :").pack(side="left")
        
        self.audio_video_file_path = tk.StringVar()
        self.audio_video_file_label = MacTubeTheme.create_label_body(
            file_frame,
            "Aucun fichier sélectionné"
        )
        self.audio_video_file_label.pack(side="left", padx=(10, 10))
        
        self.select_audio_video_button = MacTubeTheme.create_button_primary(
            file_frame,
            "Sélectionner",
            command=self.select_audio_video_file,
            width=120
        )
        self.select_audio_video_button.pack(side="right")
        
        # Format audio
        format_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(format_frame, "Format audio :").pack(side="left")
        
        self.audio_output_format = ctk.CTkComboBox(
            format_frame,
            values=self.audio_formats,
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150
        )
        self.audio_output_format.pack(side="right")
        self.audio_output_format.set(".mp3")
        
        # Qualité audio
        quality_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        quality_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(quality_frame, "Qualité audio :").pack(side="left")
        
        self.audio_quality = ctk.CTkComboBox(
            quality_frame,
            values=self.audio_qualities,
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150
        )
        self.audio_quality.pack(side="right")
        self.audio_quality.set("192")
        
        # Bouton d'extraction
        self.extract_audio_button = MacTubeTheme.create_button_primary(
            content_frame,
            "🎵 Extraire Audio",
            command=self.extract_audio_from_video,
            width=200
        )
        self.extract_audio_button.pack(pady=(10, 0))
    
    def create_audio_conversion_section(self):
        """Section 3: Conversion Audio"""
        # Carte de conversion audio
        audio_conv_card = MacTubeTheme.create_card_frame(self.transcoder_frame)
        audio_conv_card.pack(fill="x", pady=(0, 20), padx=20)
        
        # Titre de la section
        MacTubeTheme.create_label_section(
            audio_conv_card,
            "🎵 Conversion Audio"
        ).pack(pady=(20, 15), padx=20, anchor="w")
        
        # Contenu
        content_frame = ctk.CTkFrame(audio_conv_card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sélection du fichier audio
        file_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(file_frame, "Fichier audio :").pack(side="left")
        
        self.audio_input_file_path = tk.StringVar()
        self.audio_input_file_label = MacTubeTheme.create_label_body(
            file_frame,
            "Aucun fichier sélectionné"
        )
        self.audio_input_file_label.pack(side="left", padx=(10, 10))
        
        self.select_audio_input_button = MacTubeTheme.create_button_primary(
            file_frame,
            "Sélectionner",
            command=self.select_audio_input_file,
            width=120
        )
        self.select_audio_input_button.pack(side="right")
        
        # Format de sortie
        format_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(format_frame, "Format de sortie :").pack(side="left")
        
        self.audio_output_format_conv = ctk.CTkComboBox(
            format_frame,
            values=self.audio_formats,
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150
        )
        self.audio_output_format_conv.pack(side="right")
        self.audio_output_format_conv.set(".mp3")
        
        # Qualité audio
        quality_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        quality_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(quality_frame, "Qualité audio :").pack(side="left")
        
        self.audio_quality_conv = ctk.CTkComboBox(
            quality_frame,
            values=self.audio_qualities,
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=150
        )
        self.audio_quality_conv.pack(side="right")
        self.audio_quality_conv.set("192")
        
        # Bouton de conversion
        self.convert_audio_button = MacTubeTheme.create_button_primary(
            content_frame,
            "🔄 Convertir Audio",
            command=self.convert_audio,
            width=200
        )
        self.convert_audio_button.pack(pady=(10, 0))
    
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
            self.video_file_label.configure(text=f"📁 {filename}")
    
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
            self.audio_video_file_label.configure(text=f"📁 {filename}")
    
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
            self.audio_input_file_label.configure(text=f"📁 {filename}")
    
    def convert_video(self):
        """Convertit une vidéo vers un autre format"""
        if not self.video_file_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier vidéo")
            return
        
        input_path = self.video_file_path.get()
        output_format = self.video_output_format.get()
        
        # Générer le nom de fichier de sortie
        input_name = Path(input_path).stem
        output_path = os.path.join(self.download_path, f"{input_name}.{output_format}")
        
        # Lancer la conversion en thread
        threading.Thread(target=self._convert_video_thread, 
                       args=(input_path, output_path, output_format), 
                       daemon=True).start()
    
    def extract_audio_from_video(self):
        """Extrait l'audio d'une vidéo"""
        if not self.audio_video_file_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier vidéo")
            return
        
        input_path = self.audio_video_file_path.get()
        output_format = self.audio_output_format.get()
        quality = self.audio_quality.get()
        
        # Générer le nom de fichier de sortie
        input_name = Path(input_path).stem
        output_path = os.path.join(self.download_path, f"{input_name}{output_format}")
        
        # Lancer l'extraction en thread
        threading.Thread(target=self._extract_audio_thread, 
                       args=(input_path, output_path, output_format, quality), 
                       daemon=True).start()
    
    def convert_audio(self):
        """Convertit un fichier audio vers un autre format"""
        if not self.audio_input_file_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier audio")
            return
        
        input_path = self.audio_input_file_path.get()
        output_format = self.audio_output_format_conv.get()
        quality = self.audio_quality_conv.get()
        
        # Générer le nom de fichier de sortie
        input_name = Path(input_path).stem
        output_path = os.path.join(self.download_path, f"{input_name}{output_format}")
        
        # Lancer la conversion en thread
        threading.Thread(target=self._convert_audio_thread, 
                       args=(input_path, output_path, output_format, quality), 
                       daemon=True).start()
    
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
    
    def update_theme(self):
        """Met à jour le thème"""
        try:
            # Récupérer le thème actuel depuis l'app principale
            if self.app and hasattr(self.app, 'current_theme'):
                current_theme = self.app.current_theme
            else:
                # Fallback : détecter le thème système
                current_theme = "Dark" if ctk.get_appearance_mode() == "Dark" else "Light"
            
            # Appliquer le thème aux composants
            if current_theme == "Dark":
                # Thème sombre
                self.transcoder_frame.configure(fg_color="transparent")
                
                # Mettre à jour les cartes si elles existent
                for widget in self.transcoder_frame.winfo_children():
                    if hasattr(widget, 'configure'):
                        try:
                            widget.configure(fg_color="transparent")
                        except:
                            pass
                        
                        # Mettre à jour les sous-composants
                        for child in widget.winfo_children():
                            if hasattr(child, 'configure'):
                                try:
                                    if isinstance(child, ctk.CTkFrame):
                                        child.configure(fg_color="transparent")
                                except:
                                    pass
            else:
                # Thème clair
                self.transcoder_frame.configure(fg_color="transparent")
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la mise à jour du thème: {e}")
    
    def pack(self, **kwargs):
        """Pack le frame principal"""
        self.transcoder_frame.pack(**kwargs)
    
    def hide(self):
        """Masque le frame principal"""
        self.transcoder_frame.pack_forget()
