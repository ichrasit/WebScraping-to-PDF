# build.py

import os
import sys
import subprocess
import platform

def get_separator():
    """İşletim sistemine göre doğru yol ayıracını döndürür."""
    return ';' if platform.system() == "Windows" else ':'

def build_executable():
    """Uygulama için çalıştırılabilir dosyayı oluşturur."""
    
    app_name = "WebScraperPDF"
    main_script = "main.py"
    icon_path = os.path.join("assets", "icon.ico")
    
    # Platforma özel ayarları yap
    separator = get_separator()
    
    # PyInstaller komutunu oluştur
    # --windowed: Arayüzlü uygulamalar için terminal penceresini gizler.
    # --onefile: Tüm bağımlılıkları tek bir .exe dosyasına paketler.
    # --add-data: Fontlar ve resimler gibi ek dosyaları pakete ekler.
    cmd = [
        "pyinstaller",
        "--noconfirm",  # Mevcut dist/build klasörlerini sormadan siler
        "--onefile",
        "--windowed",
        f"--name={app_name}",
        # GÜNCELLEME: assets klasörünü ve src klasörünü pakete ekliyoruz.
        f"--add-data=src{separator}src",
        f"--add-data=assets{separator}assets",
    ]
    
    # Eğer icon dosyası varsa komuta ekle
    if os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    else:
        print(f"UYARI: '{icon_path}' bulunamadı. Program ikonsuz olarak oluşturulacak.")

    # Gerekli kütüphaneleri gizli import olarak eklemek, "module not found" hatalarını önler
    hidden_imports = [
        "requests",
        "bs4",
        "lxml",
        "reportlab",
        "PyQt5.sip",
    ]
    for lib in hidden_imports:
        cmd.append(f"--hidden-import={lib}")

    # Ana script'i komutun sonuna ekle
    cmd.append(main_script)
    
    print("="*50)
    print("Çalıştırılabilir dosya oluşturuluyor...")
    print(f"Komut: {' '.join(cmd)}")
    print("="*50)
    
    try:
        # Komutu çalıştır
        subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("\n✅ Harika! Build işlemi başarıyla tamamlandı.")
        print(f"Oluşturulan dosya: dist\\{app_name}.exe")
        
    except FileNotFoundError:
        print("\n❌ HATA: PyInstaller bulunamadı. Lütfen 'pip install pyinstaller' komutu ile yükleyin.")
        return False
        
    except subprocess.CalledProcessError as e:
        print("\n❌ HATA: Build işlemi sırasında bir hata oluştu.")
        print("-" * 20 + " Hata Çıktısı " + "-" * 20)
        print(e.stdout)
        print(e.stderr)
        print("-" * 55)
        return False
    
    return True

if __name__ == "__main__":
    build_executable()