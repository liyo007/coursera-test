import psutil
import time
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from plyer import notification
from collections import defaultdict
from datetime import datetime, timedelta
import subprocess  # For app blocking
import threading  # For running blocking in the background

# Import energy.py functionality
from energy import render_energy_wheel

# Import calendar functionality from cal.py
from cal import get_calendar_service, create_calendar_heatmap, fetch_events, group_events_by_date

# Constants
NOTIFICATION_THRESHOLD = 30  # seconds
NOTIFICATION_COOLDOWN = 10  # seconds
IGNORED_APPS = ['svchost.exe', 'System Idle Process', 'explorer.exe', 'Registry', 
                'csrss.exe', 'wininit.exe', 'Conhost.exe', 'RuntimeBroker.exe']

# Application display names with emojis
APP_DISPLAY_NAMES = {
    'chrome.exe': '🌐 Google Chrome',
    'firefox.exe': '🦊 Firefox',
    'msedge.exe': '🌐 Microsoft Edge',
    'spotify.exe': '🎵 Spotify',
    'Code.exe': '💻 Visual Studio Code',
    'postgres.exe': '🐘 Postgres',
    'discord.exe': '💬 Discord',
    'slack.exe': '💼 Slack',
    'teams.exe': '👥 Microsoft Teams',
    'code.exe': '💻 VS Code',
    'notepad.exe': '📝 Notepad',
    'excel.exe': '📊 Excel',
    'word.exe': '📄 Word',
    'powerpoint.exe': '📺 PowerPoint',
    'outlook.exe': '📧 Outlook',
    'steam.exe': '🎮 Steam',
    'vlc.exe': '🎥 VLC Media Player',
    'photoshop.exe': '🎨 Photoshop',
    'illustrator.exe': '✒️ Illustrator',
    'zoom.exe': '🎥 Zoom',
    'skype.exe': '💬 Skype',
    'obs64.exe': '🎥 OBS Studio',
    'winrar.exe': '📦 WinRAR',
    '7zg.exe': '📦 7-Zip',
    'telegram.exe': '✈️ Telegram',
    'whatsapp.exe': '💬 WhatsApp',
    'netflix.exe': '🎬 Netflix',
    'conhost.exe':'✨ miscellanies ',
    'GitHubDesktop.exe' : '🐈‍⬛ Github',
    'stremio.exe' : '🍿Stremio'
}

# Enhanced application categories with more detailed classification
APP_CATEGORIES = {
    'Productivity': {
        'apps': ['excel.exe', 'word.exe', 'powerpoint.exe', 'code.exe', 'notepad.exe'],
        'emoji': '💼',
        'color': '#2ecc71'
    },
    'Communication': {
        'apps': ['teams.exe', 'slack.exe', 'outlook.exe', 'discord.exe', 'skype.exe', 'telegram.exe', 'whatsapp.exe'],
        'emoji': '💬',
        'color': '#3498db'
    },
    'Browsers': {
        'apps': ['chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 'safari.exe'],
        'emoji': '🌐',
        'color': '#9b59b6'
    },
    'Entertainment': {
        'apps': ['spotify.exe', 'netflix.exe', 'steam.exe', 'vlc.exe', 'stremio.exe'],
        'emoji': '🎮',
        'color': '#e74c3c'
    },
    'Creative': {
        'apps': ['photoshop.exe', 'illustrator.exe', 'obs64.exe'],
        'emoji': '🎨',
        'color': '#f1c40f'
    }
}

# Blue light filter settings
BLUE_LIGHT_THRESHOLD = 30  # minutes of continuous screen time to suggest a break
EVENING_HOUR_START = 18  # 6 PM
EVENING_HOUR_END = 22  # 10 PM

def get_display_name(app_name):
    """Get the friendly display name for an application."""
    return APP_DISPLAY_NAMES.get(app_name, app_name)

def categorize_app(app_name):
    """Categorize an application based on its name with enhanced matching."""
    app_lower = app_name.lower()
    for category, info in APP_CATEGORIES.items():
        if any(app.lower() in app_lower for app in info['apps']):
            return category
    return 'Other'

def get_category_emoji(category):
    """Get the emoji for a category."""
    return APP_CATEGORIES.get(category, {}).get('emoji', '📱')

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
                    
                    if screen_time[name] >= NOTIFICATION_THRESHOLD*60:
                        send_notification(get_display_name(name), screen_time[name])
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Check for blue light filter suggestion
        current_hour = datetime.now().hour
        if EVENING_HOUR_START <= current_hour < EVENING_HOUR_END:
            send_blue_light_notification()
            
        time.sleep(1)

    df = pd.DataFrame(list(screen_time.items()), columns=["Application", "Time_Seconds"])
    df['Display_Name'] = df['Application'].apply(get_display_name)
    df['Time_Minutes'] = df['Time_Seconds'] / 60
    return df.sort_values('Time_Minutes', ascending=False).reset_index(drop=True)

def plot_screen_time(data):
    """Enhanced visualization of screen time usage."""
    plt.style.use('default')  # Using default style instead of seaborn
    
    # Create figure with white background
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor='white')
    fig.patch.set_facecolor('white')
    
    # Prepare data for plotting
    plot_data = data.head(8)
    categories = plot_data['Application'].apply(categorize_app)
    colors = [APP_CATEGORIES.get(cat, {}).get('color', '#95a5a6') for cat in categories]
    
    # Bar chart with category-based colors
    ax1.set_facecolor('white')
    bars = ax1.bar(plot_data['Display_Name'], plot_data['Time_Minutes'], color=colors)
    ax1.set_xlabel("Applications", fontsize=10)
    ax1.set_ylabel("Time (Minutes)", fontsize=10)
    ax1.set_title("Top Applications Usage", fontsize=12, pad=20)
    ax1.grid(True, linestyle='--', alpha=0.7)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Category distribution pie chart
    ax2.set_facecolor('white')
    category_data = data.copy()
    category_data['Category'] = category_data['Application'].apply(categorize_app)
    category_usage = category_data.groupby('Category')['Time_Minutes'].sum()
    
    colors = [APP_CATEGORIES.get(cat, {}).get('color', '#95a5a6') for cat in category_usage.index]
    wedges, texts, autotexts = ax2.pie(category_usage, 
                                      labels=category_usage.index,
                                      colors=colors,
                                      autopct='%1.1f%%',
                                      startangle=90)
    ax2.set_title("Time Distribution by Category", fontsize=12, pad=20)
    
    # Enhance text contrast
    plt.setp(autotexts, size=8, weight="bold")
    plt.setp(texts, size=9)
    
    plt.tight_layout()
    return fig

def analyze_usage_patterns(screen_time_data):
    """Analyze usage patterns with more sophisticated insights."""
    usage_data = screen_time_data.copy()
    usage_data['Category'] = usage_data['Application'].apply(categorize_app)
    category_usage = usage_data.groupby('Category')['Time_Minutes'].sum()
    
    insights = []
    total_time = usage_data['Time_Minutes'].sum()
    
    if total_time > 0:
        # Calculate advanced metrics
        productivity_ratio = category_usage.get('Productivity', 0) / total_time
        entertainment_ratio = (category_usage.get('Entertainment', 0) + 
                             category_usage.get('Social Media', 0)) / total_time
        communication_ratio = category_usage.get('Communication', 0) / total_time
        
        # Generate dynamic insights based on usage patterns
        if productivity_ratio < 0.3:
            insights.append({
                'type': 'warning',
                'message': "🎯 Low productivity detected. Consider using time-blocking techniques."
            })
        elif productivity_ratio > 0.7:
            insights.append({
                'type': 'info',
                'message': "⚡ High productivity! Remember to take breaks to avoid burnout."
            })
            
        if entertainment_ratio > 0.4:
            insights.append({
                'type': 'warning',
                'message': "⚠️ High entertainment usage. Try setting specific leisure time windows."
            })
            
        if communication_ratio > 0.3:
            insights.append({
                'type': 'info',
                'message': "💬 Consider batching communication tasks to reduce context switching."
            })
            
        # Time management insights
        if total_time > 120:
            insights.append({
                'type': 'health',
                'message': "🧘 Practice the 20-20-20 rule: Every 20 minutes, look 20 feet away for 20 seconds."
            })
    
    return insights, category_usage

def generate_ai_recommendations(usage_data, total_time):
    """Generate personalized AI recommendations based on usage patterns."""
    recommendations = []
    
    # Add category column before grouping
    usage_data_with_category = usage_data.copy()
    usage_data_with_category['Category'] = usage_data_with_category['Application'].apply(categorize_app)
    category_usage = usage_data_with_category.groupby('Category')['Time_Minutes'].sum()
    
    # Work-life balance recommendations
    if 'Productivity' in category_usage:
        prod_time = category_usage['Productivity']
        if prod_time > total_time * 0.7:
            recommendations.append("🎯 Consider implementing regular break intervals using the Pomodoro Technique")
        elif prod_time < total_time * 0.3:
            recommendations.append("💪 Try setting specific focus hours for deep work")
    
    # Digital wellness recommendations
    if 'Entertainment' in category_usage and category_usage['Entertainment'] > total_time * 0.4:
        recommendations.append("⏰ Use app timers to maintain balanced screen time")
        recommendations.append("🌟 Schedule specific entertainment time slots")
    
    # Communication optimization
    if 'Communication' in category_usage and category_usage['Communication'] > total_time * 0.3:
        recommendations.append("📧 Set specific times for checking emails and messages")
        recommendations.append("🎯 Use 'Do Not Disturb' mode during focus periods")
    
    # Browser usage optimization
    if 'Browsers' in category_usage and category_usage['Browsers'] > total_time * 0.5:
        recommendations.append("🌐 Use browser extensions to block distracting websites")
        recommendations.append("📚 Try browser tab management techniques")
    
    # Always include some general recommendations
    default_recommendations = [
        "🧘 Practice mindful computing by closing unnecessary applications",
        "💡 Use the built-in blue light filter during evening hours",
        "🎯 Set specific goals for each work session",
        "⚡ Take regular micro-breaks (2 minutes every 30 minutes)"
    ]
    
    # Combine specific and general recommendations
    recommendations.extend(default_recommendations)
    
    # Return top 5 most relevant recommendations, ensuring we always have recommendations
    return recommendations[:5] if recommendations else default_recommendations[:5]

def analyze_blue_light_usage(screen_time_data):
    """
    Analyze screen time data to suggest optimal times for enabling blue light filters.
    """
    recommendations = []
    total_time = screen_time_data['Time_Minutes'].sum()
    
    # Check for prolonged screen time
    if total_time > BLUE_LIGHT_THRESHOLD:
        recommendations.append(
            "🕶️ Prolonged screen usage detected. Consider enabling a blue light filter to reduce eye strain."
        )
    
    # Check if it's evening hours
    current_hour = datetime.now().hour
    if EVENING_HOUR_START <= current_hour < EVENING_HOUR_END:
        recommendations.append(
            "🌙 It's evening time! Enable your blue light filter to improve sleep quality."
        )
    
    return recommendations

def calculate_wellbeing_score(screen_time_data):
    """Calculate a digital wellbeing score based on screen time patterns."""
    score = 100  # Start with perfect score
    deductions = []
    
    # Add category column
    data = screen_time_data.copy()
    data['Category'] = data['Application'].apply(categorize_app)
    total_time = data['Time_Minutes'].sum()
    
    # Get category distribution
    category_usage = data.groupby('Category')['Time_Minutes'].sum()
    
    # Check for excessive entertainment usage
    entertainment_time = category_usage.get('Entertainment', 0) + category_usage.get('Social Media', 0)
    entertainment_ratio = entertainment_time / total_time if total_time > 0 else 0
    if entertainment_ratio > 0.5:
        score -= min(30, int(entertainment_ratio * 60))
        deductions.append(f"High entertainment usage ({int(entertainment_ratio*100)}% of time)")
    
    # Check for work-life balance
    productivity_time = category_usage.get('Productivity', 0)
    productivity_ratio = productivity_time / total_time if total_time > 0 else 0
    if productivity_ratio > 0.8:
        score -= min(20, int((productivity_ratio-0.7) * 100))
        deductions.append("Excessive work focus without breaks")
    
    # Check for context switching
    if len(data) > 10:
        score -= min(15, (len(data) - 10) * 2)
        deductions.append(f"Frequent application switching ({len(data)} apps)")
    
    # Determine score category
    if score >= 80:
        category = "Excellent"
        color = "green"
    elif score >= 60:
        category = "Good"
        color = "blue"
    elif score >= 40:
        category = "Fair"
        color = "orange"
    else:
        category = "Needs Improvement"
        color = "red"
    
    return {
        "score": score,
        "category": category,
        "color": color,
        "deductions": deductions
    }

def calculate_eye_strain_risk(screen_time_data):
    """Calculate eye strain risk based on continuous screen time."""
    # Calculate total continuous screen time
    total_minutes = screen_time_data['Time_Minutes'].sum()
    
    # Define risk levels
    if total_minutes < 30:
        risk = "Low"
        message = "Your current session is well within safe limits."
        color = "green"
    elif total_minutes < 60:
        risk = "Moderate"
        message = "Consider taking a short eye break soon."
        color = "orange"
    else:
        risk = "High"
        message = "Eye strain risk detected. Take a break now."
        color = "red"
    
    # Calculate time until next recommended break
    if total_minutes < 20:
        next_break = 20 - total_minutes
    else:
        next_break = 5  # Take a break soon if over 20 minutes
    
    return {
        "risk": risk,
        "message": message,
        "color": color,
        "next_break": next_break
    }

def generate_focus_session_plan(usage_data):
    """
    Generate an intelligent focus session plan based on historical usage patterns.
    """
    # Calculate optimal work session length based on usage patterns
    usage_data_with_category = usage_data.copy()
    usage_data_with_category['Category'] = usage_data_with_category['Application'].apply(categorize_app)
    
    # Identify user's productive apps
    productive_apps = usage_data_with_category[
        usage_data_with_category['Category'] == 'Productivity'
    ]['Application'].tolist()
    
    # Determine optimal session length (25-45 min) based on productivity patterns
    productivity_time = usage_data_with_category[
        usage_data_with_category['Category'] == 'Productivity'
    ]['Time_Minutes'].sum()
    
    if productivity_time > 60:
        optimal_session = 45  # Longer focus sessions for users who can maintain focus
    elif productivity_time > 30:
        optimal_session = 35  # Medium length sessions
    else:
        optimal_session = 25  # Shorter sessions for users who might struggle with focus
    
    # Determine optimal break length (5-15 min)
    entertainment_ratio = usage_data_with_category[
        usage_data_with_category['Category'] == 'Entertainment'
    ]['Time_Minutes'].sum() / usage_data_with_category['Time_Minutes'].sum() if usage_data_with_category['Time_Minutes'].sum() > 0 else 0
    
    if entertainment_ratio > 0.4:
        optimal_break = 5  # Shorter breaks for users who tend to get distracted
    else:
        optimal_break = 10  # Longer breaks for better recovery
    
    # Generate session plan
    num_sessions = 4  # Default to 4 sessions
    
    session_plan = []
    for i in range(1, num_sessions + 1):
        session_plan.append({
            "session": i,
            "duration": optimal_session,
            "break": optimal_break if i < num_sessions else 15,  # Longer break after last session
            "focus_apps": productive_apps[:3],  # Suggest top 3 productive apps
            "start_time": datetime.now() + timedelta(minutes=(optimal_session + optimal_break) * (i-1))
        })
    
    return session_plan

def analyze_context_switching(screen_time_data):
    """
    Analyze the pattern of application switches to identify context switching patterns.
    """
    # Get top apps used
    apps_used = screen_time_data['Application'].tolist()
    
    # Simple context switching analysis (in a real app, this would use sequential data)
    context_switches = 0
    productivity_to_entertainment = 0
    
    for i in range(len(apps_used) - 1):
        current_app_category = categorize_app(apps_used[i])
        next_app_category = categorize_app(apps_used[i + 1])
        
        if current_app_category != next_app_category:
            context_switches += 1
            
            if current_app_category == 'Productivity' and next_app_category == 'Entertainment':
                productivity_to_entertainment += 1
    
    # Calculate impact score (0-100)
    impact_score = min(100, context_switches * 10)
    
    # Generate recommendations
    recommendations = []
    if context_switches > 5:
        recommendations.append("🔄 You're switching contexts frequently. Try timeboxing your work.")
    if productivity_to_entertainment > 2:
        recommendations.append("⚠️ Productivity interruptions detected. Consider using app blockers during focus time.")
    
    recommendations.append("📱 Group similar tasks together to reduce mental load from switching.")
    
    return {
        "switches": context_switches,
        "impact_score": impact_score,
        "prod_to_ent_switches": productivity_to_entertainment,
        "recommendations": recommendations
    }

def create_weekly_goal_tracker():
    """
    Create a weekly goal tracking system with AI-driven recommendations.
    """
    # Initialize weekly goal tracker with default goals
    default_goals = [
        {
            "category": "Productivity",
            "target_hours": 20,
            "current_hours": 0,
            "progress":0,
            "status": "Not Started",
            "recommendations": [
                "Schedule specific productivity blocks in your calendar",
                "Start with the most important task each day"
            ]
        },
        {
            "category": "Entertainment",
            "target_hours": 10,
            "current_hours": 0,
            "progress":0,
            "status": "Not Started",
            "recommendations": [
                "Limit entertainment to evenings after completing work goals",
                "Use a timer to maintain boundaries"
            ]
        },
        {
            "category": "Communication",
            "target_hours": 5,
            "current_hours": 0,
            "progress":0,
            "status": "Not Started",
            "recommendations": [
                "Batch process emails and messages at scheduled times",
                "Use 'Do Not Disturb' mode during focus periods"
            ]
        }
    ]
    
    return default_goals

def update_weekly_goals(goals, new_usage_data):
    """
    Update weekly goals based on new usage data.
    """
    # In real app, this would store and persist data
    usage_with_category = new_usage_data.copy()
    usage_with_category['Category'] = usage_with_category['Application'].apply(categorize_app)
    category_usage = usage_with_category.groupby('Category')['Time_Minutes'].sum() / 60  # Convert to hours
    
    updated_goals = []
    for goal in goals:
        category = goal["category"]
        current_hours = goal["current_hours"] + (category_usage.get(category, 0) if category in category_usage else 0)
        
        # Calculate progress percentage
        progress = min(100, int((current_hours / goal["target_hours"]) * 100)) if goal["target_hours"] > 0 else 0
        
        # Update status
        if progress == 0:
            status = "Not Started"
        elif progress < 50:
            status = "In Progress"
        elif progress < 100:
            status = "Almost Complete"
        else:
            status = "Completed"
        
        # Generate adaptive recommendations
        recommendations = goal["recommendations"]
        if status == "Not Started" and datetime.now().weekday() >= 3:  # Late in the week
            recommendations = ["Consider adjusting this goal for next week", "Schedule specific time blocks for this activity"]
        
        updated_goals.append({
            "category": category,
            "target_hours": goal["target_hours"],
            "current_hours": current_hours,
            "progress": progress,
            "status": status,
            "recommendations": recommendations
        })
    
    return updated_goals

def create_personalized_eye_care_routine():
    """
    Create a personalized eye care routine based on 20-20-20 rule with customization.
    """
    # Base 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds
    base_routine = {
        "interval_minutes": 20,
        "distance_feet": 20,
        "duration_seconds": 20,
        "enabled": True
    }
    
    # Additional exercises
    exercises = [
        {
            "name": "Eye Rolling",
            "description": "Roll your eyes in a circular motion, 5 times clockwise and 5 times counterclockwise",
            "benefit": "Strengthens eye muscles and relieves strain",
            "duration_seconds": 30
        },
        {
            "name": "Palming",
            "description": "Rub your palms together to warm them, then gently place them over your closed eyes",
            "benefit": "Relaxes the eyes and reduces strain",
            "duration_seconds": 60
        },
        {
            "name": "Near-Far Focus",
            "description": "Focus on your thumb, then focus on something in the distance, repeat 10 times",
            "benefit": "Improves focus flexibility and reduces eye fatigue",
            "duration_seconds": 45
        }
    ]
    
    return {
        "base_routine": base_routine,
        "exercises": exercises,
        "custom_reminders": [
            "Blink frequently when using screens",
            "Adjust screen brightness based on ambient light",
            "Position your screen at arm's length and slightly below eye level"
        ]
    }

def adjust_eye_care_routine(base_routine, screen_time_data):
    """
    Dynamically adjust eye care routine based on screen time patterns.
    """
    adjusted_routine = base_routine.copy()
    total_screen_time = screen_time_data['Time_Minutes'].sum()
    
    # Adjust interval based on total screen time
    if total_screen_time > 90:  # Heavy screen use
        adjusted_routine["base_routine"]["interval_minutes"] = 15  # More frequent breaks
        adjusted_routine["base_routine"]["duration_seconds"] = 30  # Longer breaks
    elif total_screen_time < 30:  # Light screen use
        adjusted_routine["base_routine"]["interval_minutes"] = 30  # Less frequent breaks
    
    # Add specific recommendations based on categories
    category_data = screen_time_data.copy()
    category_data['Category'] = category_data['Application'].apply(categorize_app)
    
    # If lots of creative work (which requires intense focus)
    if 'Creative' in category_data['Category'].values:
        adjusted_routine["custom_reminders"].append(
            "Creative work detected: Take occasional 2-minute breaks to prevent eye strain during intense focus"
        )
    
    # If lots of reading (browsers, productivity apps)
    if ('Browsers' in category_data['Category'].values or 
        'Productivity' in category_data['Category'].values):
        adjusted_routine["custom_reminders"].append(
            "Increase font size for reading to reduce eye strain"
        )
    
    return adjusted_routine

def get_running_entertainment_apps():
    """
    Get a list of running entertainment apps.
    """
    entertainment_apps = APP_CATEGORIES['Entertainment']['apps']
    running_apps = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() in [app.lower() for app in entertainment_apps]:
            running_apps.append(proc.info['name'])
    return running_apps

def block_app(app_name):
    """
    Block an app by killing its process.
    """
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == app_name.lower():
                subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])], shell=True)
                print(f"Blocked {app_name}")
                break
        else:
            print(f"{app_name} is not running.")
    except Exception as e:
        print(f"Failed to block {app_name}: {e}")

def block_apps_for_duration(apps_to_block, duration_minutes):
    """
    Block apps for a specified duration (in minutes).
    """
    end_time = time.time() + duration_minutes * 60
    while time.time() < end_time:
        for app in apps_to_block:
            print(f"Attempting to block {app}...")
            block_app(app)
        time.sleep(5)  # Check every 5 seconds

def start_blocking_thread(apps_to_block, duration_minutes):
    """
    Start a background thread to block apps.
    """
    thread = threading.Thread(target=block_apps_for_duration, args=(apps_to_block, duration_minutes))
    thread.start()
    return thread


# Streamlit UI
def main():
    st.set_page_config(
        page_title="Smart Screen Time Tracker",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📱 Smart Screen Time Tracker")
    st.markdown("### Monitor your digital wellness with AI-powered insights")
    
    # Create tabs for different features
    tabs = st.tabs([
        "📊 Dashboard", 
        "🎯 Focus Sessions", 
        "👁️ Eye Care", 
        "📈 Weekly Goals",
        "⏳ Time Blocking",
        "📅 Calendar",
        "🚫 App Blocker",  # New tab for app blocking
        "⚙️ Settings"
    ])
    
    with tabs[0]:  # Dashboard Tab
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Real-time Screen Time Monitoring")
            if st.button("Start Tracking (1 Minute)"):
                with st.spinner("Tracking your screen time..."):
                    screen_time_data = track_screen_time(duration=60)  # 1 minute for demo
                    st.session_state.screen_time_data = screen_time_data
                    st.success("Tracking completed!")
            
            # Display data and visualizations if available
            if 'screen_time_data' in st.session_state:
                data = st.session_state.screen_time_data
                
                # Display summary stats
                st.markdown("### 📊 Usage Summary")
                total_time = data['Time_Minutes'].sum()
                st.metric("Total Screen Time", f"{total_time:.1f} minutes")
                
                # Display chart
                fig = plot_screen_time(data)
                st.pyplot(fig)
                
                # Display raw data in expandable section
                with st.expander("View detailed application usage"):
                    st.dataframe(data[['Display_Name', 'Time_Minutes']].sort_values('Time_Minutes', ascending=False))
        
        with col2:
            st.subheader("AI Insights")
            
            if 'screen_time_data' in st.session_state:
                data = st.session_state.screen_time_data
                insights, category_usage = analyze_usage_patterns(data)
                total_time = data['Time_Minutes'].sum()
                
                # Display wellbeing score
                wellbeing = calculate_wellbeing_score(data)
                st.markdown(f"### Digital Wellbeing: <span style='color:{wellbeing['color']}'>{wellbeing['score']}/100</span>", unsafe_allow_html=True)
                st.caption(f"Category: {wellbeing['category']}")
                
                if wellbeing['deductions']:
                    with st.expander("Areas for improvement"):
                        for deduction in wellbeing['deductions']:
                            st.markdown(f"- {deduction}")
                
                # Display eye strain risk
                eye_strain = calculate_eye_strain_risk(data)
                st.markdown(f"### Eye Strain Risk: <span style='color:{eye_strain['color']}'>{eye_strain['risk']}</span>", unsafe_allow_html=True)
                st.caption(eye_strain['message'])
                
                # Context switching analysis
                context_analysis = analyze_context_switching(data)
                if context_analysis['switches'] > 0:
                    st.markdown(f"### Context Switching Score: {context_analysis['impact_score']}/100")
                    st.caption(f"You switched between {context_analysis['switches']} different contexts")
                    
                    with st.expander("Context switching recommendations"):
                        for rec in context_analysis['recommendations']:
                            st.markdown(f"- {rec}")
                
                # Display personalized recommendations
                st.markdown("### 💡 Smart Recommendations")
                recommendations = generate_ai_recommendations(data, total_time)
                for rec in recommendations:
                    st.markdown(f"- {rec}")
    
    with tabs[1]:  # Focus Sessions Tab
        st.subheader("🎯 AI-Powered Focus Sessions")
        st.markdown("Plan your work sessions based on your productivity patterns")
        
        if 'screen_time_data' in st.session_state:
            # Generate focus session plan
            if 'focus_plan' not in st.session_state:
                st.session_state.focus_plan = generate_focus_session_plan(st.session_state.screen_time_data)
            
            # Display focus session plan
            for i, session in enumerate(st.session_state.focus_plan):
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    st.markdown(f"### Session {session['session']}")
                    st.caption(f"Start: {session['start_time'].strftime('%I:%M %p')}")
                
                with col2:
                    st.metric("Focus Time", f"{session['duration']} min")
                    st.caption(f"Break: {session['break']} min")
                
                with col3:
                    st.markdown("#### Suggested apps:")
                    for app in session['focus_apps']:
                        st.markdown(f"- {get_display_name(app)}")
                
                if st.button(f"Start Session {session['session']}"):
                    st.session_state.active_session = session
                    st.session_state.session_start_time = datetime.now()
                    st.session_state.show_timer = True
            
            # Display active session timer if one is running
            if 'show_timer' in st.session_state and st.session_state.show_timer:
                st.markdown("---")
                st.subheader("⏱️ Active Focus Session")
                
                elapsed_time = (datetime.now() - st.session_state.session_start_time).total_seconds() / 60
                remaining_time = max(0, st.session_state.active_session['duration'] - elapsed_time)
                
                progress = min(1.0, elapsed_time / st.session_state.active_session['duration'])
                
                st.progress(progress)
                st.metric("Time Remaining", f"{remaining_time:.1f} min")
                
                if remaining_time <= 0:
                    st.success(f"Session complete! Take a {st.session_state.active_session['break']} minute break.")
                    if st.button("Start Break Timer"):
                        st.session_state.break_start_time = datetime.now()
                        st.session_state.show_break_timer = True
                        st.session_state.show_timer = False
                
                if st.button("End Session Early"):
                    st.session_state.show_timer = False
            
            # Display break timer if one is running
            if 'show_break_timer' in st.session_state and st.session_state.show_break_timer:
                st.markdown("---")
                st.subheader("☕ Break Time")
                
                break_elapsed = (datetime.now() - st.session_state.break_start_time).total_seconds() / 60
                break_remaining = max(0, st.session_state.active_session['break'] - break_elapsed)
                
                break_progress = min(1.0, break_elapsed / st.session_state.active_session['break'])
                
                st.progress(break_progress)
                st.metric("Break Time Remaining", f"{break_remaining:.1f} min")
                
                if break_remaining <= 0:
                    st.info("Break over! Ready to start your next session?")
                    if st.button("End Break"):
                        st.session_state.show_break_timer = False
        else:
            st.info("Track your screen time first to generate personalized focus sessions.")
            if st.button("Start Quick Track (30 seconds)"):
                with st.spinner("Tracking your screen time for quick analysis..."):
                    screen_time_data = track_screen_time(duration=30)  # 30 seconds for quick demo
                    st.session_state.screen_time_data = screen_time_data
                    st.success("Tracking completed!")
    
    with tabs[2]:  # Eye Care Tab
        st.subheader("👁️ Smart Eye Care")
        st.markdown("Personalized eye strain prevention based on your screen time habits")
        
        # Initialize eye care routine if not exists
        if 'eye_care_routine' not in st.session_state:
            st.session_state.eye_care_routine = create_personalized_eye_care_routine()
        
        # Adjust routine based on screen time data if available
        if 'screen_time_data' in st.session_state:
            st.session_state.eye_care_routine = adjust_eye_care_routine(
                st.session_state.eye_care_routine, 
                st.session_state.screen_time_data
            )
        
        # Display routine settings
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 20-20-20 Rule Settings")
            
            interval = st.number_input(
                "Break interval (minutes)",
                min_value=5,
                max_value=60,
                value=st.session_state.eye_care_routine["base_routine"]["interval_minutes"]
            )
            
            duration = st.number_input(
                "Look away duration (seconds)",
                min_value=10,
                max_value=120,
                value=st.session_state.eye_care_routine["base_routine"]["duration_seconds"]
            )
            
            st.session_state.eye_care_routine["base_routine"]["interval_minutes"] = interval
            st.session_state.eye_care_routine["base_routine"]["duration_seconds"] = duration
            
            enable = st.checkbox(
                "Enable eye break reminders",
                value=st.session_state.eye_care_routine["base_routine"]["enabled"]
            )
            st.session_state.eye_care_routine["base_routine"]["enabled"] = enable
            
            if st.button("Start Eye Care Timer"):
                st.session_state.eye_timer_start = datetime.now()
                st.session_state.eye_timer_active = True
        
        with col2:
            st.markdown("### Additional Eye Exercises")
            for i, exercise in enumerate(st.session_state.eye_care_routine["exercises"]):
                with st.expander(f"{exercise['name']} ({exercise['duration_seconds']} sec)"):
                    st.markdown(f"**Description:** {exercise['description']}")
                    st.markdown(f"**Benefit:** {exercise['benefit']}")
                    
                    if st.button(f"Start {exercise['name']} Exercise", key=f"ex_{i}"):
                        st.session_state.active_exercise = exercise
                        st.session_state.exercise_start_time = datetime.now()
                        st.session_state.show_exercise_timer = True
        
        # Display recommendations
        st.markdown("### 💡 Eye Care Recommendations")
        for tip in st.session_state.eye_care_routine["custom_reminders"]:
            st.markdown(f"- {tip}")
        
        # Display active eye care timer if running
        if 'eye_timer_active' in st.session_state and st.session_state.eye_timer_active:
            st.markdown("---")
            st.subheader("⏱️ Eye Break Timer")
            
            elapsed = (datetime.now() - st.session_state.eye_timer_start).total_seconds() / 60
            remaining = max(0, interval - elapsed)
            
            st.progress(min(1.0, elapsed / interval))
            st.metric("Next eye break in", f"{remaining:.1f} min")
            
            if remaining <= 0:
                st.success(f"Time for an eye break! Look 20 feet away for {duration} seconds.")
                if st.button("Reset Timer"):
                    st.session_state.eye_timer_start = datetime.now()
        
        # Display exercise timer if active
        if 'show_exercise_timer' in st.session_state and st.session_state.show_exercise_timer:
            st.markdown("---")
            st.subheader(f"⏱️ {st.session_state.active_exercise['name']} Exercise")
            
            ex_elapsed = (datetime.now() - st.session_state.exercise_start_time).total_seconds()
            ex_duration = st.session_state.active_exercise['duration_seconds']
            ex_remaining = max(0, ex_duration - ex_elapsed)
            
            st.progress(min(1.0, ex_elapsed / ex_duration))
            st.metric("Time Remaining", f"{ex_remaining:.1f} sec")
            st.markdown(f"**Instructions:** {st.session_state.active_exercise['description']}")
            
            if ex_remaining <= 0:
                st.success("Exercise complete!")
                if st.button("End Exercise"):
                    st.session_state.show_exercise_timer = False
    
    with tabs[3]:  # Weekly Goals Tab
        st.subheader("📈 Weekly Screen Time Goals")
        st.markdown("Set and track your digital wellness goals with AI assistance")
        
        # Initialize weekly goals if not exists
        if 'weekly_goals' not in st.session_state:
            st.session_state.weekly_goals = create_weekly_goal_tracker()
        
        # Update goals with new data if available
        if 'screen_time_data' in st.session_state:
            st.session_state.weekly_goals = update_weekly_goals(
                st.session_state.weekly_goals,
                st.session_state.screen_time_data
            )
        
        # Display current day and estimated week progress
        current_day = datetime.now().strftime("%A")
        week_progress = min(100, int((datetime.now().weekday() + 1) / 7 * 100))
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### Current Progress: {current_day}")
        with col2:
            st.progress(week_progress / 100)
            st.caption(f"Week Progress: {week_progress}%")
        
        # Display goals
        for goal in st.session_state.weekly_goals:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                emoji = get_category_emoji(goal["category"])
                st.markdown(f"### {emoji} {goal['category']}")
                st.metric(
                    "Current / Target",
                    f"{goal['current_hours']:.1f} / {goal['target_hours']} hrs"
                )
            
            with col2:
                st.progress(goal["progress"] / 100)
                st.caption(f"Progress: {goal['progress']}% ({goal['status']})")
            
            with col3:
                st.markdown("#### AI Coach Tips:")
                for tip in goal["recommendations"][:2]:  # Show top 2 tips
                    st.markdown(f"- {tip}")
            
            # Allow goal adjustment
            with st.expander(f"Adjust {goal['category']} Goal"):
                new_target = st.slider(
                    "Target Hours",
                    min_value=1,
                    max_value=40,
                    value=int(goal["target_hours"])
                )
                
                if st.button(f"Update {goal['category']} Goal"):
                    for i, g in enumerate(st.session_state.weekly_goals):
                        if g["category"] == goal["category"]:
                            st.session_state.weekly_goals[i]["target_hours"] = new_target
                            # Recalculate progress
                            progress = min(100, int((g["current_hours"] / new_target) * 100)) if new_target > 0 else 0
                            st.session_state.weekly_goals[i]["progress"] = progress
                            st.experimental_rerun()
    with tabs[4]:  # Time Blocking Tab
        st.subheader("⏳ Energy-Based Time Blocking")
        st.markdown("Organize your tasks based on your natural energy patterns throughout the day.")
        
        # Render the energy wheel and related components
        render_energy_wheel()

    with tabs[5]:  # Calendar Tab
        st.subheader("📅 Calendar Integration")
        st.markdown("Manage your schedule and analyze your calendar activity.")

        # Initialize calendar service if not already done
        if 'calendar_service' not in st.session_state:
            st.session_state.calendar_service = None

        # Authentication section
        if st.session_state.calendar_service is None:
            st.subheader("Authentication")
            auth_button = st.button("Connect to Google Calendar", key="auth_button")
            
            if auth_button:
                try:
                    with st.spinner("Authenticating..."):
                        st.session_state.calendar_service = get_calendar_service()
                    st.success("Authentication successful!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Authentication failed: {e}")
        else:
            st.success("✓ Connected to Google Calendar")

            # Date range selector
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From", datetime.date.today())
            with col2:
                default_end = datetime.date.today() + datetime.timedelta(days=14)
                end_date = st.date_input("To", default_end)
            
            # Convert to datetime and format for API
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min).isoformat() + 'Z'
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max).isoformat() + 'Z'
            
            # Number of events to fetch
            max_events = st.slider("Maximum number of events to display", 1, 50, 10)
            
            # Get events
            with st.spinner("Loading events..."):
                events_result = st.session_state.calendar_service.events().list(
                    calendarId='primary', 
                    timeMin=start_datetime,
                    timeMax=end_datetime,
                    maxResults=max_events, 
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
            
            if not events:
                st.info("No events found for the selected period.")
            else:
                # Group events by date
                events_by_date = {}
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    
                    # Format the start time for better display
                    if 'T' in start:  # This is a dateTime
                        start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                        event_date = start_dt.date()
                        formatted_time = start_dt.strftime("%H:%M")
                    else:  # This is a date
                        event_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
                        formatted_time = "All day"
                    
                    if event_date not in events_by_date:
                        events_by_date[event_date] = []
                    
                    # Extract color if available
                    event_color = event.get('colorId', '0')
                    
                    events_by_date[event_date].append({
                        "time": formatted_time,
                        "summary": event.get('summary', 'Untitled Event'),
                        "description": event.get('description', ''),
                        "location": event.get('location', ''),
                        "color": event_color
                    })
                
                # Display events by date
                for date in sorted(events_by_date.keys()):
                    st.subheader(date.strftime("%A, %B %d, %Y"))
                    
                    for event in events_by_date[date]:
                        with st.container():
                            st.markdown(f"""
                            <div class="event-card">
                                <strong>{event['time']}</strong> - 
                                <span class="highlight">{event['summary']}</span>
                                {f"<br><small>📍 {event['location']}</small>" if event['location'] else ""}
                                {f"<br><small>{event['description']}</small>" if event['description'] else ""}
                            </div>
                            """, unsafe_allow_html=True)

            # Calendar Activity Heatmap
            st.subheader("Calendar Activity Heatmap")
            st.markdown("This heatmap shows your calendar activity pattern. Darker colors indicate more events scheduled on that day.")
            
            heatmap = create_calendar_heatmap(events, start_date, end_date)
            st.altair_chart(heatmap, use_container_width=True)

    with tabs[6]:  # App Blocker Tab
        st.subheader("🚫 App Blocker")
        st.markdown("Block distracting apps to stay focused.")

        # Automatically detect entertainment apps
        entertainment_apps = APP_CATEGORIES['Entertainment']['apps']
        st.markdown(f"**Detected Entertainment Apps:** {', '.join([APP_DISPLAY_NAMES.get(app, app) for app in entertainment_apps])}")

        # Duration for blocking
        duration_minutes = st.number_input(
            "Blocking duration (minutes)",
            min_value=1,
            max_value=120,
            value=30
        )

        # Start blocking
        if st.button("Block Entertainment Apps"):
            if not entertainment_apps:
                st.warning("No entertainment apps found to block.")
            else:
                st.session_state.blocking_thread = start_blocking_thread(entertainment_apps, duration_minutes)
                st.success(f"Blocking {len(entertainment_apps)} entertainment apps for {duration_minutes} minutes...")

        # Show currently blocked apps
        if 'blocking_thread' in st.session_state and st.session_state.blocking_thread.is_alive():
            st.markdown("### Currently Blocked Apps")
            for app in entertainment_apps:
                st.markdown(f"- {APP_DISPLAY_NAMES.get(app, app)}")
        else:
            st.info("No apps are currently being blocked.")

    
    with tabs[7]:  # Settings Tab
        st.subheader("⚙️ Settings & Preferences")
        
        # User profiles
        st.markdown("### 👤 User Profiles")
        profiles = ["Default", "Work Focus", "Casual Browsing", "Creative Work"]
        selected_profile = st.selectbox("Select Profile", profiles)
        
        if st.button("Create New Profile"):
            st.text_input("Profile Name", placeholder="Enter profile name...")
            st.success("Custom profile settings will be saved here")
        
        # Notification settings
        st.markdown("### 🔔 Notifications")
        
        notification_threshold = st.slider(
            "Notification Threshold (seconds)",
            min_value=10,
            max_value=120,
            value=NOTIFICATION_THRESHOLD,
            step=5
        )
        
        notification_cooldown = st.slider(
            "Notification Cooldown (seconds)",
            min_value=5,
            max_value=60,
            value=NOTIFICATION_COOLDOWN,
            step=5
        )
        
        # App categories management
        st.markdown("### 📱 Application Categories")
        
        # Allow custom categorization
        st.markdown("#### Customize Application Categories")
        
        sample_apps = list(APP_DISPLAY_NAMES.keys())[:10]  # Show first 10 apps for demo
        selected_app = st.selectbox("Select Application", sample_apps)
        
        current_category = next((category for category, info in APP_CATEGORIES.items() 
                              if selected_app in info['apps']), "Other")
        
        new_category = st.selectbox(
            f"Categorize {selected_app}",
            list(APP_CATEGORIES.keys()) + ["Other"],
            index=list(APP_CATEGORIES.keys()).index(current_category) if current_category in APP_CATEGORIES else len(APP_CATEGORIES)
        )
        
        if st.button("Update Category"):
            st.success(f"Updated {selected_app} to category: {new_category}")
            # In a real app, this would update APP_CATEGORIES
        
        # Data management
        st.markdown("### 💾 Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Data"):
                st.info("Data export functionality would be here")
        
        with col2:
            if st.button("Clear All Data"):
                if 'screen_time_data' in st.session_state:
                    del st.session_state.screen_time_data
                if 'weekly_goals' in st.session_state:
                    del st.session_state.weekly_goals
                if 'focus_plan' in st.session_state:
                    del st.session_state.focus_plan
                if 'eye_care_routine' in st.session_state:
                    del st.session_state.eye_care_routine
                    
                st.success("All data cleared successfully")
                st.experimental_rerun()

if __name__ == "__main__":
    main()