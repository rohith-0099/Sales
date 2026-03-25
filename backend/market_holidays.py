"""
Market Holidays Module
Provides functionality to detect and tag country-specific festivals and holidays
"""

import pandas as pd
from datetime import datetime, timedelta
import holidays

class MarketFestivalsCalendar:
    """
    Manages festival dates and their impact on sales for a specific country
    """
    
    def __init__(self, country_code='IN'):
        self.country_code = str(country_code).upper()
        # Initialize country holidays
        if hasattr(holidays, self.country_code):
            self.holidays = getattr(holidays, self.country_code)(years=range(2020, 2027))
        else:
            # Fallback to India if not found
            self.holidays = getattr(holidays, 'IN')(years=range(2020, 2027))
            
        # Major shopping festivals
        self.major_festivals = {
            'Diwali': ['Diwali', 'Deepavali'],
            'Holi': ['Holi'],
            'Eid': ['Eid al-Fitr', 'Eid al-Adha', 'Id-ul-Fitr', 'Id-ul-Zuha'],
            'Christmas': ['Christmas'],
            'New Year': ['New Year'],
            'Durga Puja': ['Dussehra', 'Durga Puja'],
            'Thanksgiving': ['Thanksgiving'],
            'Black Friday': ['Black Friday'],
            'Independence Day': ['Independence', '4th of July', 'Fourth of July'],
            'Republic Day': ['Republic Day'],
            'Easter': ['Easter'],
            'Halloween': ['Halloween'],
            'Labor Day': ['Labor Day']
        }
    
    def is_holiday(self, date):
        if isinstance(date, str):
            date = pd.to_datetime(date)
        return date in self.holidays
    
    def get_holiday_name(self, date):
        if isinstance(date, str):
            date = pd.to_datetime(date)
        return self.holidays.get(date, None)
    
    def get_festival_category(self, holiday_name):
        if not holiday_name:
            return None
        
        for category, keywords in self.major_festivals.items():
            for keyword in keywords:
                if keyword.lower() in holiday_name.lower():
                    return category
        return 'Other'
    
    def days_to_nearest_festival(self, date, festival_name=None):
        if isinstance(date, str):
            date = pd.to_datetime(date)
        
        search_range = 60
        min_distance = float('inf')
        nearest_festival = None
        
        for i in range(-search_range, search_range):
            check_date = date + timedelta(days=i)
            if check_date in self.holidays:
                holiday_name = self.holidays[check_date]
                category = self.get_festival_category(holiday_name)
                
                if festival_name:
                    if category == festival_name:
                        if abs(i) < abs(min_distance):
                            min_distance = i
                            nearest_festival = category
                else:
                    if category in self.major_festivals.keys():
                        if abs(i) < abs(min_distance):
                            min_distance = i
                            nearest_festival = category
        
        return min_distance if min_distance != float('inf') else None, nearest_festival
    
    def add_festival_features(self, df, date_column='date'):
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        df['is_holiday'] = df[date_column].apply(self.is_holiday)
        df['holiday_name'] = df[date_column].apply(self.get_holiday_name)
        df['festival_category'] = df['holiday_name'].apply(self.get_festival_category)
        
        festival_data = df[date_column].apply(
            lambda x: self.days_to_nearest_festival(x)
        )
        df['days_to_festival'] = festival_data.apply(lambda x: x[0] if x[0] is not None else 0)
        df['nearest_festival'] = festival_data.apply(lambda x: x[1])
        
        df['is_pre_festival'] = (df['days_to_festival'] > 0) & (df['days_to_festival'] <= 7)
        df['is_post_festival'] = (df['days_to_festival'] < 0) & (df['days_to_festival'] >= -3)
        
        df['month'] = df[date_column].dt.month
        df['is_festive_season'] = df['month'].isin([9, 10, 11, 12])
        
        return df
    
    def get_festival_impact_score(self, date):
        if isinstance(date, str):
            date = pd.to_datetime(date)
        
        score = 0.0
        
        if self.is_holiday(date):
            holiday_name = self.get_holiday_name(date)
            category = self.get_festival_category(holiday_name)
            
            if category in ['Diwali', 'Thanksgiving', 'Black Friday']:
                score = 1.0
            elif category in ['Christmas', 'Eid', 'New Year']:
                score = 0.8
            elif category in ['Holi', 'Durga Puja', 'Easter', 'Halloween', 'Independence Day']:
                score = 0.7
            else:
                score = 0.5
        
        days_to, festival = self.days_to_nearest_festival(date)
        if days_to and 0 < days_to <= 7:
            pre_festival_score = 0.6 * (8 - days_to) / 7
            score = max(score, pre_festival_score)
        
        return score

# Manager to cache calendars
_calendars = {}

def get_calendar(country_code='IN'):
    code = str(country_code).upper()
    if code not in _calendars:
        _calendars[code] = MarketFestivalsCalendar(code)
    return _calendars[code]
