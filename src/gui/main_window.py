# src/gui/main_window.py

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QTextEdit, 
                           QProgressBar, QCheckBox, QGroupBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from datetime import datetime

from ..core.scraper import WebScraper
from ..utils.logger import Logger
from ..utils.config import Config

class WorkerThread(QThread):
    """Web scraping işlemini arka planda çalıştıran thread"""
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str, int)
    
    def __init__(self, url, keyword, save_path, case_sensitive, whole_word):
        super().__init__()
        self.url = url
        self.keyword = keyword
        self.save_path = save_path
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word
        self.scraper = WebScraper()
        
    def run(self):
        """Thread'in ana çalışma fonksiyonu"""
        try:
            def progress_callback(message):
                self.progress_update.emit(message)
            
            pdf_path, match_count = self.scraper.scrape_and_save(
                self.url, self.keyword, self.save_path,
                self.case_sensitive, self.whole_word, progress_callback
            )
            
            self.finished.emit(True, pdf_path, match_count)
            
        except Exception as e:
            self.finished.emit(False, str(e), 0)

class MainWindow(QMainWindow):
    """Ana pencere sınıfı - Sadeleştirilmiş Versiyon"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.logger = Logger()
        self.worker_thread = None
        self.init_ui()
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlat"""
        self.setWindowTitle("Web Scraper PDF Generator v2.1")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.create_input_section(main_layout)
        self.create_options_section(main_layout)
        self.create_buttons_section(main_layout)
        self.create_progress_section(main_layout)
        self.create_results_section(main_layout)
        
        self.apply_styles()
        
    def create_input_section(self, layout):
        """Giriş alanları bölümünü oluşturur"""
        input_group = QGroupBox("Tarama Bilgileri")
        input_layout = QVBoxLayout(input_group)

        # URL
        input_layout.addWidget(QLabel("🌐 Taranacak Web Sitesi URL'si:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://ornek.com")
        input_layout.addWidget(self.url_input)

        # Keyword
        input_layout.addWidget(QLabel("🔍 Aranacak Anahtar Kelime:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Örn: sürdürülebilirlik")
        input_layout.addWidget(self.keyword_input)

        # Save Path
        save_layout = QHBoxLayout()
        self.save_path_input = QLineEdit(self.config.get('ui.default_save_path', os.path.expanduser("~/Desktop")))
        self.browse_button = QPushButton("📁 Gözat")
        self.browse_button.clicked.connect(self.browse_folder)
        save_layout.addWidget(self.save_path_input)
        save_layout.addWidget(self.browse_button)
        
        input_layout.addWidget(QLabel("💾 Raporun Kaydedileceği Klasör:"))
        input_layout.addLayout(save_layout)
        
        layout.addWidget(input_group)
        
    def create_options_section(self, layout):
        """Seçenekler bölümünü oluşturur"""
        options_group = QGroupBox("Arama Seçenekleri")
        options_layout = QHBoxLayout(options_group)
        
        self.case_sensitive_cb = QCheckBox("Büyük/Küçük Harfe Duyarlı Ara")
        self.whole_word_cb = QCheckBox("Sadece Tam Kelimeyi Eşleştir")
        self.whole_word_cb.setChecked(True) # Genellikle daha iyi sonuç verir
        
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.whole_word_cb)
        options_layout.addStretch()
        
        layout.addWidget(options_group)
        
    def create_buttons_section(self, layout):
        """Butonlar bölümünü oluşturur"""
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🚀 Taramayı Başlat")
        self.start_button.clicked.connect(self.start_scraping)
        self.start_button.setFixedHeight(45)
        
        self.stop_button = QPushButton("⏹️ Durdur")
        self.stop_button.clicked.connect(self.stop_scraping)
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedHeight(45)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
    def create_progress_section(self, layout):
        """Progress bar bölümünü oluşturur"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def create_results_section(self, layout):
        """Sonuçlar bölümünü oluşturur"""
        results_group = QGroupBox("İşlem Günlüğü")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        layout.addWidget(results_group)

    def start_scraping(self):
        """Tekil tarama işlemini başlatır"""
        url = self.url_input.text().strip()
        keyword = self.keyword_input.text().strip()
        save_path = self.save_path_input.text().strip()

        if not url or not url.startswith('http'):
            QMessageBox.warning(self, "Geçersiz URL", "Lütfen 'http://' veya 'https://' ile başlayan geçerli bir URL girin.")
            return
            
        if not keyword:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen aranacak bir anahtar kelime girin.")
            return
            
        if not os.path.isdir(save_path):
            QMessageBox.warning(self, "Geçersiz Yol", "Lütfen raporun kaydedileceği geçerli bir klasör seçin.")
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Sürekli dönen progress bar
        self.results_text.clear()
        
        self.worker_thread = WorkerThread(
            url, keyword, save_path,
            self.case_sensitive_cb.isChecked(), self.whole_word_cb.isChecked()
        )
        self.worker_thread.progress_update.connect(self.update_progress)
        self.worker_thread.finished.connect(self.scraping_finished)
        self.worker_thread.start()

    def stop_scraping(self):
        """Tarama işlemini durdurur"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate() # Arka plan işini anında sonlandırır
            self.worker_thread.wait()
            self.scraping_finished(False, "İşlem kullanıcı tarafından durduruldu.", 0)

    def scraping_finished(self, success, message, match_count):
        """Tarama bittiğinde çağrılır"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.update_progress(f"<b><font color='#2ecc71'>✓ İşlem başarıyla tamamlandı!</font></b>")
            self.update_progress(f"Raporunuz şu dosyaya kaydedildi: <b>{os.path.basename(message)}</b>")
            QMessageBox.information(self, "İşlem Tamamlandı", f"{match_count} adet eşleşme bulundu ve rapor oluşturuldu.")
        else:
            self.update_progress(f"<b><font color='#e74c3c'>✗ Hata Oluştu:</font></b> {message}")
            QMessageBox.critical(self, "Hata", f"İşlem sırasında bir hata oluştu:\n\n{message}")

    def update_progress(self, message):
        """İşlem günlüğünü günceller"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.append(f"<font color='#3498db'>[{timestamp}]</font> {message}")
        self.results_text.ensureCursorVisible()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Kayıt Klasörü Seç", self.save_path_input.text())
        if folder: self.save_path_input.setText(folder)
            
    def closeEvent(self, event):
        self.stop_scraping()
        event.accept()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #2c3e50; color: #ecf0f1; font-family: Arial; }
            QGroupBox { font-size: 14px; font-weight: bold; border: 1px solid #34495e; border-radius: 8px; margin-top: 10px; padding: 20px 10px 10px 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 10px; color: #1abc9c; }
            QLabel { font-size: 12px; padding-bottom: 2px; }
            QLineEdit { background-color: #34495e; border: 1px solid #7f8c8d; border-radius: 4px; padding: 8px; font-size: 13px; }
            QLineEdit:focus { border-color: #1abc9c; }
            QPushButton { background-color: #3498db; color: white; border: none; padding: 10px 18px; border-radius: 5px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1f618d; }
            QPushButton:disabled { background-color: #7f8c8d; color: #bdc3c7; }
            QTextEdit { background-color: #222b36; border: 1px solid #34495e; border-radius: 4px; font-family: Consolas, Courier New; font-size: 12px; color: #bdc3c7; }
            QCheckBox { spacing: 8px; font-size: 12px; }
            QProgressBar { border-radius: 5px; text-align: center; }
            QProgressBar::chunk { background-color: #1abc9c; border-radius: 4px; }
        """)