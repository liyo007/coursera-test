# constants.py

# Constants
# constants.py

# Blue light filter settings
BLUE_LIGHT_THRESHOLD = 30  # minutes of continuous screen time to suggest a break
EVENING_HOUR_START = 18  # 6 PM
EVENING_HOUR_END = 22  # 10 PM
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
        'apps': ['spotify.exe', 'netflix.exe', 'steam.exe', 'vlc.exe','stremio.exe'],
        'emoji': '🎮',
        'color': '#e74c3c'
    },
    'Creative': {
        'apps': ['photoshop.exe', 'illustrator.exe', 'obs64.exe'],
        'emoji': '🎨',
        'color': '#f1c40f'
    }
}