# src/utils/pdf_generator.py

import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PDFGenerator:
    """
    Basit, tekil analizler için PDF raporu oluşturan sınıf.
    Türkçe karakter ve font hatası çözüldü.
    """
    
    def __init__(self):
        self._register_fonts()
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _register_fonts(self):
        """Türkçe karakterleri destekleyen DejaVuSans fontunu ReportLab'e kaydeder."""
        try:
            # Proje kök dizininden assets klasörüne ulaş
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            assets_path = os.path.join(base_path, 'assets')
            
            regular_font_path = os.path.join(assets_path, 'DejaVuSans.ttf')
            bold_font_path = os.path.join(assets_path, 'DejaVuSans-Bold.ttf')

            if not os.path.exists(regular_font_path) or not os.path.exists(bold_font_path):
                 # Bu hata, programı durdurmaz ama terminalde net bir uyarı verir.
                 print("="*50)
                 print("!!! FONT UYARISI !!!")
                 print(f"Font dosyaları bulunamadı. Lütfen projenizin ana dizinindeki 'assets' klasörüne 'DejaVuSans.ttf' ve 'DejaVuSans-Bold.ttf' dosyalarını ekleyin.")
                 print(f"Aranan yol: {assets_path}")
                 print("="*50)
                 # Fontlar yoksa, devam etmenin anlamı yok.
                 raise FileNotFoundError("Gerekli font dosyaları 'assets' klasöründe bulunamadı.")

            pdfmetrics.registerFont(TTFont('DejaVuSans', regular_font_path))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))
            # Font ailesini tanımlayarak bold/italic eşleşmesini sağlıyoruz
            pdfmetrics.registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans-Bold', italic='DejaVuSans', boldItalic='DejaVuSans-Bold')
        except Exception as e:
            print(f"HATA: Fontlar yüklenirken kritik bir sorun oluştu: {e}")
            raise  # Font yüklenemezse programın devam etmemesi daha sağlıklı

    def _create_custom_styles(self):
        """Özel PDF stillerini oluşturur."""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            fontName='DejaVuSans-Bold',
            fontSize=20,
            spaceAfter=25,
            textColor=HexColor('#2c3e50'),
            alignment=TA_CENTER,
        )
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            fontName='DejaVuSans-Bold',
            fontSize=14,
            spaceAfter=15,
            textColor=HexColor('#34495e'),
            alignment=TA_LEFT,
        )
        self.info_style = ParagraphStyle(
            'InfoStyle',
            fontName='DejaVuSans',
            fontSize=10,
            leading=14
        )
        self.match_style = ParagraphStyle(
            'MatchStyle',
            fontName='DejaVuSans',
            fontSize=10,
            leading=15,
            spaceAfter=20,
            leftIndent=20,
            rightIndent=20,
            alignment=TA_JUSTIFY,
            borderWidth=1,
            borderColor=HexColor('#cccccc'),
            borderPadding=12,
            backColor=HexColor('#f9f9f9')
        )

    def create_pdf(self, matches, keyword, page_info, save_path, case_sensitive, whole_word):
        """PDF dosyasını oluşturur."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = re.sub(r'[^\w\s-]', '', keyword).strip().replace(' ', '_')
        filename = f"Rapor_{safe_keyword}_{timestamp}.pdf"
        pdf_path = os.path.join(save_path, filename)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=inch, bottomMargin=inch, leftMargin=inch, rightMargin=inch)
        story = []

        story.append(Paragraph("Web Sitesi Anahtar Kelime Raporu", self.title_style))
        story.append(Spacer(1, 15))
        
        story.extend(self._create_info_section(page_info, keyword, len(matches), case_sensitive, whole_word))
        
        if matches:
            story.extend(self._create_matches_section(matches, keyword, case_sensitive))
        else:
            story.append(Paragraph("Belirtilen anahtar kelime için sayfada eşleşme bulunamadı.", self.info_style))

        doc.build(story)
        return pdf_path

    def _create_info_section(self, page_info, keyword, match_count, case_sensitive, whole_word):
        """Bilgi bölümünü oluşturur."""
        content = [Paragraph("Tarama Özeti", self.subtitle_style), Spacer(1, 10)]
        
        # None olabilecek değerler için kontrol
        title = self._escape_html(page_info.get('title', 'Başlık Bulunamadı'))
        url = self._escape_html(page_info.get('url', 'URL Bilgisi Yok'))
        description = self._escape_html(page_info.get('description', 'Açıklama Yok'))

        info_data = [
            [Paragraph('<b>Sayfa Başlığı:</b>', self.info_style), Paragraph(title, self.info_style)],
            [Paragraph('<b>URL:</b>', self.info_style), Paragraph(f'<a href="{url}" color="blue">{url}</a>', self.info_style)],
            [Paragraph('<b>Açıklama:</b>', self.info_style), Paragraph(description, self.info_style)],
            [Paragraph('<b>Aranan Kelime:</b>', self.info_style), Paragraph(self._escape_html(keyword), self.info_style)],
            [Paragraph('<b>Bulunan Eşleşme Sayısı:</b>', self.info_style), Paragraph(str(match_count), self.info_style)],
            [Paragraph('<b>Büyük/Küçük Harf:</b>', self.info_style), Paragraph('Duyarlı' if case_sensitive else 'Duyarsız', self.info_style)],
            [Paragraph('<b>Eşleştirme Türü:</b>', self.info_style), Paragraph('Tam Kelime' if whole_word else 'İçinde Geçen', self.info_style)],
            [Paragraph('<b>Rapor Tarihi:</b>', self.info_style), Paragraph(datetime.now().strftime('%d.%m.%Y %H:%M:%S'), self.info_style)],
        ]
        
        table = Table(info_data, colWidths=[2.2*inch, 4.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#dddddd')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        return content

    def _create_matches_section(self, matches, keyword, case_sensitive):
        """Eşleşmeler bölümünü oluşturur."""
        content = [Paragraph("Bulunan Eşleşmeler", self.subtitle_style), Spacer(1, 10)]
        
        for i, match in enumerate(matches):
            context = self._highlight_keyword(match['context'], keyword, case_sensitive)
            # Match number'ı kalın ve mavi yap
            match_header = f"<b><font color='#3498db'>Eşleşme #{i+1}</font></b> (Pozisyon: {match['position']})"
            content.append(Paragraph(match_header, self.info_style))
            # Asıl eşleşmeyi kutu içinde göster
            content.append(Paragraph(f"...{context}...", self.match_style))
            
        return content

    def _highlight_keyword(self, text, keyword, case_sensitive):
        """Metinde anahtar kelimeyi <font> etiketi ile vurgular."""
        text = self._escape_html(text)
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.escape(keyword)
        
        # Kelimenin kendisini kırmızı ve kalın yap
        highlighted_text = re.sub(
            f'({pattern})',
            r'<font color="#e74c3c"><b>\1</b></font>',
            text,
            flags=flags
        )
        return highlighted_text

    def _escape_html(self, text):
        """ReportLab Paragraph için temel HTML karakterlerini escape eder."""
        if not text: return ""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")