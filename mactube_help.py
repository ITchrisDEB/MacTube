#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacTube Help - Système d'aide intégré pour MacTube
Interface d'aide moderne avec navigation et recherche
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import webbrowser
from pathlib import Path
import re

# Imports personnalisés
from mactube_theme import MacTubeTheme

class MacTubeHelp:
    """Système d'aide intégré pour MacTube"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.current_section = "accueil"
        self.search_results = []
        
        # Informations de l'application
        self.app_name = "MacTube"
        self.app_version = "v1.2.5"
        self.app_description = "YouTube Downloader moderne pour macOS"
        
        # Créer la fenêtre d'aide
        self.create_help_window()
        
    def create_help_window(self):
        """Crée la fenêtre principale d'aide"""
        self.help_window = ctk.CTkToplevel()
        self.help_window.title(f"Aide {self.app_name} {self.app_version}")
        # Élargir de 2% : 1000 * 1.02 = 1020, 700 * 1.02 = 714
        self.help_window.geometry("1020x714")
        self.help_window.resizable(True, True)
        self.help_window.minsize(816, 612)
        
        # Configuration de la fenêtre
        self.help_window.configure(fg_color=MacTubeTheme.get_color('bg_primary'))
        
        # Icône de l'application
        try:
            icon_path = "mactube.icns"
            if os.path.exists(icon_path):
                self.help_window.iconbitmap(icon_path)
        except:
            pass
        
        # Créer l'interface
        self.create_help_interface()
        
        # Centrer la fenêtre
        self.center_window()
        
    def create_help_interface(self):
        """Crée l'interface d'aide"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.help_window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # En-tête avec titre et version
        self.create_header(main_frame)
        
        # Barre de recherche
        self.create_search_bar(main_frame)
        
        # Contenu principal avec navigation
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Navigation à gauche
        self.create_navigation(content_frame)
        
        # Contenu à droite
        self.create_content_area(content_frame)
        
    def create_header(self, parent):
        """Crée l'en-tête avec titre et version"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Titre principal
        title_label = MacTubeTheme.create_label_title(
            header_frame,
            f"{self.app_name} - {self.app_version}"
        )
        title_label.pack(side="left")
        
        # Description
        desc_label = MacTubeTheme.create_label_body(
            header_frame,
            self.app_description
        )
        desc_label.pack(side="left", padx=(20, 0))
        
        # Bouton fermer à droite (bleu comme dans l'app principale)
        close_button = MacTubeTheme.create_button_primary(
            header_frame,
            "✕ Fermer",
            command=self.help_window.destroy,
            width=100
        )
        close_button.pack(side="right")
        
    def create_search_bar(self, parent):
        """Crée la barre de recherche"""
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 20))
        
        # Label recherche
        MacTubeTheme.create_label_body(search_frame, "🔍 Rechercher dans l'aide :").pack(side="left")
        
        # Champ de recherche
        self.search_entry = MacTubeTheme.create_entry_modern(
            search_frame,
            "Tapez votre recherche ici..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # Bouton recherche
        search_button = MacTubeTheme.create_button_primary(
            search_frame,
            "Rechercher",
            command=self.perform_search,
            width=100
        )
        search_button.pack(side="right")
        
    def create_navigation(self, parent):
        """Crée la navigation à gauche"""
        nav_frame = ctk.CTkFrame(parent, fg_color=MacTubeTheme.get_color('bg_secondary'))
        nav_frame.pack(side="left", fill="y", padx=(0, 20))
        
        # Titre navigation
        nav_title = MacTubeTheme.create_label_section(nav_frame, "Navigation")
        nav_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Boutons de navigation avec icônes
        nav_items = [
            ("🏠 Accueil", "accueil"),
            ("⬇️ Télécharger Vidéo", "telechargement"),
            ("🎵 Extraction Audio", "audio"),
            ("🔄 Transcodeur", "transcodeur"),
            ("📋 File d'attente", "file_attente"),
            ("📚 Historique", "historique"),
            ("⚙️ Paramètres", "parametres"),
            ("❓ FAQ", "faq"),
            ("🌐 Support", "support")
        ]
        
        for label, section in nav_items:
            # Créer un bouton avec icône bleue
            btn = self.create_blue_icon_button(
                nav_frame,
                label,
                lambda s=section: self.show_section(s),
                width=204  # Élargir de 2% : 200 * 1.02 = 204
            )
            btn.pack(pady=2, padx=20, fill="x")
            
    def create_content_area(self, parent):
        """Crée la zone de contenu à droite"""
        self.content_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color=MacTubeTheme.get_color('bg_secondary'),
            width=612  # Élargir de 2% : 600 * 1.02 = 612
        )
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Afficher la section d'accueil par défaut
        self.show_section("accueil")
        
    def show_section(self, section_name):
        """Affiche une section spécifique"""
        self.current_section = section_name
        
        # Vider le contenu
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Afficher la section appropriée
        if section_name == "accueil":
            self.show_accueil_section()
        elif section_name == "telechargement":
            self.show_telechargement_section()
        elif section_name == "audio":
            self.show_audio_section()
        elif section_name == "transcodeur":
            self.show_transcodeur_section()
        elif section_name == "file_attente":
            self.show_file_attente_section()
        elif section_name == "historique":
            self.show_historique_section()
        elif section_name == "parametres":
            self.show_parametres_section()
        
        elif section_name == "faq":
            self.show_faq_section()
        elif section_name == "support":
            self.show_support_section()
            
    def show_accueil_section(self):
        """Section d'accueil"""
        # Titre
        title = MacTubeTheme.create_label_title(self.content_frame, f"Bienvenue dans {self.app_name}")
        title.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Description
        desc = ctk.CTkLabel(
            self.content_frame,
            text=f"{self.app_name} est une application native macOS moderne et élégante\npour télécharger des vidéos YouTube en haute qualité.",
            font=ctk.CTkFont(size=12),
            text_color=MacTubeTheme.get_color('text_primary'),
            anchor="w",
            justify="left"
        )
        desc.pack(pady=(0, 20), padx=20, anchor="w")
        
        # Capture d'écran principale
        if os.path.exists("screenshots/MacTube.png"):
            try:
                # Créer un label avec l'image (simulation)
                screenshot_label = MacTubeTheme.create_label_body(
                    self.content_frame,
                    "🖼️ Interface principale de MacTube"
                )
                screenshot_label.pack(pady=(0, 10), padx=20, anchor="w")
                
                # Note sur la capture
                note = MacTubeTheme.create_label_small(
                    self.content_frame,
                    "📸 Capture d'écran de l'interface principale (MacTube.png)"
                )
                note.pack(pady=(0, 20), padx=20, anchor="w")
            except:
                pass
        
        # Fonctionnalités principales
        features_title = MacTubeTheme.create_label_section(self.content_frame, "✨ Fonctionnalités principales")
        features_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        features = [
            "🎬 Téléchargement vidéo HD jusqu'à 4K",
            "🎵 Extraction audio avec formats multiples",
            "🔄 Conversion et transcodage avancé",
            "📋 File d'attente intelligente",
            "📚 Historique persistant",
            "🎨 Interface moderne et intuitive"
        ]
        
        for feature in features:
            feature_label = MacTubeTheme.create_label_body(self.content_frame, feature)
            feature_label.pack(pady=2, padx=20, anchor="w")
            
    def show_telechargement_section(self):
        """Section téléchargement"""
        title = MacTubeTheme.create_label_title(self.content_frame, "⬇️ Télécharger Vidéo")
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Description
        desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Le module de téléchargement vous permet de télécharger des vidéos YouTube\navec différentes qualités et formats."
        )
        desc.pack(pady=(0, 20), padx=20, anchor="w")
        
        # Étapes
        steps_title = MacTubeTheme.create_label_section(self.content_frame, "📋 Étapes de téléchargement")
        steps_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        steps = [
            "1. Collez l'URL YouTube dans le champ URL",
            "2. Cliquez sur '🔍 Analyser' pour récupérer les informations",
            "3. La miniature et les infos de la vidéo s'affichent automatiquement",
            "4. Choisissez la qualité vidéo souhaitée (détectée automatiquement)",
            "5. Optionnel : Personnalisez le nom du fichier",
            "6. Cliquez sur '⬇️ Télécharger' pour lancer le téléchargement"
        ]
        
        for step in steps:
            step_label = MacTubeTheme.create_label_body(self.content_frame, step)
            step_label.pack(pady=2, padx=20, anchor="w")
            
        # Fonctionnalités
        features_title = MacTubeTheme.create_label_section(self.content_frame, "✨ Fonctionnalités")
        features_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        features = [
            "• Détection automatique des qualités disponibles",
            "• Affichage de la miniature YouTube",
            "• Informations détaillées (titre, durée, chaîne)",
            "• Nom de fichier personnalisable",
            "• Intégration avec la file d'attente"
        ]
        
        for feature in features:
            feature_label = MacTubeTheme.create_label_body(self.content_frame, feature)
            feature_label.pack(pady=2, padx=20, anchor="w")
            
    def show_audio_section(self):
        """Section extraction audio"""
        title = MacTubeTheme.create_label_title(self.content_frame, "🎵 Extraction Audio")
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Description
        desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Extrayez l'audio de vos vidéos YouTube préférées dans différents formats\net qualités. Fonctionne par copier-coller d'URL comme le téléchargement vidéo."
        )
        desc.pack(pady=(0, 20), padx=20, anchor="w")
        
        # Étapes
        steps_title = MacTubeTheme.create_label_section(self.content_frame, "📋 Étapes d'extraction")
        steps_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        steps = [
            "1. Collez l'URL YouTube dans le champ URL",
            "2. Cliquez sur 'Analyser' pour récupérer les informations",
            "3. Choisissez le format audio souhaité (MP3, M4A, AAC, etc.)",
            "4. Sélectionnez la qualité audio (128, 192, 256, 320 kbps)",
            "5. Optionnel : Personnalisez le nom du fichier",
            "6. Cliquez sur 'Extraire Audio' pour lancer l'extraction"
        ]
        
        for step in steps:
            step_label = MacTubeTheme.create_label_body(self.content_frame, step)
            step_label.pack(pady=2, padx=20, anchor="w")
        
        # Capture d'écran audio
        if os.path.exists("screenshots/MacTube2.png"):
            try:
                screenshot_label = MacTubeTheme.create_label_body(
                    self.content_frame,
                    "🖼️ Interface d'extraction audio"
                )
                screenshot_label.pack(pady=(0, 10), padx=20, anchor="w")
                
                note = MacTubeTheme.create_label_small(
                    self.content_frame,
                    "📸 Capture d'écran du module audio (MacTube2.png)"
                )
                note.pack(pady=(0, 20), padx=20, anchor="w")
            except:
                pass
        
        # Formats supportés
        formats_title = MacTubeTheme.create_label_section(self.content_frame, "🎼 Formats audio supportés")
        formats_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        formats = [
            "• MP3 - Compatible universel, compression efficace",
            "• M4A - Format Apple, haute qualité",
            "• AAC - Codec avancé, excellente qualité",
            "• FLAC - Sans perte, qualité maximale",
            "• WAV - Format non compressé, qualité CD",
            "• OGG - Format libre, bonne compression"
        ]
        
        for format_info in formats:
            format_label = MacTubeTheme.create_label_body(self.content_frame, format_info)
            format_label.pack(pady=2, padx=20, anchor="w")
            
        # Qualités audio
        quality_title = MacTubeTheme.create_label_section(self.content_frame, "🎚️ Qualités audio disponibles")
        quality_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        qualities = [
            "• 128 kbps - Qualité standard, taille réduite",
            "• 192 kbps - Qualité bonne, équilibre taille/qualité",
            "• 256 kbps - Qualité élevée, recommandée",
            "• 320 kbps - Qualité maximale, taille importante",
            "• Qualité maximale - Qualité source préservée"
        ]
        
        for quality in qualities:
            quality_label = MacTubeTheme.create_label_body(self.content_frame, quality)
            quality_label.pack(pady=1, padx=20, anchor="w")
            
    def show_transcodeur_section(self):
        """Section transcodeur"""
        title = MacTubeTheme.create_label_title(self.content_frame, "🔄 Transcodeur")
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Description
        desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Convertissez vos fichiers audio et vidéo entre différents formats\navec FFmpeg intégré."
        )
        desc.pack(pady=(0, 20), padx=20, anchor="w")
        
        # Les 3 fonctions du transcodeur
        functions_title = MacTubeTheme.create_label_section(self.content_frame, "🎬 Les 3 fonctions du transcodeur")
        functions_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Fonction 1: Conversion Vidéo
        video_title = MacTubeTheme.create_label_section(self.content_frame, "🎬 1. Conversion Vidéo")
        video_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        video_desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Convertissez vos fichiers vidéo entre différents formats.\nSélectionnez un fichier vidéo, choisissez le format de sortie\n(MP4, MKV, WebM, AVI, MOV) et le dossier de destination."
        )
        video_desc.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Fonction 2: Extraction Audio depuis Vidéo
        audio_extract_title = MacTubeTheme.create_label_section(self.content_frame, "🎵 2. Extraction Audio depuis Vidéo")
        audio_extract_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        audio_extract_desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Extrayez l'audio d'un fichier vidéo existant.\nSélectionnez un fichier vidéo, choisissez le format audio de sortie\net la qualité, puis lancez l'extraction."
        )
        audio_extract_desc.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Fonction 3: Conversion Audio
        audio_conv_title = MacTubeTheme.create_label_section(self.content_frame, "🔄 3. Conversion Audio")
        audio_conv_title.pack(pady=(15, 10), padx=20, anchor="w")
        
        audio_conv_desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Convertissez vos fichiers audio entre différents formats.\nSélectionnez un fichier audio, choisissez le format de sortie\n(MP3, M4A, AAC, FLAC, WAV, OGG) et la qualité audio."
        )
        audio_conv_desc.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Formats supportés
        formats_title = MacTubeTheme.create_label_section(self.content_frame, "🎯 Formats supportés")
        formats_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        formats = [
            "• Formats vidéo : MP4, MKV, WebM, AVI, MOV",
            "• Formats audio : MP3, M4A, AAC, FLAC, WAV, OGG",
            "• Qualités audio : 128, 192, 256, 320 kbps ou qualité maximale"
        ]
        
        for format_info in formats:
            format_label = MacTubeTheme.create_label_body(self.content_frame, format_info)
            format_label.pack(pady=2, padx=20, anchor="w")
            
    def show_file_attente_section(self):
        """Section file d'attente"""
        title = MacTubeTheme.create_label_title(self.content_frame, "📋 File d'attente")
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Description
        desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Gérez vos téléchargements et conversions avec la file d'attente intelligente.\nSuivez l'avancement en temps réel."
        )
        desc.pack(pady=(0, 20), padx=20, anchor="w")
        
        # Fonctionnalités
        features_title = MacTubeTheme.create_label_section(self.content_frame, "⚡ Fonctionnalités")
        features_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        features = [
            "• Téléchargements simultanés (max 2 par défaut)",
            "• Suivi en temps réel de la progression",
            "• Gestion des priorités et ordre d'exécution",
            "• Bouton 'Reprendre' pour relancer la file",
            "• Bouton 'Vider la file' pour nettoyer et supprimer les fichiers temporaires",
            "• Historique des tâches terminées"
        ]
        
        for feature in features:
            feature_label = MacTubeTheme.create_label_body(self.content_frame, feature)
            feature_label.pack(pady=2, padx=20, anchor="w")
            
        # Nettoyage automatique
        cleanup_title = MacTubeTheme.create_label_section(self.content_frame, "🧹 Nettoyage automatique")
        cleanup_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        cleanup_info = MacTubeTheme.create_label_body(
            self.content_frame,
            "Le bouton 'Vider la file d'attente' supprime automatiquement tous les fichiers\ntemporaires (.part, .ytdl, .tmp, .download, .ytdlp) de tous les dossiers\nutilisés par l'application."
        )
        cleanup_info.pack(pady=(0, 20), padx=20, anchor="w")
        
    def show_historique_section(self):
        """Section historique"""
        title = MacTubeTheme.create_label_title(self.content_frame, "📚 Historique")
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Description
        desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Consultez l'historique complet de vos téléchargements et conversions."
        )
        desc.pack(pady=(0, 20), padx=20, anchor="w")
        
        # Fonctionnalités
        features_title = MacTubeTheme.create_label_section(self.content_frame, "📊 Informations disponibles")
        features_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        features = [
            "• URL de la source",
            "• Titre du fichier",
            "• Format et qualité",
            "• Date et heure du téléchargement",
            "• Taille du fichier",
            "• Statut de la tâche"
        ]
        
        for feature in features:
            feature_label = MacTubeTheme.create_label_body(self.content_frame, feature)
            feature_label.pack(pady=2, padx=20, anchor="w")
            
        # Gestion
        management_title = MacTubeTheme.create_label_section(self.content_frame, "⚙️ Gestion de l'historique")
        management_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        management = [
            "• Affichage chronologique des tâches",
            "• Filtrage par type de tâche",
            "• Nettoyage automatique à la fermeture",
            "• Export des données (optionnel)"
        ]
        
        for item in management:
            item_label = MacTubeTheme.create_label_body(self.content_frame, item)
            item_label.pack(pady=1, padx=20, anchor="w")
            
    def show_parametres_section(self):
        """Section paramètres"""
        title = MacTubeTheme.create_label_title(self.content_frame, "⚙️ Paramètres")
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Description
        desc = MacTubeTheme.create_label_body(
            self.content_frame,
            "Configurez MacTube selon vos préférences et besoins."
        )
        desc.pack(pady=(0, 20), padx=20, anchor="w")
        
        # Thème
        theme_title = MacTubeTheme.create_label_section(self.content_frame, "🎨 Thème de l'interface")
        theme_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        theme_options = [
            "• Système - Utilise le thème du système macOS",
            "• Clair - Thème clair forcé",
            "• Sombre - Thème sombre forcé"
        ]
        
        for option in theme_options:
            option_label = MacTubeTheme.create_label_body(self.content_frame, option)
            option_label.pack(pady=2, padx=20, anchor="w")
            
        # Paramètres avancés
        advanced_title = MacTubeTheme.create_label_section(self.content_frame, "🔧 Paramètres avancés")
        advanced_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        advanced_options = [
            "• Ignorer les erreurs SSL (recommandé pour macOS)",
            "• Retry automatique en cas d'échec"
        ]
        
        for option in advanced_options:
            option_label = MacTubeTheme.create_label_body(self.content_frame, option)
            option_label.pack(pady=2, padx=20, anchor="w")
            
        # Gestion de la file d'attente
        queue_title = MacTubeTheme.create_label_section(self.content_frame, "📋 Gestion de la file d'attente")
        queue_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        queue_options = [
            "• Téléchargements simultanés : 1 à 5 (slider)",
            "• Bouton 'Vider la file d'attente' avec nettoyage automatique des fichiers temporaires"
        ]
        
        for option in queue_options:
            option_label = MacTubeTheme.create_label_body(self.content_frame, option)
            option_label.pack(pady=2, padx=20, anchor="w")
        

        
    def show_faq_section(self):
        """Section FAQ"""
        title = MacTubeTheme.create_label_title(self.content_frame, "❓ Questions Fréquentes")
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # FAQ
        faq_items = [
            {
                "question": "Comment télécharger une vidéo YouTube ?",
                "answer": "Collez l'URL dans le champ URL, cliquez sur 'Analyser',\nchoisissez la qualité et le format, puis cliquez sur 'Télécharger'."
            },
            {
                "question": "Quels formats sont supportés ?",
                "answer": "Vidéo : MP4, MKV, WebM, AVI, MOV.\nAudio : MP3, M4A, AAC, FLAC, WAV, OGG."
            },
            {
                "question": "Comment extraire l'audio d'une vidéo ?",
                "answer": "Utilisez l'onglet 'Extraction Audio' ou le module 'Transcodeur'\npour convertir une vidéo en fichier audio."
            },
            {
                "question": "Que fait le bouton 'Vider la file d'attente' ?",
                "answer": "Il vide la file d'attente et supprime automatiquement tous les fichiers\ntemporaires (.part, .ytdl, etc.) de tous les dossiers utilisés."
            }
        ]
        
        for i, faq in enumerate(faq_items, 1):
            # Question
            question_label = MacTubeTheme.create_label_section(
                self.content_frame, 
                f"Q{i}: {faq['question']}"
            )
            question_label.pack(pady=(20, 10), padx=20, anchor="w")
            
            # Réponse
            answer_label = MacTubeTheme.create_label_body(
                self.content_frame,
                f"R: {faq['answer']}"
            )
            answer_label.pack(pady=(0, 15), padx=20, anchor="w")
            
    def _create_github_icon(self, size=16):
        """Crée une icône GitHub avec fallback"""
        try:
            from PIL import Image
            github_image = Image.open("icones/github.png").convert("RGBA")
            return ctk.CTkImage(light_image=github_image, size=(size, size))
        except Exception as e:
            print(f"⚠️ Impossible de charger l'icône GitHub: {e}")
            return None
            
    def show_support_section(self):
        """Section support"""
        # Titre avec icône GitHub
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(pady=(20, 15), padx=20, fill="x")
        
        # Icône GitHub dans le titre
        github_title_icon = self._create_github_icon(24)
        if github_title_icon:
            github_title_icon_label = ctk.CTkLabel(
                title_frame,
                image=github_title_icon,
                text=""
            )
            github_title_icon_label.pack(side="left")
        else:
            # Fallback avec emoji globe
            fallback_icon = ctk.CTkLabel(
                title_frame,
                text="🌐",
                font=ctk.CTkFont(size=24)
            )
            fallback_icon.pack(side="left")
        
        # Titre "Support"
        title_text = MacTubeTheme.create_label_title(title_frame, "Support")
        title_text.pack(side="left", padx=(10, 0))
        
        # Lien GitHub avec icône
        github_text = ctk.CTkLabel(
            self.content_frame,
            text="Pour toute question, merci de visiter le GitHub :",
            font=ctk.CTkFont(size=12),
            text_color=MacTubeTheme.get_color('text_primary'),
            anchor="w",
            justify="left"
        )
        github_text.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Frame pour l'icône et le lien
        github_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        github_frame.pack(pady=(0, 20), padx=20, fill="x")
        
        # Icône GitHub
        github_icon = self._create_github_icon(16)
        if github_icon:
            github_icon_label = ctk.CTkLabel(
                github_frame,
                image=github_icon,
                text=""
            )
            github_icon_label.pack(side="left")
        else:
            # Fallback avec emoji globe
            fallback_icon = ctk.CTkLabel(
                github_frame,
                text="🌐",
                font=ctk.CTkFont(size=16)
            )
            fallback_icon.pack(side="left")
        
        # Lien GitHub
        github_link = ctk.CTkLabel(
            github_frame,
            text="https://github.com/ITchrisDEB/MacTube",
            font=ctk.CTkFont(size=12, underline=True),
            text_color=MacTubeTheme.get_color('primary'),
            anchor="w",
            justify="left",
            cursor="hand2"
        )
        github_link.pack(side="left", padx=(10, 0))
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/ITchrisDEB/MacTube"))
        
    def on_search(self, event=None):
        """Gère la recherche en temps réel"""
        query = self.search_entry.get().strip().lower()
        if len(query) >= 2:
            self.perform_search()
            
    def perform_search(self):
        """Effectue la recherche dans l'aide"""
        query = self.search_entry.get().strip().lower()
        if not query:
            return
            
        # Recherche simple dans le contenu
        search_results = []
        
        # Sections à rechercher
        sections = {
            "téléchargement": "telechargement",
            "download": "telechargement",
            "vidéo": "telechargement",
            "video": "telechargement",
            "audio": "audio",
            "extraction": "audio",
            "transcodeur": "transcodeur",
            "conversion": "transcodeur",
            "file d'attente": "file_attente",
            "queue": "file_attente",
            "historique": "historique",
            "history": "historique",
            "paramètres": "parametres",
            "settings": "parametres",
            "ffmpeg": "ffmpeg",
            "faq": "faq",
            "question": "faq",
            "support": "support",
            "aide": "accueil",
            "help": "accueil"
        }
        
        # Rechercher dans les sections
        for keyword, section in sections.items():
            if query in keyword:
                search_results.append(section)
                break
                
        # Si des résultats trouvés, afficher la première section
        if search_results:
            self.show_section(search_results[0])
        else:
            # Afficher la section d'accueil avec un message
            self.show_section("accueil")
            messagebox.showinfo("Recherche", f"Aucun résultat trouvé pour '{query}'. Essayez d'autres mots-clés.")
            
    def create_blue_icon_button(self, parent, text, command, width=200):
        """Crée un bouton avec icône bleue (même style que l'app principale)"""
        # Créer le bouton avec la couleur bleue du thème (primary)
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=MacTubeTheme.get_color('primary'),  # Couleur bleue (#007AFF)
            hover_color=MacTubeTheme.get_color('secondary'),  # Vert au survol (#34C759)
            text_color=MacTubeTheme.get_color('text_light'),  # Texte blanc
            corner_radius=8
        )
        return button
        
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.help_window.update_idletasks()
        width = self.help_window.winfo_width()
        height = self.help_window.winfo_height()
        x = (self.help_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.help_window.winfo_screenheight() // 2) - (height // 2)
        self.help_window.geometry(f'{width}x{height}+{x}+{y}')
        
    def show(self):
        """Affiche la fenêtre d'aide"""
        self.help_window.deiconify()
        self.help_window.lift()
        self.help_window.focus_force()

def create_help_menu(parent_app):
    """Crée le menu d'aide pour l'application principale"""
    # Créer la barre de menu si elle n'existe pas
    if not hasattr(parent_app, 'menubar'):
        parent_app.menubar = tk.Menu(parent_app.root)
        parent_app.root.config(menu=parent_app.menubar)
    
    # Menu Aide
    help_menu = tk.Menu(parent_app.menubar, tearoff=0)
    help_menu.add_command(label="Aide MacTube", command=lambda: MacTubeHelp(parent_app).show())
    help_menu.add_separator()
    help_menu.add_command(label="À propos de MacTube", command=lambda: show_about_dialog(parent_app))
    
    # Ajouter le menu Aide à la barre de menu
    parent_app.menubar.add_cascade(label="Aide", menu=help_menu)
    
    # Raccourci clavier Cmd+?
    parent_app.root.bind('<Command-Key-?>', lambda e: MacTubeHelp(parent_app).show())

def show_about_dialog(parent_app):
    """Affiche la boîte de dialogue À propos"""
    about_text = f"""MacTube {parent_app.app_version if hasattr(parent_app, 'app_version') else 'v1.2.5'}

© 2025 - Licence MIT
GitHub: https://github.com/ITchrisDEB/MacTube"""
    
    messagebox.showinfo("À propos de MacTube", about_text)

if __name__ == "__main__":
    # Test du système d'aide
    root = ctk.CTk()
    root.withdraw()  # Cacher la fenêtre principale
    
    help_system = MacTubeHelp()
    help_system.show()
    
    root.mainloop()
