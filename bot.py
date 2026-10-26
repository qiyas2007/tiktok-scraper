from playwright.sync_api import sync_playwright
import requests
import os
import time

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Yeni Funksiya 1: Çoxlu həştəq axtarışı
TAGS = ["tiktokmademebuyit", "amazonfinds", "dropshippingfinds", "viralproducts"]

# Yeni Funksiya 2: Baxış limiti (50.000-dən az olanları göndərməyəcək)
MIN_VIEWS = 0 
SEEN_FILE = "seen_videos.txt"

def parse_views(view_str):
    """Baxış sayını (məs. 1.5M, 50K) rəqəmə çevirir"""
    view_str = view_str.upper().strip()
    if not view_str: return 0
    multiplier = 1
    if 'K' in view_str:
        multiplier = 1000
        view_str = view_str.replace('K', '')
    elif 'M' in view_str:
        multiplier = 1000000
        view_str = view_str.replace('M', '')
    try:
        return int(float(view_str) * multiplier)
    except:
        return 0

def load_seen():
    """Yeni Funksiya 3: Əvvəl göndərilən videoların yaddaşını oxuyur"""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def save_seen(seen):
    """Göndərilmiş videoları yaddaşda saxlayır ki, təkrar göndərməsin"""
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for v in seen:
            f.write(f"{v}\n")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    requests.post(url, json=payload)

def scrape_tiktok():
    seen_videos = load_seen()
    all_results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        for tag in TAGS:
            try:
                page.goto(f"https://www.tiktok.com/tag/{tag}", timeout=60000)
                page.wait_for_selector('[data-e2e="challenge-item"]', timeout=15000)
                videos = page.locator('[data-e2e="challenge-item"]').all()
                
                # Hər həştəq üçün ilk 5 videonu analiz edir
                for video in videos[:5]:
                    link = video.locator('a').first.get_attribute('href')
                    if not link: continue
                    
                    video_id = link.split('/')[-1]
                    
                    # Təkrar yoxlanışı
                    if video_id in seen_videos:
                        continue
                        
                    views_text = video.locator('[data-e2e="video-views"]').inner_text()
                    views_num = parse_views(views_text)
                    
                    # Baxış limiti yoxlanışı
                    if views_num < MIN_VIEWS:
                        continue
                    
                    # Şəkil alt yazısından açıqlamanı çəkməyə cəhd edir
                    try:
                        desc = video.locator('img').first.get_attribute('alt')[:100] + "..."
                    except:
                        desc = "Açıqlama tapılmadı"

                    seen_videos.add(video_id)
                    snaptik_url = f"https://snaptik.app/?url={link}" # Loqosuz yükləmə linki
                    
                    msg = (
                        f"🏷 <b>#{tag}</b>\n"
                        f"👁 <b>Baxış:</b> {views_text}\n"
                        f"📝 <b>Mətn:</b> {desc}\n"
                        f"🔗 <b>TikTok:</b> {link}\n"
                        f"📥 <b>Loqosuz Yüklə/Bax:</b> <a href='{snaptik_url}'>SnapTik</a>"
                    )
                    all_results.append(msg)
                
                time.sleep(2)
            except Exception as e:
                continue

        browser.close()

        if all_results:
            save_seen(seen_videos)
            # Əgər nəticə çoxdursa, hissələrə bölüb göndərir
            message_body = "🔥 <b>Yeni Orqanik Dropshipping Məhsulları</b> 🔥\n\n" + "\n\n".join(all_results)
            send_telegram_message(message_body)
        else:
            print("Yeni və ya kriteriyalara uyğun video tapılmadı.")

if __name__ == "__main__":
    scrape_tiktok()
