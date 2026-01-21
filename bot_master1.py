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
# ⚙️ الإعدادات الكبرى
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

def renew_tor_ip():
    try:
        with socket.create_connection(("127.0.0.1", TOR_CONTROL_PORT)) as sig:
            sig.send(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\n')
            time.sleep(5)
    except: pass

def get_geo_full_data():
    try:
        proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
        # جلب بيانات متكاملة: الموقع، المنطقة الزمنية، اللغة
        data = requests.get('http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,lat,lon,timezone,currency,isp,query', proxies=proxies, timeout=15).json()
        if data['status'] == 'success':
            return data
    except: return None
    return None

def apply_ultra_stealth(driver, device, geo):
    # تزييف العتاد
    cpu = random.choice([4, 6, 8, 12])
    ram = random.choice([8, 12, 16, 32])
    # تزييف البطارية بدقة
    batt = round(random.uniform(0.20, 0.95), 2)
    is_charging = "false" if batt < 0.80 else "true"
    
    # بيانات الموقع واللغة
    lang = geo['countryCode'].lower() if geo else "en"
    tz = geo['timezone'] if geo else "UTC"
    lat = geo['lat'] if geo else 0.0
    lon = geo['lon'] if geo else 0.0

    stealth_script = f"""
    // 1. تزييف الهاردوير
    Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {cpu}}});
    Object.defineProperty(navigator, 'deviceMemory', {{get: () => {ram}}});
    
    // 2. تزييف كرت الشاشة
    const getParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(p) {{
        if (p === 37445) return 'Google Inc. (NVIDIA)';
        if (p === 37446) return '{device["gpu"]}';
        return getParam.apply(this, arguments);
    }};

    // 3. تزييف البطارية 🔋
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: {is_charging}, level: {batt}, chargingTime: 0, dischargingTime: Infinity
        }});
    }}

    // 4. تزييف اللغة والمنطقة الزمنية 🌍
    Object.defineProperty(navigator, 'language', {{get: () => '{lang}-{lang.upper()}'}});
    Object.defineProperty(navigator, 'languages', {{get: () => ['{lang}-{lang.upper()}', '{lang}']}});
    
    // 5. تزييف الـ GPS 📍
    navigator.geolocation.getCurrentPosition = (success) => success({{
        coords: {{ latitude: {lat}, longitude: {lon}, accuracy: 10, altitude: null, altitudeAccuracy: null, heading: null, speed: null }},
        timestamp: Date.now()
    }});
    navigator.geolocation.watchPosition = (success) => success({{
        coords: {{ latitude: {lat}, longitude: {lon}, accuracy: 10 }},
        timestamp: Date.now()
    }});

    // 6. منع كشف الأتمتة
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": stealth_script})
    
    # ضبط الوقت الفعلي للمتصفح ليطابق المنطقة الزمنية للـ IP
    driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": tz})
    # ضبط إحداثيات الموقع الجغرافي في المتصفح
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
        "latitude": lat,
        "longitude": lon,
        "accuracy": 100
    })

def run_session(session_num):
    os.system("pkill -f chrome 2>/dev/null || true")
    renew_tor_ip()
    
    geo = get_geo_full_data()
    device = random.choice(DEVICES)
    video = random.choice(VIDEOS_POOL)
    
    # تحسين عرض البيانات 📊
    print(f"\n" + "="*50)
    print(f"🚀 الجلسة رقم: {session_num}")
    print(f"🎬 فيديو: https://youtu.be/{video['id']}")
    print(f"🌐 الـ IP الحالي: {geo['query'] if geo else 'Unknown'}")
    print(f"📍 الموقع: {geo['city']}, {geo['country']} | 🕒 توقيت: {geo['timezone']}")
    print(f"🗺️ GPS: {geo['lat']}, {geo['lon']}")
    print(f"💻 الجهاز: {device['name']} | 🔋 البطارية: {random.randint(20,95)}%")
    print(f"🌍 اللغة: {geo['countryCode'] if geo else 'EN'}")
    print("="*50)

    profile_dir = os.path.abspath(f"tor_profile_{session_num}_{random.randint(100,999)}")
    
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={device["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={device['w']},{device['h']}")
    options.add_argument('--headless') # يمكنك إزالتها إذا أردت رؤية المتصفح
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        apply_ultra_stealth(driver, device, geo)
        
        # التوجه لليوتيوب
        driver.get(f"https://www.youtube.com/watch?v={video['id']}")
        
        # محاكاة الانتظار والمشاهدة
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        
        # تفاعل بشري بسيط (التمرير)
        time.sleep(random.randint(5, 10))
        driver.execute_script(f"window.scrollBy(0, {random.randint(200, 500)});")
        
        watch_time = random.randint(150, 240) # مدة المشاهدة
        print(f"⏳ جاري المشاهدة لمدة {watch_time} ثانية...")
        time.sleep(watch_time)
        
        print(f"✅ انتهت الجلسة بنجاح.")
        
    except Exception as e:
        print(f"❌ خطأ في الجلسة: {str(e)[:50]}")
    finally:
        try:
            driver.quit()
        except: pass
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    print("🔥 بدأ نظام المشاهدات المتقدم - الحماية القصوى")
    for i in range(1, MAX_SESSIONS + 1):
        run_session(i)
        gap = random.randint(20, 60)
        print(f"💤 انتظار {gap} ثانية قبل الجلسة القادمة...")
        time.sleep(gap)
