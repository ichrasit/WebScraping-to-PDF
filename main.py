#!/usr/bin/env python3
"""
Web Scraper PDF Generator - Ana Çalıştırma Dosyası
Yazar: [Your Name]
Tarih: 2025
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Proje dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui.main_window import MainWindow
from src.utils.logger import Logger

def main():
    """Ana fonksiyon - Uygulamayı başlatır"""
    # Qt uygulama objesi oluştur
    app = QApplication(sys.argv)
    
    # Uygulama ayarları
    app.setApplicationName("Web Scraper PDF Generator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("WebScraperApp")
    
    # High DPI desteği
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Ana pencereyi oluştur
    window = MainWindow()
    window.show()
    
    # Logger'ı başlat
    logger = Logger()
    logger.info("Uygulama başlatıldı")
    
    # Uygulama döngüsünü başlat
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()