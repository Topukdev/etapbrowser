#Tema Yöneticisi

import os

class ThemeManager:
    _instance = None
    _current_theme = "light"
    _stylesheet = ""
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
        return cls._instance
    
    def load_theme(self, theme_name="light"):
        """Temayı yükler (light veya dark)"""
        theme_path = f"./themes/{theme_name}.qss"
        
        if not os.path.exists(theme_path):
            print(f"Tema dosyası bulunamadı: {theme_path}")
            return False
        
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                self._stylesheet = f.read()
                self._current_theme = theme_name
            return True
        except Exception as e:
            print(f"Tema yükleme hatası: {e}")
            return False
    
    def get_stylesheet(self):
        """Mevcut tema stylesheet'ini döndürür"""
        return self._stylesheet
    
    def get_current_theme(self):
        """Mevcut tema ismini döndürür"""
        return self._current_theme
    
    def apply_to_app(self, app):
        """Temayı QApplication'a uygular"""
        app.setStyleSheet(self._stylesheet)
    
    def apply_to_widget(self, widget):
        """Temayı belirli bir widget'a uygular"""
        widget.setStyleSheet(self._stylesheet)


theme_manager = ThemeManager()