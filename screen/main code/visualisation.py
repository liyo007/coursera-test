# visualization.py

import matplotlib.pyplot as plt
import pandas as pd
from constants import APP_CATEGORIES
from utils import categorize_app

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