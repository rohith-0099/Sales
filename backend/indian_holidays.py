"""
Indian Holidays Module
Provides functionality to detect and tag Indian festivals and holidays
"""

import pandas as pd
from datetime import datetime, timedelta
import holidays

class IndianFestivalCalendar:
    """
    Manages Indian festival dates and their impact on sales
    """
    
    def __init__(self):
        # Initialize Indian holidays
        self.holidays = holidays.India(years=range(2020, 2027))
        
        # Major shopping festivals in India
        self.major_festivals = {
            'Diwali': ['Diwali', 'Deepavali'],
            'Holi': ['Holi'],
            'Eid': ['Eid al-Fitr', 'Eid al-Adha', 'Id-ul-Fitr', 'Id-ul-Zuha'],
            'Christmas': ['Christmas'],
            'New Year': ['New Year'],
            'Durga Puja': ['Dussehra', 'Durga Puja'],
            'Raksha Bandhan': ['Raksha Bandhan'],
            'Onam': ['Onam'],
            'Pongal': ['Pongal'],
            'Republic Day': ['Republic Day'],
            'Independence Day': ['Independence Day']
        }
    
    def is_holiday(self, date):
        """Check if a date is a holiday"""
        if isinstance(date, str):
            date = pd.to_datetime(date)
        return date in self.holidays
    
    def get_holiday_name(self, date):
        """Get the name of the holiday"""
        if isinstance(date, str):
            date = pd.to_datetime(date)
        return self.holidays.get(date, None)
    
    def get_festival_category(self, holiday_name):
        """Categorize holiday into major festival groups"""
        if not holiday_name:
            return None
        
        for category, keywords in self.major_festivals.items():
            for keyword in keywords:
                if keyword.lower() in holiday_name.lower():
                    return category
        return 'Other'
    
    def days_to_nearest_festival(self, date, festival_name=None):
        """
        Calculate days to the nearest major festival
        If festival_name is provided, calculate to that specific festival
        """
        if isinstance(date, str):
            date = pd.to_datetime(date)
        
        # Look for festivals within 60 days
        search_range = 60
        min_distance = float('inf')
        nearest_festival = None
        
        for i in range(-search_range, search_range):
            check_date = date + timedelta(days=i)
            if check_date in self.holidays:
                holiday_name = self.holidays[check_date]
                category = self.get_festival_category(holiday_name)
                
                # If specific festival requested, check for match
                if festival_name:
                    if category == festival_name:
                        if abs(i) < abs(min_distance):
                            min_distance = i
                            nearest_festival = category
                else:
                    # Any major festival
                    if category in self.major_festivals.keys():
                        if abs(i) < abs(min_distance):
                            min_distance = i
                            nearest_festival = category
        
        return min_distance if min_distance != float('inf') else None, nearest_festival
    
    def add_festival_features(self, df, date_column='date'):
        """
        Add festival-related features to a dataframe
        
        Args:
            df: DataFrame with date column
            date_column: Name of the date column
        
        Returns:
            DataFrame with added festival features
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Is it a holiday?
        df['is_holiday'] = df[date_column].apply(self.is_holiday)
        
        # Holiday name
        df['holiday_name'] = df[date_column].apply(self.get_holiday_name)
        
        # Festival category
        df['festival_category'] = df['holiday_name'].apply(self.get_festival_category)
        
        # Days to nearest major festival
        festival_data = df[date_column].apply(
            lambda x: self.days_to_nearest_festival(x)
        )
        df['days_to_festival'] = festival_data.apply(lambda x: x[0] if x[0] is not None else 0)
        df['nearest_festival'] = festival_data.apply(lambda x: x[1])
        
        # Pre-festival period (7 days before major festival)
        df['is_pre_festival'] = (df['days_to_festival'] > 0) & (df['days_to_festival'] <= 7)
        
        # Post-festival period (3 days after)
        df['is_post_festival'] = (df['days_to_festival'] < 0) & (df['days_to_festival'] >= -3)
        
        # Festival season (Diwali season: Sep-Nov, Christmas: Dec)
        df['month'] = df[date_column].dt.month
        df['is_diwali_season'] = df['month'].isin([9, 10, 11])
        df['is_christmas_season'] = df['month'].isin([12])
        
        return df
    
    def get_festival_impact_score(self, date):
        """
        Calculate a festival impact score (0-1) for a given date
        Higher score = higher expected sales impact
        """
        if isinstance(date, str):
            date = pd.to_datetime(date)
        
        score = 0.0
        
        # Base score if it's a holiday
        if self.is_holiday(date):
            holiday_name = self.get_holiday_name(date)
            category = self.get_festival_category(holiday_name)
            
            # Major festivals have higher impact
            if category == 'Diwali':
                score = 1.0
            elif category in ['Christmas', 'Eid', 'New Year']:
                score = 0.8
            elif category in ['Holi', 'Durga Puja']:
                score = 0.7
            else:
                score = 0.5
        
        # Pre-festival boost
        days_to, festival = self.days_to_nearest_festival(date)
        if days_to and 0 < days_to <= 7:
            # Closer to festival = higher impact
            pre_festival_score = 0.6 * (8 - days_to) / 7
            score = max(score, pre_festival_score)
        
        return score


# Convenience function
def get_calendar():
    """Get a singleton instance of the festival calendar"""
    return IndianFestivalCalendar()


# Example usage
if __name__ == '__main__':
    calendar = IndianFestivalCalendar()
    
    # Test with some dates
    test_dates = [
        '2024-10-31',  # Around Diwali
        '2024-12-25',  # Christmas
        '2024-03-25',  # Around Holi
        '2024-08-15',  # Independence Day
    ]
    
    print("Testing Indian Festival Calendar:")
    print("=" * 60)
    
    for date_str in test_dates:
        date = pd.to_datetime(date_str)
        is_holiday = calendar.is_holiday(date)
        holiday_name = calendar.get_holiday_name(date)
        days_to, nearest = calendar.days_to_nearest_festival(date)
        impact_score = calendar.get_festival_impact_score(date)
        
        print(f"\nDate: {date_str}")
        print(f"  Is Holiday: {is_holiday}")
        print(f"  Holiday Name: {holiday_name}")
        print(f"  Days to Festival: {days_to} ({nearest})")
        print(f"  Impact Score: {impact_score:.2f}")
