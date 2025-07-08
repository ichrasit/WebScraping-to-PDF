"""
Executable oluşturucu script
PyInstaller kullanarak Windows ve macOS için executable oluşturur
"""

import os
import sys
import subprocess
import platform

def build_executable():
    """Executable dosyasını oluşturur"""
    
    # Platform kontrolü
    current_platform = platform.system()
    print(f"Platform: {current_platform}")
    
    # PyInstaller komutu
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=WebScraperPDF",
        "--icon=assets/icon.ico" if current_platform == "Windows" else "--icon=assets/icon.icns",
        "--add-data=src;src",
        "--hidden-import=PyQt5.sip",
        "--hidden-import=requests",
        "--hidden-import=beautifulsoup4",
        "--hidden-import=reportlab",
        "--hidden-import=lxml",
        "main.py"
    ]
    
    # Icon dosyası yoksa parametreyi kaldır
    if not os.path.exists("assets/icon.ico") and not os.path.exists("assets/icon.icns"):
        cmd = [item for item in cmd if not item.startswith("--icon")]
    
    print("Executable oluşturuluyor...")
    print(f"Komut: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable başarıyla oluşturuldu!")
        print(f"Çıktı: dist/WebScraperPDF{'.exe' if current_platform == 'Windows' else ''}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Hata: {e}")
        print(f"Stderr: {e.stderr}")
        return False
        
    except FileNotFoundError:
        print("❌ PyInstaller bulunamadı. Lütfen yükleyin:")
        print("pip install pyinstaller")
        return False
    
    return True

def create_installer():
    """Windows için installer oluşturur (NSIS gerekli)"""
    if platform.system() != "Windows":
        print("Installer sadece Windows için desteklenmektedir.")
        return
    
    nsis_script = """
    !define APPNAME "Web Scraper PDF Generator"
    !define COMPANYNAME "WebScraper Team"
    !define DESCRIPTION "Web sitelerinden keyword araması yaparak PDF raporu oluşturan uygulama"
    !define VERSIONMAJOR 1
    !define VERSIONMINOR 0
    !define VERSIONBUILD 0
    !define HELPURL "https://github.com/ichrasit/webscrapertopdf"
    !define UPDATEURL "https://github.com/webscraper/webscraper-pdf-generator/releases"
    !define ABOUTURL "https://github.com/webscraper/webscraper-pdf-generator"
    
    !define INSTALLSIZE 50000
    
    Name "${APPNAME}"
    Icon "assets\\icon.ico"
    outFile "WebScraperPDF_Setup.exe"
    
    InstallDir "$PROGRAMFILES\\${APPNAME}"
    
    page directory
    page instfiles
    
    section "install"
        setOutPath $INSTDIR
        file "dist\\WebScraperPDF.exe"
        
        writeUninstaller "$INSTDIR\\uninstall.exe"
        
        createDirectory "$SMPROGRAMS\\${APPNAME}"
        createShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\WebScraperPDF.exe"
        createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\WebScraperPDF.exe"
    sectionEnd
    
    section "uninstall"
        delete "$INSTDIR\\WebScraperPDF.exe"
        delete "$INSTDIR\\uninstall.exe"
        
        delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
        delete "$DESKTOP\\${APPNAME}.lnk"
        
        rmDir "$SMPROGRAMS\\${APPNAME}"
        rmDir "$INSTDIR"
    sectionEnd
    """
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_script)
    
    print("NSIS script oluşturuldu: installer.nsi")
    print("Installer oluşturmak için: makensis installer.nsi")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "installer":
        create_installer()
    else:
        build_executable()