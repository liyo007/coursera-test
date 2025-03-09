# cal.py
import os
import datetime
import pickle
import pandas as pd
import numpy as np
import altair as alt
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Gets authenticated Google Calendar service.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials are not available or are invalid, ask the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Need to specify the path to your credentials.json file
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Build and return the service
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_calendar_heatmap(events_data, start_date, end_date):
    """
    Create a calendar heatmap visualization of events.
    """
    # Create date range
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Create a DataFrame with dates
    calendar_df = pd.DataFrame({
        'date': date_range,
        'count': 0
    })
    
    # Count events per day
    for event in events_data:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'T' in start:  # This is a dateTime
            event_date = datetime.datetime.fromisoformat(start.replace('Z', '+00:00')).date()
        else:  # This is a date
            event_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        
        # Increment count for the day
        idx = calendar_df[calendar_df['date'].dt.date == event_date].index
        if len(idx) > 0:
            calendar_df.loc[idx, 'count'] += 1
    
    # Add day and month for grouping
    calendar_df['day'] = calendar_df['date'].dt.day_name()
    calendar_df['month'] = calendar_df['date'].dt.month_name()
    
    # Create heatmap with Altair
    heatmap = alt.Chart(calendar_df).mark_rect().encode(
        x=alt.X('date:O', title='Date', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('day:O', title='Day', sort=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
        color=alt.Color('count:Q', scale=alt.Scale(scheme='blues'), legend=alt.Legend(title='Event Count')),
        tooltip=['date', 'day', 'count']
    ).properties(
        width=800,
        height=300,
        title='Calendar Activity Heatmap'
    )
    
    return heatmap

def fetch_events(service, start_datetime, end_datetime, max_results=10):
    """
    Fetch events from Google Calendar within a specified date range.
    """
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=start_datetime,
        timeMax=end_datetime,
        maxResults=max_results, 
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])

def group_events_by_date(events):
    """
    Group events by date for display purposes.
    """
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
    
    return events_by_date