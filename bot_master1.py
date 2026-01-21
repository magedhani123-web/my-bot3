#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import shutil
import socket
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ==========================================
# ⚙️ الإعدادات الكبرى (تطابق كامل مع IP TOR + تزييف شامل)
# ==========================================
MAX_SESSIONS = 1000000 
TOR_PROXY = "socks5://127.0.0.1:9050"
TOR_CONTROL_PORT = 9051

DEVICES = [
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932, "gpu": "Apple GPU"},
    {"name": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854, "gpu": "Adreno 750"},
    {"name": "Google Pixel 9 Pro", "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro Build/AD1A.240530.019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915, "gpu": "Mali-G715"},
    {"name": "Windows 11 PC", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080, "gpu": "NVIDIA RTX 4090"}
]

VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

# ==========================================
# 🛠️ الوظائف الأساسية
# ==========================================

def renew_tor_ip():
    try:
        with socket.create_connection(("127.0.0.1", TOR_CONTROL_PORT)) as sig:
            sig.send(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\n')
            time.sleep(5)
    except: pass

def get_geo_full_data():
    try:
        proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
        # جلب بيانات تفصيلية (الموقع، الوقت، التاريخ، المنطقة الزمنية)
        r = requests.get('http://ip-api.com/json/?fields=status,country,countryCode,city,lat,lon,timezone,query', proxies=proxies, timeout=15).json()
        if r['status'] == 'success': return r
    except: return None

def create_driver(profile_dir, device):
    """ الوظيفة المحسنة لمنع أخطاء الاتصال """
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={device["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={device['w']},{device['h']}")
    
    options.add_argument('--no-sandbox') 
    options.add_argument('--disable-dev-shm-usage') 
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222') 
    options.add_argument('--headless')
    options.add_argument('--mute-audio')

    driver = uc.Chrome(options=options, use_subprocess=True)
    return driver

def apply_stealth_logic(driver, device, geo):
    # تزييف العتاد والبطارية
    cpu = random.choice([4, 8, 12])
    ram = random.choice([8, 16, 32])
    batt = round(random.uniform(0.15, 0.98), 2)
    is_charging = random.choice(["true", "false"])
    
    # بيانات الموقع واللغة من الـ IP
    lang = geo['countryCode'].lower() if geo else "en"
    tz = geo['timezone'] if geo else "UTC"
    lat = geo['lat'] if geo else 0.0
    lon = geo['lon'] if geo else 0.0

    js_code = f"""
    Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cpu}}});
    Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram}}});
    const getParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(p) {{
        if (p === 37445) return 'Google Inc. (NVIDIA)';
        if (p === 37446) return '{device["gpu"]}';
        return getParam.apply(this, arguments);
    }};
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: {is_charging}, level: {batt}, chargingTime: 0, dischargingTime: Infinity
        }});
    }}
    Object.defineProperty(navigator, 'language', {{get: () => '{lang}-{lang.upper()}'}});
    Object.defineProperty(navigator, 'languages', {{get: () => ['{lang}-{lang.upper()}', '{lang}']}});
    
    // تزييف الـ GPS 📍
    navigator.geolocation.getCurrentPosition = (success) => success({{
        coords: {{ latitude: {lat}, longitude: {lon}, accuracy: 100 }}
    }});
    
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})
    
    # ضبط الوقت والمنطقة الزمنية والـ GPS في المتصفح
    driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": tz})
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": lat, "longitude": lon, "accuracy": 100
    })

def run_session(session_num):
    # تنظيف العمليات السابقة
    os.system("pkill -f chrome 2>/dev/null || true")
    
    renew_tor_ip()
    geo = get_geo_full_data()
    device = random.choice(DEVICES)
    video = random.choice(VIDEOS_POOL)
    profile_dir = os.path.abspath(f"tor_profile_{session_num}_{random.randint(1000, 9999)}")

    # عرض البيانات المطلوبة 🚀
    print(f"\n🚀 الجلسة #{session_num} بدأت")
    print(f"🎬 الفـيديو: https://www.youtube.com/watch?v={video['id']}")
    print(f"🌐 IP TOR: {geo['query'] if geo else 'Unknown'}")
    print(f"📍 المـوقع: {geo['city']}, {geo['country']} | GPS: {geo['lat']}, {geo['lon']}")
    print(f"🕒 التوقيت: {geo['timezone']} | 🌍 اللغة: {geo['countryCode'] if geo else '??'}")
    print(f"💻 الجهاز: {device['name']} | 🔋 البطارية: {random.randint(20, 98)}%")
    print("-" * 50)

    try:
        driver = create_driver(profile_dir, device)
        apply_stealth_logic(driver, device, geo)
        wait = WebDriverWait(driver, 30)

        # الدخول لليوتيوب والبحث
        driver.get("https://www.youtube.com")
        time.sleep(random.randint(5, 8))
        
        try:
            # تخطي الموافقة على الخصوصية
            btns = driver.find_elements(By.XPATH, "//button[contains(.,'Accept') or contains(.,'Agree') or contains(.,'موافق')]")
            if btns: btns[0].click()
            
            # عملية البحث بالكلمات المفتاحية
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "search_query")))
            for char in video['keywords']:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            search_box.send_keys(Keys.ENTER)
            
            target_video = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{video['id']}')]")))
            target_video.click()
        except:
            # إذا فشل البحث، توجه للفيديو مباشرة
            driver.get(f"https://www.youtube.com/watch?v={video['id']}")

        # المشاهدة والتفاعل
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        driver.execute_script("document.querySelector('video').play();")
        
        time.sleep(random.randint(10, 20))
        driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)});")
        
        watch_duration = random.randint(120, 180)
        print(f"⏳ جاري المشاهدة لمدة {watch_duration} ثانية...")
        time.sleep(watch_duration)
        
        print(f"✅ اكتملت الجلسة بنجاح.")
        
    except Exception as e:
        print(f"❌ خطأ: {str(e)[:50]}")
    finally:
        try:
            driver.quit()
        except: pass
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    print("🔥 بدأ نظام المشاهدات الاحترافي (TOR + GPS Stealth)")
    for i in range(1, MAX_SESSIONS + 1):
        run_session(i)
        wait_gap = random.randint(15, 45)
        print(f"💤 انتظار {wait_gap} ثانية...")
        time.sleep(wait_gap)
