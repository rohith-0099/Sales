"""
Indian Holidays Module
Provides functionality to detect and tag Indian festivals and holidays.
"""

from datetime import datetime, timedelta

import holidays
import pandas as pd


DEFAULT_NO_FESTIVAL_DISTANCE = 61


class IndianFestivalCalendar:
    """
    Manages Indian festival dates and their impact on sales.
    """

    def __init__(self):
        self.holidays = None
        self._loaded_start_year = None
        self._loaded_end_year = None

        current_year = datetime.now().year
        self._ensure_year_range(current_year - 5, current_year + 5)

        self.major_festivals = {
            "Diwali": ["Diwali", "Deepavali"],
            "Holi": ["Holi"],
            "Eid": ["Eid al-Fitr", "Eid al-Adha", "Id-ul-Fitr", "Id-ul-Zuha"],
            "Christmas": ["Christmas"],
            "New Year": ["New Year"],
            "Durga Puja": ["Dussehra", "Durga Puja"],
            "Raksha Bandhan": ["Raksha Bandhan"],
            "Onam": ["Onam"],
            "Pongal": ["Pongal"],
            "Republic Day": ["Republic Day"],
            "Independence Day": ["Independence Day"],
        }

    def _build_holidays(self, start_year, end_year):
        return holidays.India(years=range(start_year, end_year + 1))

    def _ensure_year_range(self, start_year, end_year):
        if self.holidays is None:
            self.holidays = self._build_holidays(start_year, end_year)
            self._loaded_start_year = start_year
            self._loaded_end_year = end_year
            return

        if start_year >= self._loaded_start_year and end_year <= self._loaded_end_year:
            return

        merged_start = min(start_year, self._loaded_start_year)
        merged_end = max(end_year, self._loaded_end_year)
        self.holidays = self._build_holidays(merged_start, merged_end)
        self._loaded_start_year = merged_start
        self._loaded_end_year = merged_end

    def _ensure_date_coverage(self, date, lookaround_days=0):
        if isinstance(date, str):
            date = pd.to_datetime(date)
        start_date = date - timedelta(days=lookaround_days)
        end_date = date + timedelta(days=lookaround_days)
        self._ensure_year_range(start_date.year, end_date.year)
        return date

    def is_holiday(self, date):
        date = self._ensure_date_coverage(date)
        return date in self.holidays

    def get_holiday_name(self, date):
        date = self._ensure_date_coverage(date)
        return self.holidays.get(date, None)

    def get_festival_category(self, holiday_name):
        if holiday_name is None or pd.isna(holiday_name) or not str(holiday_name).strip():
            return None

        holiday_name = str(holiday_name)
        for category, keywords in self.major_festivals.items():
            for keyword in keywords:
                if keyword.lower() in holiday_name.lower():
                    return category
        return "Other"

    def days_to_nearest_festival(self, date, festival_name=None):
        date = self._ensure_date_coverage(date, lookaround_days=60)

        search_range = 60
        min_distance = float("inf")
        nearest_festival = None

        for offset in range(-search_range, search_range + 1):
            check_date = date + timedelta(days=offset)
            if check_date in self.holidays:
                holiday_name = self.holidays[check_date]
                category = self.get_festival_category(holiday_name)

                if festival_name:
                    if category == festival_name and abs(offset) < abs(min_distance):
                        min_distance = offset
                        nearest_festival = category
                elif category in self.major_festivals.keys() and abs(offset) < abs(min_distance):
                    min_distance = offset
                    nearest_festival = category

        if min_distance == float("inf"):
            return DEFAULT_NO_FESTIVAL_DISTANCE, None
        return min_distance, nearest_festival

    def add_festival_features(self, df, date_column="date"):
        featured_df = df.copy()
        featured_df[date_column] = pd.to_datetime(featured_df[date_column])

        featured_df["is_holiday"] = featured_df[date_column].apply(self.is_holiday)
        featured_df["holiday_name"] = featured_df[date_column].apply(self.get_holiday_name)
        featured_df["festival_category"] = featured_df["holiday_name"].apply(self.get_festival_category)

        festival_data = featured_df[date_column].apply(lambda value: self.days_to_nearest_festival(value))
        featured_df["days_to_festival"] = festival_data.apply(lambda value: value[0])
        featured_df["nearest_festival"] = festival_data.apply(lambda value: value[1])

        featured_df["is_pre_festival"] = (
            (featured_df["nearest_festival"].notna())
            & (featured_df["days_to_festival"] > 0)
            & (featured_df["days_to_festival"] <= 7)
        )
        featured_df["is_post_festival"] = (
            (featured_df["nearest_festival"].notna())
            & (featured_df["days_to_festival"] < 0)
            & (featured_df["days_to_festival"] >= -3)
        )

        featured_df["month"] = featured_df[date_column].dt.month
        featured_df["is_diwali_season"] = featured_df["month"].isin([9, 10, 11])
        featured_df["is_christmas_season"] = featured_df["month"].isin([12])

        return featured_df

    def get_festival_impact_score(self, date):
        date = self._ensure_date_coverage(date, lookaround_days=60)
        score = 0.0

        if self.is_holiday(date):
            holiday_name = self.get_holiday_name(date)
            category = self.get_festival_category(holiday_name)

            if category == "Diwali":
                score = 1.0
            elif category in ["Christmas", "Eid", "New Year"]:
                score = 0.8
            elif category in ["Holi", "Durga Puja"]:
                score = 0.7
            else:
                score = 0.5

        days_to, _festival = self.days_to_nearest_festival(date)
        if days_to is not None and 0 < days_to <= 7:
            pre_festival_score = 0.6 * (8 - days_to) / 7
            score = max(score, pre_festival_score)

        return score


def get_calendar():
    """Get a singleton instance of the festival calendar."""
    return IndianFestivalCalendar()


if __name__ == "__main__":
    calendar = IndianFestivalCalendar()
    test_dates = [
        "2024-10-31",
        "2024-12-25",
        "2024-03-25",
        "2024-08-15",
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
