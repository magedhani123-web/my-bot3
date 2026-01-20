import time
import random
import os
import shutil
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# --- [ الإعدادات الأساسية ] ---
TOR_PROXY = "socks5://127.0.0.1:9050"

VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

DEVICES = [
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932},
    {"name": "iPhone 15 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 393, "h": 852},
    {"name": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854},
    {"name": "Samsung Galaxy S23 Ultra", "ua": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 360, "h": 800},
    {"name": "Google Pixel 9 Pro", "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro Build/AD1A.240530.019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915},
    {"name": "Huawei Mate 60 Pro", "ua": "Mozilla/5.0 (Linux; Android 12; ALN-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915},
    {"name": "Xiaomi 14 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; 24030PN60G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 393, "h": 873},
    {"name": "Windows 11 PC", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080},
    {"name": "MacBook Pro (macOS)", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900}
]

LOCATIONS = [
    {"city": "Riyadh", "lat": 24.7136, "lon": 46.6753, "tz": "Asia/Riyadh", "lang": "ar-SA"},
    {"city": "Dubai", "lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai", "lang": "ar-AE"},
    {"city": "New York", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "lang": "en-US"}
]

def inject_stealth(driver, dev, loc):
    # تحديث البطارية حسب طلبك
    battery_list = [1.0, 0.45, 0.78, 0.34, 0.62, 0.80, 0.25]
    selected_battery = random.choice(battery_list)
    js_code = f"""
    Object.defineProperty(navigator, 'languages', {{get: () => ['{loc['lang']}', 'en-US']}});
    Object.defineProperty(navigator, 'platform', {{get: () => '{dev["plat"]}'}});
    Object.defineProperty(Intl.DateTimeFormat().resolvedOptions(), 'timeZone', {{value: '{loc['tz']}'}});
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: true,
            level: {selected_battery},
            chargingTime: 0,
            dischargingTime: Infinity
        }});
    }}
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})

def run_session(session_num):
    dev = random.choice(DEVICES)
    loc = random.choice(LOCATIONS)
    video_data = random.choice(VIDEOS_POOL)
    
    print(f"\n🚀 [الجلسة {session_num}] | الجهاز: {dev['name']} | المدينة: {loc['city']}")
    
    options = uc.ChromeOptions()
    # استخدام اسم بروفايل مختلف في كل مرة لتجنب القفل
    profile_dir = os.path.abspath(f"profile_{session_num % 10}")
    
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={dev["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={dev['w']},{dev['h']}")
    
    # تحسينات هامة جداً لمنع التوقف في Linux
    options.add_argument('--headless=new') # النسخة الجديدة من الهيدلس
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--mute-audio') # كتم الصوت من النظام لضمان استقرار السيرفر

    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.set_page_load_timeout(60) # تحديد وقت أقصى للتحميل لمنع التجمد
        inject_stealth(driver, dev, loc)
        wait = WebDriverWait(driver, 20)

        print("🔗 فتح يوتيوب...")
        driver.get("https://www.youtube.com")
        
        # التعامل مع صفحة الموافقة (Reject All)
        try:
            reject_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Reject')] | //button[contains(.,'Reject')]")))
            reject_btn.click()
            print("🛡️ تم تجاوز صفحة ملفات التعريف")
        except: pass

        # تشغيل الفيديو
        driver.get(f"https://www.youtube.com/watch?v={video_data['id']}")
        print(f"📺 بدأ مشاهدة الفيديو الأساسي...")
        
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        video = driver.find_element(By.TAG_NAME, "video")
        
        # تشغيل الصوت ورفع السرعة عشوائياً
        driver.execute_script("arguments[0].muted = false; arguments[0].volume = 0.5;", video)
        
        watch_time = random.randint(70, 110)
        time.sleep(watch_time)

        # --- ميزة فيديو مقترح آخر 20 ثانية ---
        try:
            print("🔗 محاولة الانتقال لفيديو مقترح...")
            # البحث عن أول فيديو مقترح
            recommended = driver.find_element(By.CSS_SELECTOR, "ytd-compact-video-renderer a")
            recommended.click()
            time.sleep(5)
            # القفز لآخر 25 ثانية لمشاهدة 20 منها
            driver.execute_script("var v = document.querySelector('video'); v.currentTime = v.duration - 25;")
            time.sleep(20)
            print("✅ اكتملت مشاهدة الفيديو المقترح.")
        except: print("⚠️ لم يتوفر فيديو مقترح حالياً")

    except Exception as e:
        print(f"⚠️ حدث خطأ أو توقف: {str(e)[:50]}")
    finally:
        if driver:
            driver.quit()
        # تنظيف الملفات المؤقتة فوراً
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    # تنظيف العمليات السابقة لضمان عدم التجمد
    os.system("pkill -f chrome")
    os.system("pkill -f chromedriver")
    
    for i in range(1, 1000001):
        run_session(i)
        delay = random.randint(5, 10)
        print(f"💤 انتظار {delay} ثانية للجلسة القادمة...")
        time.sleep(delay)
