#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👑 ULTIMATE IMPERIAL VIEWER - ALL-IN-ONE EDITION
المطور: تحسين شامل لضمان احتساب المشاهدات 100%
"""

import os
import time
import random
import shutil
import tempfile
import sys
import socket
import json
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ==========================================
# ⚙️ الإعدادات الأساسية
# ==========================================
TOR_PROXY = "socks5://127.0.0.1:9050"

DEVICES = [
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932, "mobile": True},
    {"name": "iPhone 15 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 393, "h": 852, "mobile": True},
    {"name": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854, "mobile": True},
    {"name": "Samsung Galaxy S23 Ultra", "ua": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 360, "h": 800, "mobile": True},
    {"name": "Google Pixel 9 Pro", "ua": "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro Build/AD1A.240530.019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.103 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915, "mobile": True},
    {"name": "Huawei Mate 60 Pro", "ua": "Mozilla/5.0 (Linux; Android 12; ALN-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36", "plat": "Linux aarch64", "w": 412, "h": 915, "mobile": True},
    {"name": "Xiaomi 14 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; 24030PN60G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 393, "h": 873, "mobile": True},
    {"name": "Windows 11 PC", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080, "mobile": False},
    {"name": "MacBook Pro (macOS)", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900, "mobile": False}
]

VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

LOCATIONS = [
    {"city": "Riyadh", "lat": 24.7136, "lon": 46.6753, "tz": "Asia/Riyadh", "lang": "ar-SA"},
    {"city": "Dubai", "lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai", "lang": "ar-AE"},
    {"city": "New York", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "lang": "en-US"}
]

# ==========================================
# 🛠️ أدوات النظام والشبكة
# ==========================================
def get_current_ip():
    try:
        proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
        response = requests.get('https://api.ipify.org', proxies=proxies, timeout=10)
        return response.text
    except:
        return "Direct (Tor Failed)"

def inject_advanced_stealth(driver, dev, loc):
    # ميزة البطارية المطلوبة
    batt = random.choice([1.0, 0.45, 0.78, 0.34, 0.62, 0.80, 0.25])
    # محاكاة سرعة الإنترنت (بين 2MB و 50MB)
    net_speed = random.choice([2, 5, 10, 25, 50])
    
    js_code = f"""
    // البطارية
    if (navigator.getBattery) {{
        navigator.getBattery = () => Promise.resolve({{
            charging: true, level: {batt}, chargingTime: 0, dischargingTime: Infinity
        }});
    }}
    // الموقع واللغة
    Object.defineProperty(navigator, 'languages', {{get: () => ['{loc['lang']}', 'en-US']}});
    Object.defineProperty(navigator, 'platform', {{get: () => '{dev["plat"]}'}});
    // سرعة الإنترنت
    Object.defineProperty(navigator, 'connection', {{get: () => ({{effectiveType: '{random.choice(['4g', '3g'])}', downlink: {net_speed}, rtt: 50}})}});
    // حماية ضد كشف الأتمتة
    Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})

# ==========================================
# 🚀 إنشاء المتصفح (متصفح واحد في كل مرة)
# ==========================================
def create_imperial_browser(dev, loc):
    profile_dir = tempfile.mkdtemp(prefix="imperial_")
    options = uc.ChromeOptions()
    
    options.add_argument(f'--user-data-dir={profile_dir}')
    options.add_argument(f'--user-agent={dev["ua"]}')
    options.add_argument(f'--proxy-server={TOR_PROXY}')
    options.add_argument(f"--window-size={dev['w']},{dev['h']}")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.set_page_load_timeout(60)
        inject_advanced_stealth(driver, dev, loc)
        return driver, profile_dir
    except Exception as e:
        print(f"❌ خطأ في إنشاء المتصفح: {e}")
        return None, profile_dir

# ==========================================
# 📺 نظام المشاهدة الذكي
# ==========================================
def watch_video_flow(driver, video_data, session_num):
    try:
        wait = WebDriverWait(driver, 30)
        
        # 1. فتح يوتيوب وتخطي الموافقة
        driver.get("https://www.youtube.com")
        time.sleep(4)
        try:
            btns = driver.find_elements(By.TAG_NAME, "button")
            for b in btns:
                if "Accept" in b.text or "Reject" in b.text: b.click(); break
        except: pass

        # 2. الانتقال للفيديو المباشر
        print(f"🎬 تشغيل: {video_data['keywords']}")
        driver.get(f"https://www.youtube.com/watch?v={video_data['id']}")
        
        # 3. تفعيل الصوت والسرعة (2x لتسريع العملية)
        video_el = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        driver.execute_script("""
            var v = document.querySelector('video');
            v.muted = false; 
            v.volume = 0.5;
            v.playbackRate = 2.0;
            v.play();
        """)
        print("🔊 الصوت مفعل | ⚡ السرعة: 2x")

        # 4. مدة المشاهدة الأساسية
        watch_time = random.randint(90, 150)
        print(f"⏳ مشاهدة لمدة {watch_time} ثانية...")
        time.sleep(watch_time)

        # 5. ميزة الفيديو المقترح (آخر 20 ثانية)
        try:
            print("🔗 الانتقال لفيديو مقترح لتعزيز الأمان...")
            recs = driver.find_elements(By.CSS_SELECTOR, "a.ytd-thumbnail")
            if recs:
                recs[0].click()
                time.sleep(5)
                # القفز لآخر 20 ثانية
                driver.execute_script("var v = document.querySelector('video'); v.currentTime = v.duration - 22;")
                time.sleep(20)
        except: pass

        # 6. كتم الصوت قبل الإغلاق
        driver.execute_script("document.querySelector('video').muted = true;")
        return True
    except Exception as e:
        print(f"⚠️ خطأ أثناء المشاهدة: {str(e)[:50]}")
        return False

# ==========================================
# 🏁 التشغيل الرئيسي
# ==========================================
def main():
    os.system("clear")
    print("="*60)
    print("👑 IMPERIAL HYBRID VIEWER - ULTIMATE EDITION")
    print("="*60)
    
    session = 1
    while True:
        # التأكد من عدم وجود متصفحات قديمة عالقة
        os.system("pkill -f chrome 2>/dev/null || true")
        
        current_ip = get_current_ip()
        dev = random.choice(DEVICES)
        loc = random.choice(LOCATIONS)
        vid = random.choice(VIDEOS_POOL)

        print(f"\n🚀 [الجلسة {session}]")
        print(f"🌐 IP الحالي: {current_ip}")
        print(f"📱 الجهاز: {dev['name']} | 🔋 البطارية عشوائية")
        print(f"📍 الموقع: {loc['city']}")

        driver, p_dir = create_imperial_browser(dev, loc)
        
        if driver:
            success = watch_video_flow(driver, vid, session)
            driver.quit()
            if success: print(f"✅ انتهت الجلسة {session} بنجاح")
            else: print(f"❌ فشلت الجلسة {session}")
        
        # تنظيف الملفات المؤقتة
        if os.path.exists(p_dir): shutil.rmtree(p_dir, ignore_errors=True)
        
        # استراحة قصيرة جداً لضمان التسريع
        wait_gap = random.randint(5, 10)
        print(f"😴 انتظار {wait_gap} ثانية قبل الجلسة التالية...")
        time.sleep(wait_gap)
        session += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف السكربت بواسطة المستخدم.")
        sys.exit()
