# app.py
from constants import NOTIFICATION_THRESHOLD
import streamlit as st
import pandas as pd
from tracker import track_screen_time
from visualisation import plot_screen_time
from analysis import analyze_usage_patterns, generate_ai_recommendations, analyze_blue_light_usage
from utils import get_display_name

def main():
    st.set_page_config(page_title="Smart Screen Time Tracker", page_icon="🤖", layout="wide")
    
    st.title("🤖 Smart Screen Time Analytics")
    st.markdown("### AI-Powered Usage Insights & Recommendations")
    
    with st.sidebar:
        st.header("⚙️ Settings")
        track_duration = st.slider(
            "Tracking Duration (seconds)", 
            min_value=10, 
            max_value=3600, 
            value=60
        )
    
    if st.button("Start Smart Tracking", type="primary"):
        with st.spinner("🔍 Analyzing your screen time patterns..."):
            screen_time_data = track_screen_time(duration=track_duration)
            
            # Convert the dictionary to a DataFrame
            df = pd.DataFrame(list(screen_time_data.items()), columns=["Application", "Time_Seconds"])
            df['Display_Name'] = df['Application'].apply(get_display_name)
            df['Time_Minutes'] = df['Time_Seconds'] / 60
            
            # Display usage statistics
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Active Applications")
                significant_usage = df[df['Time_Minutes'] > 1]
                st.dataframe(
                    significant_usage[['Display_Name', 'Time_Minutes']].style.format({
                        'Time_Minutes': '{:.1f}'
                    })
                )
            
            # Generate and display insights
            insights, category_usage = analyze_usage_patterns(df)
            
            # Get recommendations after adding category information
            recommendations = generate_ai_recommendations(df, df['Time_Minutes'].sum())
            
            # Get blue light filter recommendations
            blue_light_recommendations = analyze_blue_light_usage(df)
            
            with col2:
                st.subheader("🧠 AI Insights")
                for insight in insights:
                    if insight['type'] == 'warning':
                        st.warning(insight['message'])
                    elif insight['type'] == 'info':
                        st.info(insight['message'])
                    else:
                        st.success(insight['message'])
            
            # Display visualizations
            st.subheader("📈 Usage Analytics")
            fig = plot_screen_time(df)
            st.pyplot(fig)
            
            # Display recommendations
            st.subheader("💡 Smart Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
            
            # Display blue light filter recommendations
            if blue_light_recommendations:
                st.subheader("🕶️ Blue Light Filter Recommendations")
                for i, rec in enumerate(blue_light_recommendations, 1):
                    st.write(f"{i}. {rec}")
            
            # Display alerts for excessive usage
            st.subheader("⚠️ Usage Alerts")
            excessive_usage = df[df['Time_Minutes'] > NOTIFICATION_THRESHOLD]
            if not excessive_usage.empty:
                for _, row in excessive_usage.iterrows():
                    st.warning(f"Extended usage detected: {row['Display_Name']} ({row['Time_Minutes']:.1f} minutes)")
            else:
                st.success("👏 Great job! No excessive application usage detected.")

    st.markdown("---")
    st.caption("Developed by Shashank and rupiga")

if __name__ == "__main__":
    main()