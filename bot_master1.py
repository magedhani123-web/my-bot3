#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMPERIAL HYBRID VIEWER - FINAL EDITION (MODIFIED TIMEOUTS)
"""

import os
import time
import random
import shutil
import tempfile
import subprocess
import sys
import socket
import requests

# محاولة استيراد Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
except ImportError:
    print("📦 Installing selenium...")
    os.system("pip install selenium requests > /dev/null 2>&1")
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

print("="*60)
print("👑 IMPERIAL HYBRID VIEWER - FINAL EDITION")
print("="*60)

# ==========================================
# ⚙️ الإعدادات الإمبراطورية
# ==========================================
TOR_PROXY = "socks5://127.0.0.1:9050"
CONTROL_PORT = 9051

# قائمة الأجهزة
DEVICES = [
    {"name": "iPhone 16 Pro Max", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "plat": "iPhone", "w": 430, "h": 932, "mobile": True},
    {"name": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36", "plat": "Linux armv8l", "w": 384, "h": 854, "mobile": True},
    {"name": "Windows 11 PC", "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "plat": "Win32", "w": 1920, "h": 1080, "mobile": False},
    {"name": "MacBook Pro", "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "plat": "MacIntel", "w": 1440, "h": 900, "mobile": False}
]

VIDEOS_POOL = [
    {"id": "MrKhyV4Gcog", "keywords": "وش الحلم اللي حققته"},
    {"id": "bmgpC4lGSuQ", "keywords": "أجمل جزيرة في العالم سقطرى"},
    {"id": "6hYLIDz-RRM", "keywords": "هنا اختلفنا وفارقنا علي شان"},
    {"id": "AvH9Ig3A0Qo", "keywords": "Socotra treasure island"}
]

# ==========================================
# 🔍 فحص وتجهيز النظام
# ==========================================
def setup_chrome_path():
    print("🔍 Checking Chrome installation...")
    os.system("pkill -f chrome 2>/dev/null || true")
    os.system("pkill -f chromedriver 2>/dev/null || true")
    time.sleep(2) # زدنا المدة لضمان إغلاق العمليات القديمة

    chrome_path = "/usr/bin/google-chrome"
    possible_paths = ["/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chrome", "/usr/bin/google-chrome-stable"]
    
    found = False
    for path in possible_paths:
        if os.path.exists(path):
            chrome_path = path
            found = True
            print(f"✅ Found Chrome at: {chrome_path}")
            break
    
    if not found:
        print("❌ Chrome not found. Attempting install...")
        os.system("sudo apt-get update && sudo apt-get install -y google-chrome-stable")
        chrome_path = "/usr/bin/google-chrome"
    
    return chrome_path

# ==========================================
# 🌍 إدارة TOR NETWORK
# ==========================================
def rotate_ip():
    print("🔄 Rotating IP address...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10) # زدنا مهلة المهلة لـ Tor
            if s.connect_ex(("127.0.0.1", CONTROL_PORT)) == 0:
                s.send(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n')
                time.sleep(10) # زدنا مدة الانتظار لاستقرار الـ IP الجديد
                
                proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}
                try:
                    info = requests.get('http://ip-api.com/json/', proxies=proxies, timeout=15).json()
                    print(f"🌍 NEW IP: {info.get('query')} | 📍 {info.get('country')}")
                except:
                    print("⚠️ IP rotated but check timed out.")
            else:
                print("⚠️ Tor control port not open. Skipping rotation.")
    except Exception as e:
        print(f"⚠️ Tor rotation failed: {e}")

# ==========================================
# 📶 محاكاة سرعة الشبكة
# ==========================================
def set_network_speed(driver):
    profiles = [
        {"name": "5G", "down": 50000, "up": 20000, "lat": 20},
        {"name": "4G", "down": 15000, "up": 7000, "lat": 50},
        {"name": "WiFi", "down": 30000, "up": 15000, "lat": 30}
    ]
    profile = random.choice(profiles)
    try:
        driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
            "offline": False,
            "latency": profile["lat"],
            "downloadThroughput": profile["down"] * 1024,
            "uploadThroughput": profile["up"] * 1024
        })
        print(f"📶 Network Speed: {profile['name']}")
    except:
        pass

# ==========================================
# 🛠️ إنشاء المتصفح
# ==========================================
def create_browser(chrome_bin, device):
    try:
        profile_dir = tempfile.mkdtemp(prefix="imp_prof_")
        options = Options()
        options.binary_location = chrome_bin
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--headless=new')
        options.add_argument('--mute-audio')
        options.add_argument(f'--user-data-dir={profile_dir}')
        options.add_argument(f'--proxy-server={TOR_PROXY}')
        options.add_argument(f'--user-agent={device["ua"]}')
        
        if device['mobile']:
            mobile_emulation = {
                "deviceMetrics": {"width": device['w'], "height": device['h'], "pixelRatio": 3.0},
                "userAgent": device['ua']
            }
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        else:
            options.add_argument(f'--window-size={device["w"]},{device["h"]}')

        options.add_argument('--disable-extensions')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        print(f"  🛠️ Creating Chrome for {device['name']}...")
        driver = webdriver.Chrome(options=options)
        set_network_speed(driver)
        
        return driver, profile_dir
    except Exception as e:
        print(f"  ❌ Browser creation failed: {e}")
        return None, None

# ==========================================
# 📺 تشغيل الفيديو
# ==========================================
def play_video(driver, video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"  🌐 Loading: {url}")
        driver.get(url)
        
        # 🟢 التعديل الأهم: زدنا وقت تحميل الصفحة لـ 20 ثانية لضمان عدم وجود Null
        time.sleep(20) 
        
        js_code = """
        function imperialPlayer() {
            try {
                var v = document.querySelector('video');
                if(v) {
                    v.muted = true;
                    v.playbackRate = 2.0;
                    if(v.paused) v.play();
                    return true;
                }
                var skip = document.querySelector('.ytp-ad-skip-button, .ytp-skip-ad-button');
                if(skip) { skip.click(); }
                var banner = document.querySelector('.ytp-ad-overlay-close-button');
                if(banner) banner.click();
                return false;
            } catch(e) { return false; }
        }
        return imperialPlayer();
        """
        
        driver.execute_script(js_code)
        
        watch_time = random.randint(180, 400) # زدنا وقت المشاهدة قليلاً
        print(f"  ⏱️ Watching for {watch_time}s (Speed 2x)...")
        
        start = time.time()
        while time.time() - start < watch_time:
            driver.execute_script(js_code)
            if random.random() < 0.2:
                driver.execute_script(f"window.scrollBy(0, {random.randint(-50, 50)})")
            time.sleep(10) # زدنا دورة الفحص لـ 10 ثواني لتقليل الضغط
            
        print("  ✅ Session completed successfully")
        return True
    except Exception as e:
        print(f"  ❌ Playback error: {str(e)[:50]}")
        return False

# ==========================================
# 🚀 البرنامج الرئيسي
# ==========================================
def main():
    chrome_bin = setup_chrome_path()
    
    if os.system("pgrep -x tor > /dev/null") != 0:
        print("⚠️ Warning: Tor service not running. Starting it...")
        os.system("sudo service tor start")
        time.sleep(15) # زدنا وقت بدء تور لضمان الجاهزية

    session_count = 1
    while True:
        print(f"\n🎯 [Session {session_count}] Initiating...")
        rotate_ip()
        device = random.choice(DEVICES)
        video = random.choice(VIDEOS_POOL)
        driver, profile = create_browser(chrome_bin, device)
        
        if driver:
            play_video(driver, video['id'])
            try: driver.quit()
            except: pass
            shutil.rmtree(profile, ignore_errors=True)
            print("  🧹 Cleanup done")
        
        session_count += 1
        wait = random.randint(15, 30) # زدنا وقت الراحة بين الجلسات
        print(f"⏳ Cooldown: {wait}s...")
        time.sleep(wait)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Stopped by King.")
