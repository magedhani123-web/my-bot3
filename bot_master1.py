#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import random
import shutil
import tempfile
import socket
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# ==========================================
# ⚙️ الإعدادات الكبرى (تطابق كامل مع IP TOR + تزييف RAM/CPU)
# ==========================================
MAX_SESSIONS = 1000000 
TOR_PROXY = "socks5://127.0.0.1:9050"
TOR_CONTROL_PORT = 9051
MAX_WORKERS = 1 

DEVICES = [
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932, "gpu": "Apple GPU"},
    {"name": "iPhone 15 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 393, "h": 852, "gpu": "Apple GPU"},
    {"name": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854, "gpu": "Adreno 750"},
    {"name": "Samsung Galaxy S23 Ultra", "ua": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 360, "h": 800, "gpu": "Adreno 740"},
    {"name": "Google Pixel 9 Pro", "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro Build/AD1A.240530.019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915, "gpu": "Mali-G715"},
    {"name": "Huawei Mate 60 Pro", "ua": "Mozilla/5.0 (Linux; Android 12; ALN-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915, "gpu": "Mali-G710"},
    {"name": "Xiaomi 14 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; 24030PN60G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 393, "h": 873, "gpu": "Adreno 750"},
    {"name": "Windows 11 PC", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080, "gpu": "NVIDIA RTX 4090"},
    {"name": "MacBook Pro (macOS)", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900, "gpu": "Apple M3"}
]

VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

def renew_tor_ip():
    try:
        with socket.create_connection(("127.0.0.1", TOR_CONTROL_PORT)) as sig:
            sig.send(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\n')
            time.sleep(5)
    except: pass

def get_current_ip():
    try:
        proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
        r = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=15).json()
        return r['ip']
    except: return "Unknown"

def get_geo_data():
    try:
        proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
        return requests.get('http://ip-api.com/json/', proxies=proxies, timeout=15).json()
    except: return None

def apply_stealth_js(driver, device, geo, extra_data):
    # استخدام البيانات العشوائية التي تم إنشاؤها للجلسة
    cpu = extra_data['cpu']
    ram = extra_data['ram']
    batt = extra_data['batt']
    charging = extra_data['charging']
    
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
            charging: {charging}, level: {batt}, chargingTime: 0, dischargingTime: Infinity
        }});
    }}
    Object.defineProperty(navigator, 'language', {{get: () => '{lang}-{lang.upper()}'}});
    Object.defineProperty(navigator, 'languages', {{get: () => ['{lang}-{lang.upper()}', '{lang}']}});
    if (Intl) {{
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
            return {{ timeZone: '{tz}', calendar: 'gregory', numberingSystem: 'latn', locale: '{lang}-{lang.upper()}' }};
        }};
    }}
    navigator.geolocation.getCurrentPosition = (success) => success({{
        coords: {{ latitude: {lat}, longitude: {lon}, accuracy: 100 }}
    }});
    Object.defineProperty(navigator, 'platform', {{get: () => '{device["plat"]}'}});
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})

def run_session(session_num):
    os.system("pkill -f chrome 2>/dev/null || true")
    os.system("pkill -f chromedriver 2>/dev/null || true")
    
    renew_tor_ip()
    current_ip = get_current_ip()
    geo = get_geo_data()
    device = random.choice(DEVICES)
    video = random.choice(VIDEOS_POOL)
    
    # توليد بيانات العتاد والبطارية للجلسة الحالية للطباعة والحقن
    session_data = {
        "cpu": random.choice([2, 4, 6, 8, 12]),
        "ram": random.choice([4, 8, 12, 16, 32]),
        "batt": round(random.uniform(0.15, 0.98), 2),
        "charging": random.choice(["true", "false"])
    }
    
    # عرض البيانات المطلوبة في الكونسول كما طلبت
    print(f"\n🚀 جلسة #{session_num} | IP: {current_ip} ({geo['country'] if geo else 'Unknown'})")
    print(f"💻 جهاز: {device['name']} | لغة: {geo['countryCode'] if geo else '??'} | توقيت: {geo['timezone'] if geo else '??'}")
    print(f"🔋 بطارية: {int(session_data['batt']*100)}% | شحن: {session_data['charging']} | معالج: {session_data['cpu']} Cores | رام: {session_data['ram']}GB")
    print(f"📍 GPS: Lat {geo['lat'] if geo else 0} | Lon {geo['lon'] if geo else 0}")

    profile_dir = os.path.abspath(f"profile_session_{random.randint(1000, 9999)}")
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={device["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={device['w']},{device['h']}")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--mute-audio')

    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        apply_stealth_js(driver, device, geo, session_data)
        wait = WebDriverWait(driver, 30)

        driver.get("https://www.youtube.com")
        time.sleep(random.randint(5, 8))
        
        try:
            btns = driver.find_elements(By.XPATH, "//button[contains(.,'Accept') or contains(.,'Agree') or contains(.,'موافق')]")
            if btns: btns[0].click()
            search_box = wait.until(EC.element_to_be_clickable((By.NAME, "search_query")))
            for char in video['keywords']:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            search_box.send_keys(Keys.ENTER)
            target_video = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '{video['id']}')]")))
            target_video.click()
        except:
            driver.get(f"https://www.youtube.com/watch?v={video['id']}")

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        driver.execute_script("document.querySelector('video').playbackRate = 1.0; document.querySelector('video').play();")
        
        time.sleep(random.randint(120, 180))
        print(f"✅ اكتملت الجلسة بتطابق كامل للبيانات.")
        
    except Exception as e:
        print(f"❌ خطأ: {str(e)[:50]}")
    finally:
        if driver:
            driver.quit()
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    for i in range(1, MAX_SESSIONS + 1):
        run_session(i)
        wait_gap = random.randint(15, 45)
        print(f"⏳ انتظار {wait_gap} ثانية...")
        time.sleep(wait_gap)
