from playwright.sync_api import sync_playwright
import requests
import os
import time
import urllib.parse

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PROXY_URL = os.environ.get("PROXY_URL")

TAGS = ["tiktokmademebuyit", "amazonfinds", "dropshippingfinds", "viralproducts"]
MIN_VIEWS = 0 # Test üçün
SEEN_FILE = "seen_videos.txt"

def parse_views(view_str):
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
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        for v in seen:
            f.write(f"{v}\n")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Mesaj Telegrama göndərildi!")
    else:
        print(f"❌ Telegram xətası: {response.text}")

def scrape_tiktok():
    seen_videos = load_seen()
    all_results = []
    
    with sync_playwright() as p:
        browser_args = {"headless": True}
        
        # Proksini tam təmizləyib Playwright-ın istədiyi formata salırıq
        if PROXY_URL:
            # Dırnaqları, boşluqları və sonluqdakı / işarəsini silirik
            clean_url = PROXY_URL.strip().strip('"').strip("'").rstrip("/")
            
            if not clean_url.startswith("http"):
                clean_url = "http://" + clean_url
                
            parsed = urllib.parse.urlparse(clean_url)
            
            # Server ünvanını yaradırıq (istifadəçi adı və şifrəsiz)
            server_address = f"{parsed.scheme}://{parsed.hostname}"
            if parsed.port:
                server_address += f":{parsed.port}"
                
            browser_args["proxy"] = {"server": server_address}
            
            # Əgər istifadəçi adı və şifrə varsa, ayrıca əlavə edirik
            if parsed.username and parsed.password:
                browser_args["proxy"]["username"] = urllib.parse.unquote(parsed.username)
                browser_args["proxy"]["password"] = urllib.parse.unquote(parsed.password)
                
            print(f"🌐 Proksi ilə qoşulur: {server_address}")
            
        browser = p.chromium.launch(**browser_args)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()

        for tag in TAGS:
            try:
                print(f"🔍 #{tag} səhifəsi taranır...")
                page.goto(f"https://www.tiktok.com/tag/{tag}", timeout=60000)
                page.wait_for_selector('[data-e2e="challenge-item"]', timeout=20000)
                videos = page.locator('[data-e2e="challenge-item"]').all()
                
                for video in videos[:5]:
                    link = video.locator('a').first.get_attribute('href')
                    if not link: continue
                    
                    video_id = link.split('/')[-1]
                    if video_id in seen_videos:
                        continue
                        
                    views_text = video.locator('[data-e2e="video-views"]').inner_text()
                    views_num = parse_views(views_text)
                    
                    if views_num < MIN_VIEWS:
                        continue
                    
                    try:
                        desc = video.locator('img').first.get_attribute('alt')[:100] + "..."
                    except:
                        desc = "Açıqlama tapılmadı"

                    seen_videos.add(video_id)
                    snaptik_url = f"https://snaptik.app/?url={link}"
                    
                    msg = (
                        f"🏷 <b>#{tag}</b>\n"
                        f"👁 <b>Baxış:</b> {views_text}\n"
                        f"📝 <b>Mətn:</b> {desc}\n"
                        f"🔗 <b>TikTok:</b> {link}\n"
                        f"📥 <b>Loqosuz Yüklə/Bax:</b> <a href='{snaptik_url}'>SnapTik</a>"
                    )
                    all_results.append(msg)
                
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ #{tag} xətası: {e}")
                continue

        browser.close()

        if all_results:
            save_seen(seen_videos)
            message_body = "🔥 <b>Yeni Orqanik Dropshipping Məhsulları</b> 🔥\n\n" + "\n\n".join(all_results)
            send_telegram_message(message_body)
        else:
            print("Yeni və ya kriteriyalara uyğun video tapılmadı.")

if __name__ == "__main__":
    scrape_tiktok()
