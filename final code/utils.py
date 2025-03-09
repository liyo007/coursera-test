# utils.py

from constants import APP_DISPLAY_NAMES, APP_CATEGORIES

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