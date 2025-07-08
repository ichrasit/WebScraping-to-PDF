"""
Uygulama konfigürasyonu
"""

import os
import json
from pathlib import Path

class Config:
    """Uygulama konfigürasyon sınıfı"""
    
    def __init__(self):
        self.config_file = self._get_config_file()
        self.config = self._load_config()
        
    def _get_config_file(self):
        """Config dosyasının yolunu döndürür"""
        config_dir = Path.home() / '.webscraper'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'config.json'
        
    def _load_config(self):
        """Config dosyasını yükler"""
        default_config = {
            'app': {
                'name': 'Web Scraper PDF Generator',
                'version': '1.0.0',
                'author': 'WebScraper Team'
            },
            'scraper': {
                'timeout': 30,
                'max_retries': 3,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'context_length': 300
            },
            'pdf': {
                'page_size': 'A4',
                'margin_top': 72,
                'margin_bottom': 18,
                'margin_left': 72,
                'margin_right': 72,
                'font_size': 10,
                'highlight_color': 'red'
            },
            'ui': {
                'theme': 'default',
                'window_width': 1000,
                'window_height': 700,
                'default_save_path': str(Path.home() / 'Desktop')
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Eksik anahtarları varsayılan değerlerle doldur
                    return self._merge_config(default_config, config)
            except Exception:
                pass
        
        # Varsayılan config'i kaydet
        self._save_config(default_config)
        return default_config
        
    def _merge_config(self, default, user):
        """Kullanıcı ve varsayılan config'i birleştirir"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
        
    def _save_config(self, config):
        """Config'i dosyaya kaydeder"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
            
    def get(self, key, default=None):
        """Config değerini getirir"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
        
    def set(self, key, value):
        """Config değerini ayarlar"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config(self.config)
        
    def get_app_info(self):
        """Uygulama bilgilerini döndürür"""
        return self.config.get('app', {})
        
    def get_scraper_settings(self):
        """Scraper ayarlarını döndürür"""
        return self.config.get('scraper', {})
        
    def get_pdf_settings(self):
        """PDF ayarlarını döndürür"""
        return self.config.get('pdf', {})
        
    def get_ui_settings(self):
        """UI ayarlarını döndürür"""
        return self.config.get('ui', {})