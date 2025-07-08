"""
Loglama sistemi
"""

import logging
import os
from datetime import datetime

class Logger:
    """Uygulama için loglama sınıfı"""
    
    def __init__(self, name="WebScraper", log_file=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Eğer handler zaten varsa tekrar ekleme
        if not self.logger.handlers:
            self._setup_handlers(log_file)
            
    def _setup_handlers(self, log_file):
        """Log handler'larını kurar"""
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file is None:
            # Logs klasörü oluştur
            logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            log_file = os.path.join(logs_dir, f"webscraper_{datetime.now().strftime('%Y%m%d')}.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
    def debug(self, message):
        """Debug seviyesinde log"""
        self.logger.debug(message)
        
    def info(self, message):
        """Info seviyesinde log"""
        self.logger.info(message)
        
    def warning(self, message):
        """Warning seviyesinde log"""
        self.logger.warning(message)
        
    def error(self, message):
        """Error seviyesinde log"""
        self.logger.error(message)
        
    def critical(self, message):
        """Critical seviyesinde log"""
        self.logger.critical(message)