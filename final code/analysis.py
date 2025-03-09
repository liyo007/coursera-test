# analysis.py

import pandas as pd
from utils import categorize_app
from constants import APP_CATEGORIES

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

# analysis.py

from datetime import datetime
from constants import BLUE_LIGHT_THRESHOLD, EVENING_HOUR_START, EVENING_HOUR_END

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