#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacTube - YouTube Downloader moderne pour macOS
Application native avec détection complète des qualités YouTube
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import re
import time
import threading
import json
import io
import queue
from pathlib import Path
from datetime import datetime

# Imports pour le téléchargement
import yt_dlp
import requests

# Imports personnalisés
from mactube_theme import MacTubeTheme, setup_mactube_theme
from mactube_components import MacTubeNavigation, MacTubeCard, MacTubeProgressBar, MacTubeThumbnail
from mactube_ffmpeg import get_ffmpeg_path

class DownloadTask:
    """Tâche de téléchargement pour la file d'attente"""
    
    def __init__(self, url, quality, output_format, filename, download_path):
        self.url = url
        self.quality = quality
        self.output_format = output_format
        self.filename = filename
        self.download_path = download_path
        self.status = "En attente"
        self.progress = 0
        self.speed = "0 MB/s"
        self.eta = "Calcul..."
        self.created_at = datetime.now()
        self.id = f"task_{int(time.time())}_{id(self)}"
        self.video_title = self._extract_video_title()
    
    def _extract_video_title(self):
        """Extrait le titre de la vidéo depuis l'URL ou le nom de fichier"""
        if self.filename and self.filename != "Nom personnalisé (optionnel)":
            return self.filename
        elif "youtube.com" in self.url or "youtu.be" in self.url:
            # Extraire l'ID de la vidéo pour un titre court
            import re
            video_id_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)', self.url)
            if video_id_match:
                return f"YouTube Video ({video_id_match.group(1)[:8]}...)"
        return "Vidéo inconnue"

class MacTubeApp:
    """Application MacTube - YouTube Downloader pour macOS"""
    
    def __init__(self):
        # Configuration du thème
        setup_mactube_theme()
        
        # Configuration SSL pour macOS
        self.setup_ssl_for_macos()
        
        # Variables d'état
        self.video_info = None
        self.download_path = str(Path.home() / "Downloads")
        self.is_downloading = False
        
        # File d'attente des téléchargements
        self.download_queue = queue.Queue()
        self.download_threads = []
        self.active_tasks = {}  # Stocker {task_id: task} pour les tâches actives
        self.max_concurrent_downloads = 2  # Nombre max de téléchargements simultanés
        self.queue_worker_running = False
        
        # Création de la fenêtre principale
        self.setup_main_window()
        
        # Initialisation de l'historique (avant l'interface)
        self.history = MacTubeHistory()
        
        # Création de l'interface
        self.create_interface()
        
        # Configuration des événements
        self.setup_bindings()
        
        # Démarrer le gestionnaire de file d'attente
        self.start_queue_worker()
        
        print("✅ MacTube - YouTube Downloader initialisé")
    
    def setup_ssl_for_macos(self):
        """Configuration SSL spécifique pour macOS"""
        try:
            import ssl
            import urllib3
            
            # Désactiver les avertissements SSL
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Configuration SSL pour yt-dlp
            ssl._create_default_https_context = ssl._create_unverified_context
            
            print("✅ Configuration SSL appliquée pour macOS")
        except Exception as e:
            print(f"⚠️  Configuration SSL partielle: {e}")
    
    def setup_main_window(self):
        """Configure la fenêtre principale"""
        self.root = ctk.CTk()
        self.root.title("MacTube - YouTube Downloader")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 800)
        
        # Configuration de la fenêtre
        self.root.configure(fg_color=MacTubeTheme.get_color('bg_primary'))
        
        # Icône de l'application (optionnel)
        try:
            icon_path = "mactube.icns"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
    
    def create_interface(self):
        """Crée l'interface principale"""
        # Barre de navigation
        self.navigation = MacTubeNavigation(self.root)
        
        # Contenu principal
        self.main_content = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        self.main_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Créer les différents tabs
        self.create_download_tab()
        self.create_history_tab()
        self.create_queue_tab()
        self.create_settings_tab()
        
        # Afficher le tab de téléchargement par défaut
        self.show_tab("download")
    
    def create_download_tab(self):
        """Crée le tab de téléchargement"""
        self.download_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        
        # Carte d'analyse
        self.analysis_card = MacTubeCard(
            self.download_frame,
            "🔍 Analyse de vidéo YouTube"
        )
        self.analysis_card.pack(fill="x", pady=(0, 20))
        
        # Champ URL
        url_frame = ctk.CTkFrame(self.analysis_card.content_frame, fg_color="transparent")
        url_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(url_frame, "🔗 URL YouTube :").pack(side="left")
        
        self.url_entry = MacTubeTheme.create_entry_modern(
            url_frame,
            "Collez l'URL de la vidéo YouTube ici..."
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        self.analyze_button = MacTubeTheme.create_button_primary(
            url_frame,
            "🔍 Analyser",
            command=self.analyze_video,
            width=100
        )
        self.analyze_button.pack(side="right")
        
        # Zone d'information vidéo
        info_frame = ctk.CTkFrame(self.analysis_card.content_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 15))
        
        # Miniature (à gauche)
        self.thumbnail = MacTubeThumbnail(info_frame)
        self.thumbnail.pack(side="left", padx=(0, 20))
        
        # Informations vidéo (à droite)
        video_info_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        video_info_frame.pack(side="left", fill="both", expand=True)
        
        self.video_title = MacTubeTheme.create_label_title(
            video_info_frame,
            "Titre de la vidéo"
        )
        self.video_title.pack(anchor="w", pady=(0, 10))
        
        self.video_duration = MacTubeTheme.create_label_body(
            video_info_frame,
            "⏱️ Durée: --:--"
        )
        self.video_duration.pack(anchor="w", pady=(0, 5))
        
        self.video_channel = MacTubeTheme.create_label_body(
            video_info_frame,
            "📺 Chaîne: --"
        )
        self.video_channel.pack(anchor="w")
        
        # Carte d'options
        self.options_card = MacTubeCard(
            self.download_frame,
            "⚙️ Options de téléchargement"
        )
        self.options_card.pack(fill="x", pady=(0, 20))
        
        # Qualité vidéo
        quality_frame = ctk.CTkFrame(self.options_card.content_frame, fg_color="transparent")
        quality_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(quality_frame, "🎬 Qualité vidéo :").pack(side="left")
        
        self.quality_combo = ctk.CTkComboBox(
            quality_frame,
            values=["Analyser d'abord une vidéo"],
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=300
        )
        self.quality_combo.pack(side="right")
        
        # Nom du fichier
        filename_frame = ctk.CTkFrame(self.options_card.content_frame, fg_color="transparent")
        filename_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(filename_frame, "📝 Nom du fichier :").pack(side="left")
        
        self.filename_entry = MacTubeTheme.create_entry_modern(
            filename_frame,
            "Nom personnalisé (optionnel)"
        )
        self.filename_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        # Format
        format_frame = ctk.CTkFrame(self.options_card.content_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(format_frame, "📁 Format de sortie :").pack(side="left")
        
        self.format_combo = ctk.CTkComboBox(
            format_frame,
            values=[".mp4", ".mkv", ".avi", ".mov", ".webm"],
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=300
        )
        self.format_combo.set(".mp4")
        self.format_combo.pack(side="right")
        
        # Dossier de destination
        path_frame = ctk.CTkFrame(self.options_card.content_frame, fg_color="transparent")
        path_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(path_frame, "📂 Dossier de destination :").pack(side="left")
        
        self.path_entry = MacTubeTheme.create_entry_modern(
            path_frame,
            self.download_path
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        self.browse_button = MacTubeTheme.create_button_primary(
            path_frame,
            "📁 Choisir...",
            command=self.browse_folder,
            width=100
        )
        self.browse_button.pack(side="right")
        
        # Bouton de téléchargement
        self.download_button = MacTubeTheme.create_button_primary(
            self.download_frame,
            "⬇️ Télécharger",
            command=self.start_download
        )
        self.download_button.pack(pady=20)
        
        # Barre de progression (masquée par défaut)
        self.progress_bar = MacTubeProgressBar(self.download_frame)
        self.progress_bar.pack(fill="x", pady=(0, 20))
        self.progress_bar.hide()  # Masquer par défaut
        
        # Label de statut
        self.status_label = MacTubeTheme.create_label_body(
            self.download_frame,
            "✅ Prêt à analyser une vidéo YouTube"
        )
        self.status_label.pack()
    
    def create_history_tab(self):
        """Crée le tab d'historique"""
        self.history_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        
        # Carte historique
        self.history_card = MacTubeCard(
            self.history_frame,
            "📚 Historique des téléchargements"
        )
        self.history_card.pack(fill="both", expand=True)
        
        # Liste des téléchargements
        self.history_list = ctk.CTkTextbox(
            self.history_card.content_frame,
            height=400,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.history_list.pack(fill="both", expand=True, pady=(0, 15))
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(self.history_card.content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        self.refresh_button = MacTubeTheme.create_button_primary(
            buttons_frame,
            "🔄 Actualiser",
            command=self.refresh_history,
            width=120
        )
        self.refresh_button.pack(side="left", padx=(0, 10))
        
        self.clear_button = MacTubeTheme.create_button_primary(
            buttons_frame,
            "🗑️ Effacer",
            command=self.clear_history,
            width=120
        )
        self.clear_button.pack(side="left")
        
        # Charger l'historique initial
        self.refresh_history()
    
    def create_queue_tab(self):
        """Crée le tab de la file d'attente"""
        self.queue_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        
        # Carte file d'attente
        self.queue_card = MacTubeCard(
            self.queue_frame,
            "📋 File d'attente des téléchargements"
        )
        self.queue_card.pack(fill="both", expand=True)
        
        # Informations de la file
        info_frame = ctk.CTkFrame(self.queue_card.content_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 15))
        
        self.queue_info_label = MacTubeTheme.create_label_body(
            info_frame,
            "📊 Téléchargements en cours: 0 | En attente: 0"
        )
        self.queue_info_label.pack(side="left")
        
        # Liste des tâches
        self.queue_list_frame = ctk.CTkFrame(self.queue_card.content_frame, fg_color="transparent")
        self.queue_list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # En-têtes
        headers_frame = ctk.CTkFrame(self.queue_list_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(0, 10))
        
        MacTubeTheme.create_label_body(headers_frame, "Tâche").pack(side="left", padx=(0, 20))
        MacTubeTheme.create_label_body(headers_frame, "Progression").pack(side="left", padx=(0, 20))
        MacTubeTheme.create_label_body(headers_frame, "Vitesse").pack(side="left", padx=(0, 20))
        MacTubeTheme.create_label_body(headers_frame, "Temps").pack(side="left", padx=(0, 20))
        MacTubeTheme.create_label_body(headers_frame, "Statut").pack(side="left", padx=(0, 20))
        MacTubeTheme.create_label_body(headers_frame, "Actions").pack(side="left")
        
        # Zone de liste (scrollable)
        self.queue_list_container = ctk.CTkScrollableFrame(
            self.queue_list_frame,
            height=300
        )
        self.queue_list_container.pack(fill="both", expand=True)
        
        # Boutons d'action
        buttons_frame = ctk.CTkFrame(self.queue_card.content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        self.refresh_queue_button = MacTubeTheme.create_button_primary(
            buttons_frame,
            "🔄 Actualiser",
            command=self._refresh_queue_list,
            width=120
        )
        self.refresh_queue_button.pack(side="left", padx=(0, 10))
        
        self.pause_queue_button = MacTubeTheme.create_button_secondary(
            buttons_frame,
            "⏸️ Pause",
            command=self.pause_queue,
            width=120
        )
        self.pause_queue_button.pack(side="left", padx=(0, 10))
        
        self.resume_queue_button = MacTubeTheme.create_button_success(
            buttons_frame,
            "▶️ Reprendre",
            command=self.resume_queue,
            width=120
        )
        self.resume_queue_button.pack(side="left")
        
        # Initialiser la liste
        self._refresh_queue_list()
    
    def create_settings_tab(self):
        """Crée le tab des paramètres"""
        self.settings_frame = ctk.CTkFrame(
            self.main_content,
            fg_color="transparent"
        )
        
        # Carte de paramètres
        self.settings_card = MacTubeCard(
            self.settings_frame,
            "⚙️ Paramètres MacTube"
        )
        self.settings_card.pack(fill="both", expand=True)
        
        # Thème
        theme_frame = ctk.CTkFrame(self.settings_card.content_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(theme_frame, "🎨 Thème :").pack(side="left")
        
        self.theme_combo = ctk.CTkComboBox(
            theme_frame,
            values=["Système", "Clair", "Sombre"],
            state="readonly",
            height=35,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            width=200,
            command=self.change_theme
        )
        self.theme_combo.set("Système")
        self.theme_combo.pack(side="right")
        
        # Autres paramètres
        MacTubeTheme.create_label_section(
            self.settings_card.content_frame,
            "🔧 Paramètres avancés"
        ).pack(pady=(20, 10), anchor="w")
        
        # SSL
        self.ssl_checkbox = ctk.CTkCheckBox(
            self.settings_card.content_frame,
            text="Ignorer les erreurs SSL (recommandé pour macOS)",
            font=ctk.CTkFont(size=12)
        )
        self.ssl_checkbox.pack(pady=(0, 10), anchor="w")
        self.ssl_checkbox.select()
        
        # Retry
        self.retry_checkbox = ctk.CTkCheckBox(
            self.settings_card.content_frame,
            text="Retry automatique en cas d'échec",
            font=ctk.CTkFont(size=12)
        )
        self.retry_checkbox.pack(pady=(0, 10), anchor="w")
        self.retry_checkbox.select()
        
        # File d'attente
        MacTubeTheme.create_label_section(
            self.settings_card.content_frame,
            "📋 Gestion de la file d'attente"
        ).pack(pady=(20, 10), anchor="w")
        
        # Nombre max de téléchargements simultanés
        max_downloads_frame = ctk.CTkFrame(self.settings_card.content_frame, fg_color="transparent")
        max_downloads_frame.pack(fill="x", pady=(0, 15))
        
        MacTubeTheme.create_label_body(max_downloads_frame, "🔄 Téléchargements simultanés :").pack(side="left")
        
        self.max_downloads_slider = ctk.CTkSlider(
            max_downloads_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            command=self.update_max_downloads
        )
        self.max_downloads_slider.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.max_downloads_slider.set(self.max_concurrent_downloads)
        
        self.max_downloads_label = MacTubeTheme.create_label_body(
            max_downloads_frame,
            f"{self.max_concurrent_downloads}"
        )
        self.max_downloads_label.pack(side="right")
        
        # Bouton pour vider la file d'attente
        self.clear_queue_button = MacTubeTheme.create_button_secondary(
            self.settings_card.content_frame,
            "🗑️ Vider la file d'attente",
            command=self.clear_download_queue,
            width=200
        )
        self.clear_queue_button.pack(pady=(0, 10), anchor="w")
    
    def update_max_downloads(self, value):
        """Met à jour le nombre max de téléchargements simultanés"""
        self.max_concurrent_downloads = int(value)
        self.max_downloads_label.configure(text=f"{self.max_concurrent_downloads}")
        print(f"✅ Nombre max de téléchargements mis à jour: {self.max_concurrent_downloads}")
    
    def clear_download_queue(self):
        """Vide la file d'attente des téléchargements"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment vider la file d'attente ?"):
            # Vider la file
            while not self.download_queue.empty():
                try:
                    self.download_queue.get_nowait()
                    self.download_queue.task_done()
                except queue.Empty:
                    break
            
            # Arrêter les téléchargements en cours
            for thread in self.download_threads:
                if thread.is_alive():
                    # Note: On ne peut pas forcer l'arrêt d'un thread, mais on peut marquer les tâches
                    pass
            
            self.download_threads = []
            messagebox.showinfo("Succès", "File d'attente vidée avec succès!")
            print("✅ File d'attente vidée")
    
    def show_tab(self, tab_name):
        """Affiche un tab spécifique"""
        # Masquer tous les tabs
        self.download_frame.pack_forget()
        self.history_frame.pack_forget()
        self.queue_frame.pack_forget()
        self.settings_frame.pack_forget()
        
        # Afficher le tab sélectionné
        if tab_name == "download":
            self.download_frame.pack(fill="both", expand=True)
        elif tab_name == "history":
            self.history_frame.pack(fill="both", expand=True)
        elif tab_name == "queue":
            self.queue_frame.pack(fill="both", expand=True)
        elif tab_name == "settings":
            self.settings_frame.pack(fill="both", expand=True)
    
    def setup_bindings(self):
        """Configure les bindings"""
        # Changement de tab
        self.root.bind("<<TabChanged>>", self.on_tab_changed)
        
        # Raccourci Cmd+V pour coller
        self.root.bind('<Command-v>', self.paste_url)
        
        # Entrée pour analyser
        self.url_entry.bind('<Return>', lambda e: self.analyze_video())
        
        # Focus automatique sur le champ URL
        self.url_entry.focus()
    
    def start_queue_worker(self):
        """Démarre le gestionnaire de file d'attente"""
        self.queue_worker_running = True
        threading.Thread(target=self._queue_worker, daemon=True).start()
        print("✅ Gestionnaire de file d'attente démarré")
    
    def _queue_worker(self):
        """Gestionnaire principal de la file d'attente"""
        while self.queue_worker_running:
            try:
                # Attendre une tâche
                task = self.download_queue.get(timeout=1)
                
                # Vérifier le nombre de téléchargements actifs
                active_downloads = len([t for t in self.download_threads if t.is_alive()])
                
                if active_downloads < self.max_concurrent_downloads:
                    print(f"🚀 Lancement du téléchargement: {task.id}")
                    
                    # Stocker la tâche comme active
                    self.active_tasks[task.id] = task
                    
                    # Lancer le téléchargement
                    download_thread = threading.Thread(
                        target=self._download_task_thread, 
                        args=(task,), 
                        daemon=True
                    )
                    download_thread.start()
                    self.download_threads.append(download_thread)
                    
                    # Nettoyer les threads terminés
                    self.download_threads = [t for t in self.download_threads if t.is_alive()]
                    
                    # Marquer la tâche comme traitée seulement après le lancement
                    self.download_queue.task_done()
                else:
                    print(f"⏳ Téléchargement en attente (limite atteinte): {task.id}")
                    # Remettre la tâche en file d'attente
                    self.download_queue.put(task)
                    time.sleep(2)  # Attendre un peu
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Erreur dans le gestionnaire de file d'attente: {e}")
                # En cas d'erreur, marquer la tâche comme traitée pour éviter le blocage
                try:
                    self.download_queue.task_done()
                except:
                    pass
    
    def add_to_queue(self, url, quality, output_format, filename, download_path):
        """Ajoute une tâche à la file d'attente"""
        task = DownloadTask(url, quality, output_format, filename, download_path)
        self.download_queue.put(task)
        
        # Mettre à jour l'interface
        self.root.after(0, self._update_queue_display)
        
        # Programmer des mises à jour régulières de la file d'attente
        self._schedule_queue_updates()
        
        print(f"✅ Tâche ajoutée à la file d'attente: {task.id}")
        return task
    
    def _schedule_queue_updates(self):
        """Programme des mises à jour régulières de la file d'attente"""
        if hasattr(self, 'queue_frame'):
            # Mettre à jour toutes les 2 secondes
            self.root.after(2000, self._refresh_queue_list)
            # Programmer la prochaine mise à jour
            self.root.after(2000, self._schedule_queue_updates)
    
    def _update_queue_display(self):
        """Met à jour l'affichage de la file d'attente"""
        if hasattr(self, 'queue_frame'):
            # Mettre à jour la liste des tâches
            self._refresh_queue_list()
    
    def _download_task_thread(self, task):
        """Thread pour télécharger une tâche de la file d'attente"""
        try:
            print(f"📥 Début du téléchargement: {task.id} - {task.url}")
            task.status = "Téléchargement en cours..."
            self.root.after(0, lambda: self._update_task_status(task))
            
            # Configuration yt-dlp pour cette tâche
            format_selector = self._get_format_selector(task.quality)
            output_template = os.path.join(task.download_path, f"{task.filename}.%(ext)s")
            
            print(f"🔧 Configuration yt-dlp:")
            print(f"   Format: {format_selector}")
            print(f"   Sortie: {output_template}")
            print(f"   Format final: {task.output_format.lstrip('.')}")
            
            # Obtenir le chemin FFmpeg du projet
            ffmpeg_path = get_ffmpeg_path()
            if not ffmpeg_path:
                raise Exception("FFmpeg non trouvé dans le projet")
            
            print(f"🔧 Utilisation de FFmpeg: {ffmpeg_path}")
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': output_template,
                'merge_output_format': task.output_format.lstrip('.'),
                'progress_hooks': [lambda d: self._task_progress_hook(d, task)],
                'verbose': True,  # Plus de debug
                'ffmpeg_location': ffmpeg_path,  # Utiliser FFmpeg du projet
            }
            
            # Lancer le téléchargement
            print(f"🚀 Lancement de yt-dlp...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([task.url])
            
            print(f"📊 Résultat yt-dlp: {result}")
            
            # Marquer comme terminé
            task.status = "Terminé ✅"
            task.progress = 100
            
            # Retirer de la liste des tâches actives
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            
            self.root.after(0, lambda: self._update_task_status(task))
            
            # Ajouter à l'historique
            self.history.add_download(
                task.filename, task.url, task.download_path, 
                task.output_format, task.quality
            )
            
            print(f"✅ Téléchargement terminé avec succès: {task.id}")
            
        except Exception as e:
            print(f"❌ Erreur de téléchargement: {task.id} - {e}")
            import traceback
            traceback.print_exc()
            
            task.status = f"Erreur: {str(e)}"
            self.root.after(0, lambda: self._update_task_status(task))
    
    def _task_progress_hook(self, d, task):
        """Hook de progression pour une tâche"""
        if d['status'] == 'downloading':
            # Mettre à jour la progression
            if 'total_bytes' in d and d['total_bytes']:
                task.progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                task.progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            
            # Mettre à jour la vitesse
            if 'speed' in d and d['speed']:
                task.speed = f"{d['speed'] / (1024*1024):.1f} MB/s"
            
            # Mettre à jour le temps restant
            if 'eta' in d and d['eta']:
                task.eta = f"{d['eta']}s"
            
            # Mettre à jour le statut
            task.status = "Téléchargement en cours..."
            
            # Rafraîchir l'interface en temps réel
            self.root.after(0, self._refresh_queue_list)
    
    def _update_task_status(self, task):
        """Met à jour le statut d'une tâche dans l'interface"""
        if hasattr(self, 'queue_frame'):
            self._refresh_queue_list()
    
    def _get_format_selector(self, quality):
        """Retourne le sélecteur de format yt-dlp pour une qualité donnée"""
        # Logique similaire à celle existante mais adaptée pour yt-dlp
        if 'Ultra HD' in quality or '1620' in quality:
            return "bestvideo[height<=1620]+bestaudio"
        elif 'Full HD' in quality or '1080' in quality:
            return "bestvideo[height<=1080]+bestaudio"
        elif 'HD+' in quality or '810' in quality:
            return "bestvideo[height<=810]+bestaudio"
        elif 'HD' in quality and '540' in quality:
            return "bestvideo[height<=540]+bestaudio"
        elif 'SD' in quality and '360' in quality:
            return "bestvideo[height<=360]+bestaudio"
        elif 'SD' in quality and '270' in quality:
            return "bestvideo[height<=270]+bestaudio"
        else:
            return "bestvideo+bestaudio"
    
    def _refresh_queue_list(self):
        """Met à jour la liste des tâches de la file d'attente"""
        if hasattr(self, 'queue_frame'):
            # Nettoyer la liste existante
            for widget in self.queue_list_container.winfo_children():
                widget.destroy()
            
            # Compter les tâches
            queue_size = self.download_queue.qsize()
            active_downloads = len(self.active_tasks)
            
            # Mettre à jour le label d'information
            self.queue_info_label.configure(
                text=f"📊 Téléchargements en cours: {active_downloads} | En attente: {queue_size}"
            )
            
            # Afficher les tâches actives avec leurs vraies données
            for task_id, task in self.active_tasks.items():
                # Créer une ligne avec les vraies informations de la tâche
                self._create_download_row(
                    title=task.video_title[:50] + "..." if len(task.video_title) > 50 else task.video_title,
                    status=task.status,
                    progress=task.progress,
                    speed=task.speed,
                    eta=task.eta,
                    state="active"
                )
            
            # Afficher les tâches en attente
            if queue_size > 0:
                # Créer une ligne pour chaque tâche en attente
                for i in range(queue_size):
                    self._create_download_row(
                        title=f"Tâche en attente {i+1}",
                        status="En attente",
                        progress=0,
                        speed="0 MB/s",
                        eta="En attente",
                        state="waiting"
                    )
            
            # Si aucune tâche, afficher un message
            if active_downloads == 0 and queue_size == 0:
                empty_label = MacTubeTheme.create_label_body(
                    self.queue_list_container,
                    "📋 Aucune tâche dans la file d'attente"
                )
                empty_label.pack(anchor="center", pady=20)
    
    def _create_download_row(self, title, status, progress, speed, eta, state):
        """Crée une ligne d'affichage pour un téléchargement"""
        row_frame = ctk.CTkFrame(self.queue_list_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        
        # Titre de la tâche
        title_label = MacTubeTheme.create_label_body(row_frame, title)
        title_label.configure(width=200)
        title_label.pack(side="left", padx=(0, 20), anchor="w")
        
        # Barre de progression
        progress_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        progress_frame.configure(width=150)
        progress_frame.pack(side="left", padx=(0, 20))
        
        progress_bar = ctk.CTkProgressBar(progress_frame, width=120, height=12)
        progress_bar.pack()
        progress_bar.set(progress / 100)
        
        # Couleur de la barre selon le statut
        if state == "active":
            progress_bar.configure(progress_color="green")
        elif state == "waiting":
            progress_bar.configure(progress_color="orange")
        else:
            progress_bar.configure(progress_color="blue")
        
        progress_label = MacTubeTheme.create_label_body(progress_frame, f"{progress:.1f}%")
        progress_label.pack()
        
        # Vitesse
        speed_label = MacTubeTheme.create_label_body(row_frame, speed)
        speed_label.configure(width=80)
        speed_label.pack(side="left", padx=(0, 20), anchor="w")
        
        # Temps restant
        eta_label = MacTubeTheme.create_label_body(row_frame, eta)
        eta_label.configure(width=80)
        eta_label.pack(side="left", padx=(0, 20), anchor="w")
        
        # Statut
        status_color = "green" if state == "active" else "orange" if state == "waiting" else "red"
        status_label = MacTubeTheme.create_label_body(row_frame, status)
        status_label.configure(width=100)
        status_label.pack(side="left", padx=(0, 20), anchor="w")
        
        # Actions
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.configure(width=100)
        actions_frame.pack(side="left")
        
        if state == "active":
            pause_btn = MacTubeTheme.create_button_secondary(
                actions_frame, "⏸️", command=lambda: self._pause_download(title), width=30
            )
            pause_btn.pack(side="left", padx=2)
        elif state == "waiting":
            remove_btn = MacTubeTheme.create_button_secondary(
                actions_frame, "❌", command=lambda: self._remove_from_queue(title), width=30
            )
            remove_btn.pack(side="left", padx=2)
    
    def _pause_download(self, title):
        """Met en pause un téléchargement spécifique"""
        messagebox.showinfo("Pause", f"Pause du téléchargement: {title}")
        # TODO: Implémenter la pause individuelle
    
    def _remove_from_queue(self, title):
        """Retire une tâche de la file d'attente"""
        if messagebox.askyesno("Confirmation", f"Retirer {title} de la file d'attente ?"):
            # TODO: Implémenter la suppression individuelle
            messagebox.showinfo("Succès", f"{title} retiré de la file d'attente")
    
    def pause_queue(self):
        """Met en pause la file d'attente"""
        self.queue_worker_running = False
        self.pause_queue_button.configure(state="disabled")
        self.resume_queue_button.configure(state="normal")
        messagebox.showinfo("File d'attente", "File d'attente mise en pause")
        print("⏸️ File d'attente mise en pause")
    
    def resume_queue(self):
        """Reprend la file d'attente"""
        if not self.queue_worker_running:
            self.start_queue_worker()
            self.pause_queue_button.configure(state="normal")
            self.resume_queue_button.configure(state="disabled")
            messagebox.showinfo("File d'attente", "File d'attente reprise")
            print("▶️ File d'attente reprise")
    
    def on_tab_changed(self, event):
        """Appelé lors du changement de tab"""
        current_tab = getattr(self.navigation, 'current_tab', 'download')
        self.show_tab(current_tab)
    
    def paste_url(self, event=None):
        """Colle l'URL depuis le presse-papiers"""
        try:
            clipboard_content = self.root.clipboard_get()
            if "youtube.com" in clipboard_content or "youtu.be" in clipboard_content:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_content)
                self.analyze_video()
        except:
            pass
    
    def validate_youtube_url(self, url):
        """Valide l'URL YouTube"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            if re.search(pattern, url):
                return True
        return False
    
    def analyze_video(self):
        """Analyse la vidéo YouTube"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Erreur", "Veuillez saisir une URL YouTube")
            return
        
        if not self.validate_youtube_url(url):
            messagebox.showerror("Erreur", "URL YouTube invalide")
            return
        
        # Désactiver le bouton pendant l'analyse
        self.analyze_button.configure(state="disabled", text="⏳ Analyse...")
        self.status_label.configure(text="🔍 Analyse de la vidéo en cours...")
        
        # Lancer l'analyse dans un thread
        threading.Thread(target=self._analyze_video_thread, args=(url,), daemon=True).start()
    
    def _analyze_video_thread(self, url):
        """Thread pour l'analyse de la vidéo avec yt-dlp"""
        try:
            # Obtenir le chemin FFmpeg du projet
            ffmpeg_path = get_ffmpeg_path()
            if not ffmpeg_path:
                print("⚠️ FFmpeg non trouvé dans le projet, utilisation du système")
            else:
                print(f"🔧 Utilisation de FFmpeg: {ffmpeg_path}")
            
            # Configuration yt-dlp
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
                thumbnail_url = info.get('thumbnail', '')
                
                # Récupérer les formats disponibles
                formats = info.get('formats', [])
                streams = []
                
                # Traiter chaque format
                for fmt in formats:
                    if fmt.get('vcodec') != 'none' and fmt.get('resolution'):
                        # Format vidéo avec résolution
                        if fmt.get('acodec') != 'none':
                            # Vidéo + audio
                            stream_type = 'video+audio'
                        else:
                            # Vidéo seulement
                            stream_type = 'video_only'
                        
                        streams.append({
                            'format_id': fmt.get('format_id'),
                            'resolution': fmt.get('resolution'),
                            'filesize': fmt.get('filesize'),
                            'type': stream_type,
                            'format_obj': fmt,
                            'ext': fmt.get('ext'),
                            'fps': fmt.get('fps')
                        })
                    elif fmt.get('acodec') != 'none' and not fmt.get('vcodec', 'none') == 'none':
                        # Format audio seulement
                        streams.append({
                            'format_id': fmt.get('format_id'),
                            'resolution': f"Audio {fmt.get('abr', 'N/A')}kbps",
                            'filesize': fmt.get('filesize'),
                            'type': 'audio_only',
                            'format_obj': fmt,
                            'ext': fmt.get('ext'),
                            'abr': fmt.get('abr')
                        })
                
                # Trier les streams par qualité
                def sort_key(stream):
                    if 'Audio' in stream['resolution']:
                        return -1  # Audio en dernier
                    
                    res = stream['resolution']
                    if 'x' in res:  # Format "1920x1080"
                        try:
                            height = int(res.split('x')[1])
                            return height
                        except:
                            return 0
                    return 0
                
                streams.sort(key=sort_key, reverse=True)
                
                # Créer l'objet d'information
                video_info = {
                    'title': title,
                    'duration': duration,
                    'channel': channel,
                    'thumbnail_url': thumbnail_url,
                    'streams': streams,
                    'yt_object': info
                }
                
                # Mettre à jour l'interface
                self.root.after(0, self._update_video_info, video_info)
                
        except Exception as e:
            error_msg = f"Erreur lors de l'analyse : {str(e)}"
            print(error_msg)
            self.root.after(0, self._show_analysis_error, error_msg)
    
    def _update_video_info(self, info):
        """Met à jour l'interface avec les informations de la vidéo"""
        self.video_info = info
        
        # Mettre à jour les informations
        self.video_title.configure(text=info['title'])
        
        # Format de la durée
        if info['duration']:
            minutes = info['duration'] // 60
            seconds = info['duration'] % 60
            duration_str = f"⏱️ Durée: {minutes:02d}:{seconds:02d}"
        else:
            duration_str = "⏱️ Durée: Inconnue"
        self.video_duration.configure(text=duration_str)
        
        self.video_channel.configure(text=f"📺 Chaîne: {info['channel']}")
        
        # Charger la miniature
        self._load_thumbnail(info['thumbnail_url'])
        
        # Mettre à jour les qualités disponibles avec filtre style screenshot
        quality_values = []
        resolutions_found = {}  # Stocker {hauteur: stream} pour garder le meilleur
        
        for stream in info['streams']:
            resolution = stream['resolution']
            
            # Traiter les résolutions vidéo
            if 'x' in resolution:
                try:
                    height = resolution.split('x')[1]
                    # Stocker le stream pour cette hauteur (le premier trouvé est souvent le meilleur)
                    if height not in resolutions_found:
                        resolutions_found[height] = stream
                except:
                    pass  # Ignorer les erreurs de parsing
            elif 'Audio' in resolution and stream['type'] == 'audio_only':
                # Ajouter l'audio directement
                quality_values.append(resolution)
        
        # Convertir toutes les hauteurs trouvées en qualités lisibles
        # Trier par hauteur décroissante pour avoir les meilleures en premier
        sorted_heights = sorted(resolutions_found.keys(), key=lambda x: int(x), reverse=True)
        
        for height in sorted_heights:
            resolution = resolutions_found[height]
            # Créer un nom lisible pour chaque qualité
            if height == '2160':
                display_name = "4K (3840x2160)"
            elif height == '1620':
                display_name = "Ultra HD (3840x1620)"
            elif height == '1440':
                display_name = "1440p QHD (2560x1440)"
            elif height == '1080':
                display_name = "Full HD (1920x1080)"
            elif height == '810':
                display_name = "HD+ (1920x810)"
            elif height == '720':
                display_name = "720p HD (1280x720)"
            elif height == '540':
                display_name = "HD (1280x540)"
            elif height == '480':
                display_name = "480p (854x480)"
            elif height == '360':
                display_name = "360p (640x360)"
            elif height == '270':
                display_name = "270p (640x270)"
            elif height == '240':
                display_name = "240p (426x240)"
            elif height == '180':
                display_name = "180p (426x180)"
            elif height == '144':
                display_name = "144p (256x144)"
            elif height == '128':
                display_name = "128p (256x128)"
            elif height == '90':
                display_name = "90p (213x90)"
            elif height == '45':
                display_name = "45p (106x45)"
            elif height == '27':
                display_name = "27p (48x27)"
            else:
                display_name = f"{height}p ({resolutions_found[height]['resolution']})"
            
            quality_values.append(display_name)
        
        # Trier les qualités (4K en premier, audio à la fin)
        def sort_quality(q):
            if 'Audio' in q:
                return -1  # Audio à la fin
            elif '2160p' in q:
                return 2160
            elif '1440p' in q:
                return 1440
            elif '1080p' in q:
                return 1080
            elif '720p' in q:
                return 720
            elif '480p' in q:
                return 480
            elif '360p' in q:
                return 360
            elif '240p' in q:
                return 240
            elif '144p' in q:
                return 144
            else:
                return 0
        
        quality_values.sort(key=sort_quality, reverse=True)
        
        self.quality_combo.configure(values=quality_values)
        
        # Sélectionner la meilleure qualité par défaut
        if quality_values:
            self.quality_combo.set(quality_values[0])
        
        # Réactiver le bouton
        self.analyze_button.configure(state="normal", text="🔍 Analyser")
        self.status_label.configure(text="✅ Vidéo analysée avec succès - Prêt à télécharger")
        
        # Actualiser l'historique
        self.refresh_history()
    
    def _load_thumbnail(self, url):
        """Charge et affiche la miniature de la vidéo"""
        try:
            # Créer une session requests avec SSL désactivé
            session = requests.Session()
            session.verify = False
            
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                # Charger l'image avec Pillow
                from PIL import Image, ImageTk
                image = Image.open(io.BytesIO(response.content))
                
                # Redimensionner à 320x180 en gardant les proportions
                image.thumbnail((320, 180), Image.Resampling.LANCZOS)
                
                # Convertir pour tkinter
                photo = ImageTk.PhotoImage(image)
                
                # Mettre à jour la miniature
                self.thumbnail.set_image(photo)
                
        except Exception as e:
            error_text = "Erreur de chargement\nde la miniature"
            if "SSL" in str(e) or "certificate" in str(e).lower():
                error_text = "Erreur SSL lors du\nchargement de la miniature"
            self.thumbnail.set_error(error_text)
    
    def _format_size(self, size_bytes):
        """Formate la taille en MB/GB"""
        if not size_bytes:
            return "Inconnue"
        
        mb = size_bytes / (1024 * 1024)
        if mb < 1024:
            return f"{mb:.1f} MB"
        else:
            gb = mb / 1024
            return f"{gb:.1f} GB"
    
    def _show_analysis_error(self, error_msg):
        """Affiche une erreur d'analyse"""
        self.analyze_button.configure(state="normal", text="🔍 Analyser")
        self.status_label.configure(text="❌ Erreur lors de l'analyse")
        messagebox.showerror("Erreur d'analyse", error_msg)
    
    def browse_folder(self):
        """Ouvre le sélecteur de dossier"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            # Limiter l'affichage du chemin
            display_path = folder
            if len(display_path) > 50:
                display_path = "..." + display_path[-47:]
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, display_path)
    
    def start_download(self):
        """Démarre le téléchargement en l'ajoutant à la file d'attente"""
        if not self.video_info:
            messagebox.showerror("Erreur", "Veuillez analyser une vidéo d'abord")
            return
        
        # Récupérer les options
        selected_quality = self.quality_combo.get()
        if not selected_quality or selected_quality == "Analyser d'abord une vidéo":
            messagebox.showerror("Erreur", "Veuillez sélectionner une qualité")
            return
        
        output_format = self.format_combo.get()
        filename = self.filename_entry.get().strip()
        download_path = self.path_entry.get().strip()
        
        if not filename or filename == "Nom personnalisé (optionnel)":
            filename = self.video_info.get('title', 'video')
        
        if not download_path:
            download_path = str(Path.home() / "Downloads")
        
        # Vérifier que le dossier existe
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer le dossier: {e}")
                return
        
        # Ajouter à la file d'attente
        task = self.add_to_queue(
            self.url_entry.get().strip(),
            selected_quality,
            output_format,
            filename,
            download_path
        )
        
        # Mettre à jour l'interface
        self.status_label.configure(text=f"✅ Ajouté à la file d'attente: {task.id}")
        self.download_button.configure(text="⬇️ Ajouter à la file")
        
        # Réinitialiser les champs
        self.url_entry.delete(0, tk.END)
        self.quality_combo.set("Analyser d'abord une vidéo")
        self.filename_entry.delete(0, tk.END)
        
        # Afficher un message de confirmation
        messagebox.showinfo(
            "Tâche ajoutée", 
            f"Téléchargement ajouté à la file d'attente!\n\n"
            f"URL: {self.url_entry.get().strip()}\n"
            f"Qualité: {selected_quality}\n"
            f"Format: {output_format}\n"
            f"Fichier: {filename}\n"
            f"Dossier: {download_path}"
        )
    
    def _download_video_thread(self, stream_info, output_format):
        """Thread pour le téléchargement de la vidéo avec yt-dlp"""
        try:
            # Générer le nom de fichier
            custom_filename = self.filename_entry.get().strip()
            if custom_filename and custom_filename != "Nom personnalisé (optionnel)":
                safe_filename = "".join(c for c in custom_filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_filename}{output_format}"
            else:
                safe_title = "".join(c for c in self.video_info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title}{output_format}"
            
            output_path = os.path.join(self.download_path, filename)
            
            # Configuration yt-dlp pour le téléchargement avec audio
            if stream_info['type'] == 'video_only':
                # Pour vidéo seule, forcer fusion avec meilleur audio
                format_selector = f"{stream_info['format_id']}+bestaudio"
            elif stream_info['type'] == 'video+audio':
                # Pour vidéo+audio intégré
                format_selector = stream_info['format_id']
            else:
                # Pour audio seul
                format_selector = stream_info['format_id']
            
            # Obtenir le chemin FFmpeg du projet
            ffmpeg_path = get_ffmpeg_path()
            if not ffmpeg_path:
                print("⚠️ FFmpeg non trouvé dans le projet, utilisation du système")
            else:
                print(f"🔧 Utilisation de FFmpeg: {ffmpeg_path}")
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'merge_output_format': output_format.replace('.', ''),
            }
            
            # Ajouter FFmpeg du projet si disponible
            if ffmpeg_path:
                ydl_opts['ffmpeg_location'] = ffmpeg_path
            
            # Hook de progression pour yt-dlp
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes']:
                        percent = d['downloaded_bytes'] / d['total_bytes']
                        speed = d.get('speed', 0)
                        speed_str = f"{speed/1024/1024:.1f} MB/s" if speed else "-- MB/s"
                        status = f"Téléchargement... {percent*100:.1f}% - {speed_str}"
                        self.root.after(0, self.progress_bar.update_progress, status, percent)
                elif d['status'] == 'finished':
                    self.root.after(0, self.progress_bar.update_progress, "Finalisation...", 0.9)
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            # Mettre à jour le statut
            self.root.after(0, self.progress_bar.update_progress, "Début du téléchargement...", 0)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url_entry.get().strip()])
            
            # Terminé
            self.root.after(0, self._download_complete, output_path)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Erreur lors du téléchargement : {str(e)}")
    
    def _download_complete(self, output_path):
        """Appelé quand le téléchargement est terminé"""
        self.is_downloading = False
        self.download_button.configure(state="normal", text="⬇️ Télécharger")
        self.progress_bar.hide()
        self.status_label.configure(text="✅ Téléchargement terminé avec succès !")
        
        # Enregistrer dans l'historique
        self.history.add_download(
            title=self.video_info['title'],
            url=self.url_entry.get().strip(),
            path=output_path,
            format=self.format_combo.get(),
            quality=self.quality_combo.get().split(' (')[0]
        )
        
        # Notification
        messagebox.showinfo("Téléchargement terminé", f"Vidéo téléchargée avec succès !\n\nEmplacement: {output_path}")
        
        # Actualiser l'historique
        self.refresh_history()
    
    def _show_error(self, error_msg):
        """Affiche une erreur"""
        self.is_downloading = False
        self.download_button.configure(state="normal", text="⬇️ Télécharger")
        self.progress_bar.hide()
        self.status_label.configure(text="❌ Erreur lors du téléchargement")
        messagebox.showerror("Erreur de téléchargement", error_msg)
    
    def change_theme(self, theme):
        """Change le thème de l'application"""
        print(f"🔄 Changement de thème vers: {theme}")
        
        if theme == "Clair":
            MacTubeTheme.force_light_mode()
        elif theme == "Sombre":
            MacTubeTheme.force_dark_mode()
        else:
            ctk.set_appearance_mode("system")
        
        # Attendre un peu que CustomTkinter applique le thème
        self.root.after(100, self._update_theme_colors)
        
        print(f"✅ Thème changé vers: {theme}")
    
    def _update_theme_colors(self):
        """Met à jour les couleurs de tous les composants selon le thème actuel"""
        try:
            # Forcer la mise à jour du thème CustomTkinter
            current_theme = ctk.get_appearance_mode()
            print(f"🔧 Thème actuel: {current_theme}")
            
            # Mettre à jour la couleur de fond principale
            bg_color = MacTubeTheme.get_color('bg_primary')
            self.root.configure(fg_color=bg_color)
            print(f"🎨 Couleur de fond: {bg_color}")
            
            # Mettre à jour le contenu principal
            if hasattr(self, 'main_content'):
                self.main_content.configure(fg_color=bg_color)
                print("✅ Contenu principal mis à jour")
            
            # Mettre à jour la barre de navigation (IMPORTANT !)
            if hasattr(self, 'navigation'):
                nav_bg = MacTubeTheme.get_color('bg_header')
                # Mettre à jour le frame de navigation
                if hasattr(self.navigation, 'nav_frame'):
                    self.navigation.nav_frame.configure(fg_color=nav_bg)
                    print(f"✅ Frame de navigation mis à jour avec: {nav_bg}")
                
                # Mettre à jour tous les boutons de navigation
                nav_text_color = MacTubeTheme.get_color('text_primary')
                for button in [self.navigation.download_btn, self.navigation.history_btn, 
                             self.navigation.queue_btn, self.navigation.settings_btn]:
                    if button:
                        button.configure(text_color=nav_text_color)
                        print(f"✅ Bouton navigation mis à jour: {button.cget('text')}")
                
                # Mettre à jour l'indicateur actif
                if hasattr(self.navigation, 'active_indicator'):
                    self.navigation.active_indicator.configure(fg_color=MacTubeTheme.get_color('primary'))
                    print("✅ Indicateur actif mis à jour")
            
            # Mettre à jour les cartes avec couleurs forcées
            card_color = MacTubeTheme.get_color('bg_card')
            if hasattr(self, 'video_card'):
                self.video_card.frame.configure(fg_color=card_color)
                # Mettre à jour aussi le titre de la carte
                if hasattr(self.video_card, 'title_label'):
                    self.video_card.title_label.configure(text_color=MacTubeTheme.get_color('text_primary'))
                print("✅ Carte vidéo mise à jour")
            if hasattr(self, 'options_card'):
                self.options_card.frame.configure(fg_color=card_color)
                if hasattr(self.options_card, 'title_label'):
                    self.options_card.title_label.configure(text_color=MacTubeTheme.get_color('text_primary'))
                print("✅ Carte options mise à jour")
            if hasattr(self, 'history_card'):
                self.history_card.frame.configure(fg_color=card_color)
                if hasattr(self.history_card, 'title_label'):
                    self.history_card.title_label.configure(text_color=MacTubeTheme.get_color('text_primary'))
                print("✅ Carte historique mise à jour")
            if hasattr(self, 'queue_card'):
                self.queue_card.frame.configure(fg_color=card_color)
                if hasattr(self.queue_card, 'title_label'):
                    self.queue_card.title_label.configure(text_color=MacTubeTheme.get_color('text_primary'))
                print("✅ Carte file d'attente mise à jour")
            if hasattr(self, 'settings_card'):
                self.settings_card.frame.configure(fg_color=card_color)
                if hasattr(self.settings_card, 'title_label'):
                    self.settings_card.title_label.configure(text_color=MacTubeTheme.get_color('text_primary'))
                print("✅ Carte paramètres mise à jour")
            
            # Mettre à jour les labels avec couleurs forcées
            self._update_label_colors()
            
            # Mettre à jour les entrées avec couleurs forcées
            self._update_entry_colors()
            
            # Mettre à jour les combobox et autres composants
            self._update_combo_colors()
            
            # Mettre à jour les frames et conteneurs
            self._update_frame_colors()
            
            # Forcer la mise à jour de l'interface
            self.root.update_idletasks()
            self.root.update()
            
            print(f"✅ Thème mis à jour: {current_theme}")
            
        except Exception as e:
            print(f"⚠️  Erreur mise à jour thème: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_label_colors(self):
        """Met à jour les couleurs des labels"""
        try:
            # Couleur du texte selon le thème
            text_color = MacTubeTheme.get_color('text_primary')
            print(f"🎨 Mise à jour des labels avec la couleur: {text_color}")
            
            # Labels principaux
            if hasattr(self, 'video_title'):
                self.video_title.configure(text_color=text_color)
                print("✅ Label titre vidéo mis à jour")
            if hasattr(self, 'video_duration'):
                self.video_duration.configure(text_color=text_color)
                print("✅ Label durée vidéo mis à jour")
            if hasattr(self, 'video_channel'):
                self.video_channel.configure(text_color=text_color)
                print("✅ Label chaîne vidéo mis à jour")
            if hasattr(self, 'status_label'):
                self.status_label.configure(text_color=text_color)
                print("✅ Label statut mis à jour")
            
            # Labels des sections
            if hasattr(self, 'queue_info_label'):
                self.queue_info_label.configure(text_color=text_color)
                print("✅ Label info file d'attente mis à jour")
            if hasattr(self, 'max_downloads_label'):
                self.max_downloads_label.configure(text_color=text_color)
                print("✅ Label max téléchargements mis à jour")
            
            # Mettre à jour tous les labels de navigation
            if hasattr(self, 'navigation'):
                for button in [self.navigation.download_btn, self.navigation.history_btn, 
                             self.navigation.queue_btn, self.navigation.settings_btn]:
                    if button:
                        button.configure(text_color=text_color)
                print("✅ Boutons de navigation mis à jour")
            
            # Mettre à jour TOUS les labels créés directement (IMPORTANT !)
            self._update_all_direct_labels(text_color)
                
        except Exception as e:
            print(f"⚠️  Erreur mise à jour labels: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_all_direct_labels(self, text_color):
        """Met à jour tous les labels créés directement avec MacTubeTheme"""
        try:
            print("🔍 Recherche de tous les labels directs...")
            
            # Parcourir tous les widgets de l'interface pour trouver les labels
            def update_widget_colors(widget):
                """Met à jour récursivement tous les widgets"""
                try:
                    # Si c'est un label, mettre à jour sa couleur
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color=text_color)
                        print(f"✅ Label direct mis à jour: {widget.cget('text')[:30]}...")
                    
                    # Récursivement mettre à jour tous les enfants
                    for child in widget.winfo_children():
                        update_widget_colors(child)
                        
                except Exception as e:
                    # Ignorer les erreurs sur les widgets individuels
                    pass
            
            # Commencer par la racine
            update_widget_colors(self.root)
            print("✅ Tous les labels directs mis à jour")
            
        except Exception as e:
            print(f"⚠️  Erreur mise à jour labels directs: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_entry_colors(self):
        """Met à jour les couleurs des champs de saisie"""
        try:
            # Couleurs selon le thème
            bg_color = MacTubeTheme.get_color('bg_secondary')
            border_color = MacTubeTheme.get_color('text_secondary')
            text_color = MacTubeTheme.get_color('text_primary')
            
            print(f"🎨 Mise à jour des entrées - Fond: {bg_color}, Bordure: {border_color}, Texte: {text_color}")
            
            # Champs de saisie
            if hasattr(self, 'url_entry'):
                self.url_entry.configure(
                    fg_color=bg_color,
                    border_color=border_color,
                    text_color=text_color
                )
                print("✅ Champ URL mis à jour")
            if hasattr(self, 'filename_entry'):
                self.filename_entry.configure(
                    fg_color=bg_color,
                    border_color=border_color,
                    text_color=text_color
                )
                print("✅ Champ nom de fichier mis à jour")
            if hasattr(self, 'path_entry'):
                self.path_entry.configure(
                    fg_color=bg_color,
                    border_color=border_color,
                    text_color=text_color
                )
                print("✅ Champ chemin mis à jour")
            
            # Mettre à jour aussi les placeholders si possible
            self._update_placeholder_colors()
                
        except Exception as e:
            print(f"⚠️  Erreur mise à jour entrées: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_placeholder_colors(self):
        """Met à jour les couleurs des placeholders"""
        try:
            # Couleur du placeholder selon le thème
            placeholder_color = MacTubeTheme.get_color('text_secondary')
            print(f"🎨 Mise à jour des placeholders avec: {placeholder_color}")
            
            # Mettre à jour les placeholders des champs
            if hasattr(self, 'url_entry'):
                # Reconfigurer le champ avec le nouveau placeholder
                current_placeholder = self.url_entry.cget('placeholder_text')
                self.url_entry.configure(placeholder_text_color=placeholder_color)
                print("✅ Placeholder URL mis à jour")
                
            if hasattr(self, 'filename_entry'):
                current_placeholder = self.filename_entry.cget('placeholder_text')
                self.filename_entry.configure(placeholder_text_color=placeholder_color)
                print("✅ Placeholder nom de fichier mis à jour")
                
        except Exception as e:
            print(f"⚠️  Erreur mise à jour placeholders: {e}")
    
    def _update_combo_colors(self):
        """Met à jour les couleurs des combobox"""
        try:
            if hasattr(self, 'quality_combo'):
                self.quality_combo.configure(fg_color=MacTubeTheme.get_color('bg_secondary'))
                self.quality_combo.configure(border_color=MacTubeTheme.get_color('text_secondary'))
                self.quality_combo.configure(text_color=MacTubeTheme.get_color('text_primary'))
            if hasattr(self, 'format_combo'):
                self.format_combo.configure(fg_color=MacTubeTheme.get_color('bg_secondary'))
                self.format_combo.configure(border_color=MacTubeTheme.get_color('text_secondary'))
                self.format_combo.configure(text_color=MacTubeTheme.get_color('text_primary'))
            if hasattr(self, 'theme_combo'):
                self.theme_combo.configure(fg_color=MacTubeTheme.get_color('bg_secondary'))
                self.theme_combo.configure(border_color=MacTubeTheme.get_color('text_secondary'))
                self.theme_combo.configure(text_color=MacTubeTheme.get_color('text_primary'))
        except Exception as e:
            print(f"⚠️  Erreur mise à jour combobox: {e}")
    
    def _update_frame_colors(self):
        """Met à jour les couleurs des frames et conteneurs"""
        try:
            if hasattr(self, 'download_frame'):
                self.download_frame.configure(fg_color=MacTubeTheme.get_color('bg_card'))
            if hasattr(self, 'analysis_card'):
                self.analysis_card.frame.configure(fg_color=MacTubeTheme.get_color('bg_card'))
            if hasattr(self, 'options_card'):
                self.options_card.frame.configure(fg_color=MacTubeTheme.get_color('bg_card'))
            if hasattr(self, 'history_frame'):
                self.history_frame.configure(fg_color=MacTubeTheme.get_color('bg_card'))
            if hasattr(self, 'queue_frame'):
                self.queue_frame.configure(fg_color=MacTubeTheme.get_color('bg_card'))
            if hasattr(self, 'settings_frame'):
                self.settings_frame.configure(fg_color=MacTubeTheme.get_color('bg_card'))
        except Exception as e:
            print(f"⚠️  Erreur mise à jour frames: {e}")
    
    def refresh_history(self):
        """Actualise l'historique"""
        downloads = self.history.get_downloads()
        
        self.history_list.delete("1.0", tk.END)
        
        if not downloads:
            self.history_list.insert("1.0", "Aucun téléchargement dans l'historique.")
        else:
            for i, download in enumerate(downloads[-20:], 1):  # 20 derniers
                date_str = download['date']
                entry = f"{i}. {download['title']}\n"
                entry += f"   📅 {date_str} | 🎬 {download['quality']} | 📁 {download['format']}\n"
                entry += f"   📂 {download['path']}\n\n"
                self.history_list.insert(tk.END, entry)
    
    def clear_history(self):
        """Efface l'historique"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment effacer l'historique ?"):
            self.history.clear()
            self.refresh_history()
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

class MacTubeHistory:
    """Gestionnaire d'historique pour MacTube"""
    
    def __init__(self):
        self.history_file = Path.home() / ".mactube_history.json"
        self.downloads = self.load_history()
    
    def load_history(self):
        """Charge l'historique depuis le fichier"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def save_history(self):
        """Sauvegarde l'historique"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.downloads, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur de sauvegarde: {e}")
    
    def add_download(self, title, url, path, format, quality):
        """Ajoute un téléchargement à l'historique"""
        download = {
            'title': title,
            'url': url,
            'path': path,
            'format': format,
            'quality': quality,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.downloads.append(download)
        self.save_history()
    
    def get_downloads(self):
        """Récupère tous les téléchargements"""
        return self.downloads
    
    def clear(self):
        """Efface l'historique"""
        self.downloads = []
        self.save_history()

def main():
    """Fonction principale"""
    try:
        print("🚀 Lancement de MacTube - YouTube Downloader...")
        app = MacTubeApp()
        app.run()
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("✅ MacTube fermé normalement")
        print("👋 Au revoir !")

if __name__ == "__main__":
    main()
