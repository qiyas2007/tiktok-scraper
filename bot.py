from playwright.sync_api import sync_playwright
import requests
import os

# Məlumatlar GitHub Secrets-dən gəlir
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(text):
    """Telegrama mesaj göndərən funksiya"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Mesaj Telegrama göndərildi!")
    else:
        print(f"❌ Xəta: {response.text}")

def scrape_tiktok():
    with sync_playwright() as p:
        print("🌐 Brauzer proksisiz başladılır...")
        # Headless=True arxa planda işləməsini təmin edir, proksi çıxarılıb
        browser = p.chromium.launch(headless=True)
        
        # Sizi bot kimi görməməsi üçün saxta bir cihaz mühiti yaradırıq
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("🔍 TikTok #tiktokmademebuyit səhifəsinə daxil olunur...")
            # TikTok-un həştəq səhifəsinə gedirik
            page.goto("https://www.tiktok.com/tag/tiktokmademebuyit", timeout=60000)
            
            # Videoların yüklənməsini gözləyirik
            page.wait_for_selector('[data-e2e="challenge-item"]', timeout=15000)
            
            # Səhifədəki bütün videoları tapırıq
            videos = page.locator('[data-e2e="challenge-item"]').all()
            
            results = []
            
            # İlk 5 videonu analiz edirik
            for video in videos[:5]:
                link = video.locator('a').first.get_attribute('href')
                views = video.locator('[data-e2e="video-views"]').inner_text()
                
                results.append(f"🔗 <b>Link:</b> {link}\n👁 <b>Baxış:</b> {views}")
            
            # Nəticələri birləşdirib Telegram-a göndəririk
            if results:
                final_message = "🔥 <b>ABŞ Trend Dropshipping Məhsulları</b> 🔥\n\n" + "\n\n".join(results)
                send_telegram_message(final_message)
            else:
                print("⚠️ Heç bir video tapılmadı.")

        except Exception as e:
            print(f"Xəta baş verdi (Ola bilsin TikTok captcha çıxartdı): {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_tiktok()
