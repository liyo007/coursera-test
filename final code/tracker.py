# tracker.py

import time
import psutil
from collections import defaultdict
from plyer import notification
from constants import NOTIFICATION_THRESHOLD, NOTIFICATION_COOLDOWN, IGNORED_APPS, APP_DISPLAY_NAMES, BLUE_LIGHT_THRESHOLD,EVENING_HOUR_END,EVENING_HOUR_START
from utils import get_display_name
from datetime import datetime

last_notification = {}

def send_notification(app_name, usage_time):
    """Send smart notifications with context-aware messages."""
    current_time = time.time()
    if app_name not in last_notification or \
       (current_time - last_notification.get(app_name, 0)) > NOTIFICATION_COOLDOWN:
        
        message = (f"You've been using {app_name} for {usage_time:.1f} sec.\n"
                  f"Time for a quick break! 🎯")
        
        notification.notify(
            title="⏰ Smart Screen Time Alert",
            message=message,
            timeout=10
        )
        last_notification[app_name] = current_time

def send_blue_light_notification():
    """Send a notification to enable blue light filter."""
    notification.notify(
        title="🕶️ Blue Light Filter Suggestion",
        message="It's evening time! Enable your blue light filter to reduce eye strain and improve sleep quality.",
        timeout=10
    )

def track_screen_time(duration=60):
    """Track screen time usage with enhanced display names."""
    screen_time = defaultdict(int)
    start_time = time.time()
    
    while time.time() - start_time < duration:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name']
                if name in APP_DISPLAY_NAMES and name not in IGNORED_APPS:
                    screen_time[name] += 1
                    
                    if screen_time[name]  >= NOTIFICATION_THRESHOLD * 60:
                        send_notification(get_display_name(name), screen_time[name])
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Check for blue light filter suggestion
        current_hour = datetime.now().hour
        if EVENING_HOUR_START <= current_hour < EVENING_HOUR_END:
            send_blue_light_notification()
        
        time.sleep(1)

    return screen_time