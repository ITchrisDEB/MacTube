#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Composants UI pour MacTube - YouTube Downloader pour macOS
"""

import customtkinter as ctk
from mactube_theme import MacTubeTheme

class MacTubeNavigation:
    """Barre de navigation style macOS"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_tab = "download"
        self.create_navigation()
    
    def create_navigation(self):
        """Crée la barre de navigation"""
        self.nav_frame = ctk.CTkFrame(
            self.parent,
            fg_color=MacTubeTheme.get_color('bg_header'),
            height=50,
            corner_radius=0
        )
        self.nav_frame.pack(fill="x", side="top")
        
        # Boutons de navigation
        self.download_btn = self.create_nav_button("⬇️ Télécharger", "download", 0)
        self.history_btn = self.create_nav_button("📚 Historique", "history", 1)
        self.queue_btn = self.create_nav_button("📋 File d'attente", "queue", 2)
        self.settings_btn = self.create_nav_button("⚙️ Paramètres", "settings", 3)
        
        # Indicateur de tab actif (corrigé)
        self.active_indicator = ctk.CTkFrame(
            self.nav_frame,
            fg_color=MacTubeTheme.get_color('primary'),
            width=120,
            height=3,
            corner_radius=0
        )
        self.active_indicator.place(x=0, y=47)
    
    def create_nav_button(self, text, tab_name, position):
        """Crée un bouton de navigation"""
        btn = ctk.CTkButton(
            self.nav_frame,
            text=text,
            command=lambda: self.switch_tab(tab_name),
            fg_color="transparent",
            hover_color=MacTubeTheme.get_color('bg_secondary'),
            text_color=MacTubeTheme.get_color('text_primary'),
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120,
            height=40,
            corner_radius=0
        )
        btn.place(x=position * 120, y=5)
        return btn
    
    def switch_tab(self, tab_name):
        """Change de tab"""
        self.current_tab = tab_name
        # Mettre à jour l'indicateur
        position = self.tab_name_to_position(tab_name)
        self.active_indicator.place(x=position * 120, y=47)
        # Émettre un événement pour changer le contenu
        self.parent.event_generate("<<TabChanged>>")
    
    def tab_name_to_position(self, tab_name):
        """Convertit le nom du tab en position"""
        positions = {"download": 0, "history": 1, "queue": 2, "settings": 3}
        return positions.get(tab_name, 0)

class MacTubeCard:
    """Carte style macOS"""
    
    def __init__(self, parent, title, **kwargs):
        self.parent = parent
        self.title = title
        self.create_card(**kwargs)
    
    def create_card(self, **kwargs):
        """Crée la carte"""
        self.frame = MacTubeTheme.create_card_frame(self.parent)
        
        # Titre de la carte
        if self.title:
            self.title_label = MacTubeTheme.create_label_section(
                self.frame,
                self.title
            )
            self.title_label.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Contenu de la carte
        self.content_frame = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def pack(self, **kwargs):
        """Pack la carte"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid la carte"""
        self.frame.grid(**kwargs)

class MacTubeProgressBar:
    """Barre de progression style macOS"""
    
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
        
        # Masquer par défaut
        self.frame.pack_forget()
    
    def update_progress(self, status, progress=None):
        """Met à jour la progression"""
        self.status_label.configure(text=status)
        if progress is not None:
            self.progress.set(progress)
        
        # Afficher la barre
        self.frame.pack(fill="x", pady=(10, 0))
    
    def hide(self):
        """Masque la barre de progression"""
        self.frame.pack_forget()
    
    def pack(self, **kwargs):
        """Pack la barre de progression"""
        self.frame.pack(**kwargs)

class MacTubeThumbnail:
    """Affichage de miniature style macOS"""
    
    def __init__(self, parent):
        self.parent = parent
        self.create_thumbnail()
    
    def create_thumbnail(self):
        """Crée l'affichage de miniature"""
        self.frame = ctk.CTkFrame(
            self.parent,
            width=320,
            height=180,
            corner_radius=8,
            fg_color=MacTubeTheme.get_color('bg_secondary'),
            border_width=1,
            border_color=MacTubeTheme.get_color('text_secondary')
        )
        
        # Label par défaut
        self.thumbnail_label = ctk.CTkLabel(
            self.frame,
            text="🎬\nMiniature",
            font=ctk.CTkFont(size=14),
            text_color=MacTubeTheme.get_color('text_secondary')
        )
        self.thumbnail_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def set_image(self, image):
        """Définit l'image de la miniature"""
        self.thumbnail_label.configure(image=image, text="")
        self.thumbnail_label.image = image  # Garder une référence
    
    def set_error(self, error_text):
        """Affiche un message d'erreur"""
        self.thumbnail_label.configure(
            text=f"❌\n{error_text}",
            image=""
        )
    
    def pack(self, **kwargs):
        """Pack la miniature"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid la miniature"""
        self.frame.grid(**kwargs)
