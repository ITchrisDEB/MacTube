#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MacTube Theme - Thème moderne pour MacTube (YouTube Downloader pour macOS)
"""

import customtkinter as ctk
import darkdetect

class MacTubeTheme:
    """Gestionnaire de thème pour MacTube"""
    
    # Couleurs MacTube
    COLORS = {
        # Couleurs principales
        'primary': "#007AFF",      # Bleu macOS
        'secondary': "#34C759",    # Vert macOS
        'accent': "#FF9500",       # Orange macOS
        'danger': "#FF3B30",       # Rouge macOS
        
        # Arrière-plans
        'bg_primary': "#F2F2F7",       # Gris clair macOS
        'bg_secondary': "#FFFFFF",     # Blanc
        'bg_header': "#E5E5EA",        # Gris header
        'bg_card': "#FFFFFF",          # Blanc carte
        'bg_tertiary': "#F9F9FB",      # Gris très léger pour zones secondaires
        'border': "#D1D1D6",           # Gris bordure clair
        
        # Textes
        'text_primary': "#000000",     # Noir
        'text_secondary': "#8E8E93",   # Gris secondaire
        'text_light': "#FFFFFF",       # Blanc
        
        # Mode sombre
        'dark': {
            'bg_primary': "#1C1C1E",
            'bg_secondary': "#2C2C2E", 
            'bg_header': "#3A3A3C",
            'bg_card': "#2C2C2E",
            'bg_tertiary': "#3A3A3C",   # Légèrement plus clair pour contraster
            'border': "#48484A",        # Gris bordure sombre
            'text_primary': "#FFFFFF",
            'text_secondary': "#8E8E93"
        }
    }
    
    @classmethod
    def get_color(cls, color_name):
        """Récupère une couleur selon le thème actuel"""
        # Vérifier le thème CustomTkinter actuel
        try:
            import customtkinter as ctk
            current_theme = ctk.get_appearance_mode()
            is_dark = (current_theme.lower() == "dark")  # Accepter 'Dark' et 'dark'
        except Exception as e:
            # Fallback sur darkdetect
            is_dark = darkdetect.isDark()
        
        if is_dark and color_name in cls.COLORS['dark']:
            color = cls.COLORS['dark'][color_name]
            return color
        
        color = cls.COLORS.get(color_name, "#000000")
        return color
    
    @classmethod
    def force_dark_mode(cls):
        """Force le mode sombre pour tous les composants"""
        ctk.set_appearance_mode("dark")
        
        # Mettre à jour les couleurs globales
        ctk.set_default_color_theme("dark-blue")
        
        return True
    
    @classmethod
    def force_light_mode(cls):
        """Force le mode clair pour tous les composants"""
        ctk.set_appearance_mode("light")
        
        # Mettre à jour les couleurs globales
        ctk.set_default_color_theme("blue")
        
        return True
    
    @classmethod
    def create_label_title(cls, parent, text):
        """Crée un label de titre"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=cls.get_color('text_primary')
        )
    
    @classmethod
    def create_label_section(cls, parent, text):
        """Crée un label de section"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=cls.get_color('text_primary')
        )
    
    @classmethod
    def create_label_body(cls, parent, text):
        """Crée un label de corps de texte"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=12),
            text_color=cls.get_color('text_primary')
        )
    
    @classmethod
    def create_button_primary(cls, parent, text, command=None, **kwargs):
        """Crée un bouton principal"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=cls.get_color('primary'),
            hover_color=cls.get_color('secondary'),
            corner_radius=8,
            height=35,
            **kwargs
        )
    
    @classmethod
    def create_button_success(cls, parent, text, command=None, **kwargs):
        """Crée un bouton de succès"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=cls.get_color('secondary'),
            hover_color=cls.get_color('primary'),
            corner_radius=8,
            height=40,
            **kwargs
        )
    
    @classmethod
    def create_button_secondary(cls, parent, text, command=None, **kwargs):
        """Crée un bouton secondaire"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=cls.get_color('accent'),
            hover_color=cls.get_color('primary'),
            corner_radius=8,
            height=35,
            **kwargs
        )
    
    @classmethod
    def create_entry_modern(cls, parent, placeholder):
        """Crée un champ de saisie moderne"""
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            font=ctk.CTkFont(size=12),
            corner_radius=8,
            height=35,
            border_width=1,
            border_color=cls.get_color('text_secondary')
        )
    
    @classmethod
    def create_card_frame(cls, parent):
        """Crée un frame de carte"""
        return ctk.CTkFrame(
            parent,
            fg_color=cls.get_color('bg_card'),
            corner_radius=12,
            border_width=1,
            border_color=cls.get_color('text_secondary')
        )

def setup_mactube_theme():
    """Configure le thème MacTube"""
    try:
        # Détecter le thème système
        is_dark = darkdetect.isDark()
        
        if is_dark:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        
        # Définir le thème de couleur
        ctk.set_default_color_theme("blue")
        
        print("✅ Thème MacTube configuré")
        
    except Exception as e:
        print(f"⚠️  Configuration thème partielle: {e}")
        ctk.set_appearance_mode("system")
