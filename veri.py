import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException
import chromedriver_autoinstaller
import urllib.request
from selenium.webdriver.chrome.options import Options

# ChromeDriver'ı otomatik olarak yükle
chromedriver_autoinstaller.install()

# User-Agent ve Proxy seçeneklerini ayarla
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.88 Safari/537.36")
# Proxy kullanımı (isteğe bağlı)
# options.add_argument("--proxy-server=http://<proxy_ip>:<proxy_port>")

# Veri çekmek istediğiniz kategoriler ve URL'ler
categories = {
    "Kargo": "https://www.trendyol.com/kargo-erkek-pantolon-x-g2-c70-a179-v194570?pi=2"
}

# Çıktı klasörü
output_folder = "product_images"  # Masaüstünde kaydet
os.makedirs(output_folder, exist_ok=True)

# Her kategori için işlem
for category_name, url in categories.items():
    category_folder = os.path.join(output_folder, category_name)
    os.makedirs(category_folder, exist_ok=True)

    try:
        driver = webdriver.Chrome(options=options)  # Tarayıcıyı başlat
        driver.get(url)
        time.sleep(5)  # Sayfanın yüklenmesini bekle
    except WebDriverException as e:
        print(f"Tarayıcı başlatılırken bir hata oluştu: {e}")
        continue

    print(f"'{category_name}' kategorisi için veri çekiliyor...")
    products_collected = set()
    scroll_attempts = 0  # Kaydırma denemeleri
    max_scroll_attempts = 10  # En fazla deneme sayısı
    scroll_pause_time = 5  # Kaydırma sonrası bekleme süresi

    while len(products_collected) < 800:  # Daha az görsel çekmek için limit
        try:
            # Görselleri her döngüde yeniden topla
            products = driver.find_elements(By.XPATH, '//img[contains(@class, "p-card-img")]')

            # Yeni ürünleri kaydet
            for product in products:
                try:
                    img_url = product.get_attribute("src")
                    if img_url and img_url not in products_collected:  # Yeni bir görselse
                        products_collected.add(img_url)
                        img_path = os.path.join(category_folder, f"{category_name}_{len(products_collected)}.jpg")
                        urllib.request.urlretrieve(img_url, img_path)  # Görseli indir
                        print(f"Görsel kaydedildi: {img_path}")

                        if len(products_collected) >= 800:  # Görsel limitine ulaşıldığında çık
                            break
                except Exception as e:
                    print(f"Görsel indirilemedi: {e}")

            # Görsel limitine ulaşıldıysa çık
            if len(products_collected) >= 800:
                break

            # Sayfanın biraz daha aşağısına kaydır
            driver.execute_script("window.scrollBy(0, 1000);")  # 1000 piksel aşağı kaydır
            time.sleep(scroll_pause_time)  # Kaydırma sonrası bekleme

            # Yeni içerik yüklenmesini kontrol et
            new_products = driver.find_elements(By.XPATH, '//img[contains(@class, "p-card-img")]')
            if len(new_products) == len(products):  # Yeni görsel yüklenmediyse
                scroll_attempts += 1
                if scroll_attempts >= max_scroll_attempts:  # Maksimum kaydırma denemesi yapıldıysa
                    print(f"'{category_name}' kategorisinde daha fazla görsel bulunamadı.")
                    break
            else:
                scroll_attempts = 0  # Yeni içerik yüklendiyse sıfırla

        except TimeoutException:
            print("Sayfa yüklenirken zaman aşımı oluştu. Yeniden deneniyor...")
            driver.refresh()
            time.sleep(5)
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            break

    driver.quit()  # Tarayıcıyı kapat
    print(f"'{category_name}' kategorisinden {len(products_collected)} görsel indirildi.")

print("Tüm görseller başarıyla indirildi!")
