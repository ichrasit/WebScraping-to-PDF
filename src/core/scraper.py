# src/core/scraper.py

import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse
from ..utils.logger import Logger
from ..utils.pdf_generator import PDFGenerator

class WebScraper:
    """Web scraping işlemlerini gerçekleştiren, sadeleştirilmiş ana sınıf"""
    
    def __init__(self):
        self.logger = Logger()
        self.pdf_generator = PDFGenerator()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        })
        
    def scrape_and_save(self, url, keyword, save_path, case_sensitive=False, whole_word=False, progress_callback=None):
        """
        Web sitesini tarar ve sonuçları PDF'e kaydeder.
        """
        try:
            if progress_callback: progress_callback(f"🌐 {url} adresine bağlanılıyor...")
            response = self._fetch_page(url)
            
            if progress_callback: progress_callback("📄 Sayfa içeriği analiz ediliyor...")
            soup = BeautifulSoup(response.content, 'html.parser')
            page_info = self._extract_page_info(soup, url)
            
            if progress_callback: progress_callback(f"🔍 '{keyword}' kelimesi aranıyor...")
            text_content = self._get_clean_text(soup)
            matches = self._find_matches_in_text(text_content, keyword, case_sensitive, whole_word)
            
            if progress_callback: progress_callback(f"✅ {len(matches)} adet eşleşme bulundu.")
            
            # PDF oluştur (eşleşme olmasa bile özet raporu oluşturulur)
            if progress_callback: progress_callback("📝 PDF raporu oluşturuluyor...")
            pdf_path = self.pdf_generator.create_pdf(
                matches, keyword, page_info, save_path, 
                case_sensitive, whole_word
            )
            
            if progress_callback: progress_callback(f"💾 PDF kaydedildi: {os.path.basename(pdf_path)}")
            return pdf_path, len(matches)
                
        except Exception as e:
            self.logger.error(f"Scraping hatası: {str(e)}")
            raise
            
    def _fetch_page(self, url):
        """Web sayfasını getirir."""
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Sayfa erişim hatası: {e}")
            
    def _extract_page_info(self, soup, url):
        """Sayfa meta bilgilerini çıkarır."""
        title_tag = soup.find('title')
        page_title = title_tag.get_text(strip=True) if title_tag else "Başlık Bulunamadı"
        
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc_tag.get('content', 'Açıklama bulunamadı.') if meta_desc_tag else 'Açıklama bulunamadı.'
        
        domain = urlparse(url).netloc
        
        return {
            'title': page_title,
            'url': url,
            'domain': domain,
            'description': description[:300] + '...' if len(description) > 300 else description
        }
        
    def _get_clean_text(self, soup):
        """Sayfadaki tüm görünür metni temiz bir şekilde alır."""
        # İstenmeyen tag'leri kaldır
        for element in soup(["script", "style", "noscript", "link", "meta", "header", "footer", "nav"]):
            element.decompose()
        
        # Sadece body içindeki metni al, daha temiz sonuç verir
        body = soup.find('body')
        if not body:
            return ""

        text = body.get_text(separator=' ', strip=True)
        # Çoklu boşlukları ve sekmeleri tek boşluğa indir
        text = re.sub(r'\s+', ' ', text)
        return text

    def _find_matches_in_text(self, text, keyword, case_sensitive, whole_word):
        """Verilen metin içinde anahtar kelime eşleşmelerini bulur."""
        matches = []
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        if whole_word:
            # \b kelime sınırı demektir. 'veri' ararken 'verimli' bulmaz.
            pattern = r'\b' + re.escape(keyword) + r'\b'
        else:
            pattern = re.escape(keyword)

        for i, match in enumerate(re.finditer(pattern, text, flags)):
            start_pos = match.start()
            end_pos = match.end()
            
            # Eşleşmenin etrafından bağlam (context) al
            context_start = max(0, start_pos - 150)
            context_end = min(len(text), end_pos + 150)
            context = text[context_start:context_end].strip()
            
            matches.append({
                'context': context,
                'position': start_pos,
                'match_number': i + 1,
            })
        return matches