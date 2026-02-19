# app/utils/helpers.py
"""
Helper utility functions
Version: 1.0.0
"""
import uuid
from datetime import datetime, timedelta
import calendar
import hashlib
import json
from app.models import Settings
import pytz
import pandas as pd

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())[:8]

def generate_color_from_string(string):
    """Generate consistent color from string"""
    hash_object = hashlib.md5(string.encode())
    hex_digest = hash_object.hexdigest()
    return f"#{hex_digest[:6]}"

def get_date_range(period, reference_date=None):
    """Get start and end dates for a period"""
    if reference_date is None:
        reference_date = datetime.now()
    
    if period == 'today':
        start = datetime(reference_date.year, reference_date.month, reference_date.day)
        end = start + timedelta(days=1, seconds=-1)
    elif period == 'week':
        start = reference_date - timedelta(days=reference_date.weekday())
        start = datetime(start.year, start.month, start.day)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    elif period == 'month':
        start = datetime(reference_date.year, reference_date.month, 1)
        last_day = calendar.monthrange(reference_date.year, reference_date.month)[1]
        end = datetime(reference_date.year, reference_date.month, last_day, 23, 59, 59)
    elif period == 'year':
        start = datetime(reference_date.year, 1, 1)
        end = datetime(reference_date.year, 12, 31, 23, 59, 59)
    else:
        raise ValueError(f"Invalid period: {period}")
    
    return start, end

def format_timedelta(td):
    """Format timedelta to human readable string"""
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 and not parts:
        parts.append(f"{seconds}s")
    
    return ' '.join(parts) if parts else '0s'

def chunk_list(lst, chunk_size):
    """Split list into chunks"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def merge_dicts(dict1, dict2):
    """Merge two dictionaries recursively"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def parse_csv_line(line):
    """Parse CSV line handling quoted fields"""
    import csv
    from io import StringIO
    
    reader = csv.reader(StringIO(line))
    return next(reader)

def safe_divide(numerator, denominator, default=0):
    """Safe division with default value"""
    try:
        return numerator / denominator if denominator != 0 else default
    except:
        return default

def calculate_percentage(part, whole):
    """Calculate percentage"""
    return safe_divide(part * 100, whole, 0)

def get_user_timezone():
    """Get user's preferred timezone from settings"""
    try:
        timezone_str = Settings.get('timezone', 'local')
        if timezone_str == 'local' or not timezone_str:
            return None
        return pytz.timezone(timezone_str)
    except Exception as e:
        print(f"Error getting timezone: {e}")
        return None

def utc_to_local(utc_dt, timezone=None):
    """Convert UTC datetime to user's local timezone"""
    if not utc_dt:
        return utc_dt
    
    try:
        # Ensure datetime is timezone-aware (UTC)
        if isinstance(utc_dt, datetime):
            if utc_dt.tzinfo is None:
                utc_dt = pytz.UTC.localize(utc_dt)
        else:
            return utc_dt
        
        # Get user's timezone
        if timezone is None:
            timezone = get_user_timezone()
        
        if timezone:
            return utc_dt.astimezone(timezone)
        return utc_dt
    except Exception as e:
        print(f"Error converting UTC to local: {e}")
        return utc_dt

def local_to_utc(local_dt, timezone=None):
    """Convert local datetime to UTC for storage"""
    if not local_dt:
        return local_dt
    
    try:
        # Get user's timezone
        if timezone is None:
            timezone = get_user_timezone()
        
        # If datetime is naive, assume it's in user's timezone
        if isinstance(local_dt, datetime):
            if local_dt.tzinfo is None and timezone:
                local_dt = timezone.localize(local_dt)
            elif local_dt.tzinfo is None:
                # No timezone info, assume UTC
                local_dt = pytz.UTC.localize(local_dt)
        
        # Convert to UTC
        return local_dt.astimezone(pytz.UTC)
    except Exception as e:
        print(f"Error converting local to UTC: {e}")
        return local_dt

def get_current_utc_time():
    """Get current time in UTC"""
    return datetime.now(pytz.UTC)

def get_current_local_time():
    """Get current time in user's local timezone"""
    utc_now = get_current_utc_time()
    local_tz = get_user_timezone()
    if local_tz:
        return utc_now.astimezone(local_tz)
    return utc_now

def format_datetime_for_api(dt):
    """Format datetime for API response (ISO format with timezone)"""
    if not dt:
        return None
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        return dt.isoformat()
    return str(dt)

def parse_date_from_request(date_str, end_of_day=False):
    """Parse date from request string and convert to UTC for storage"""
    if not date_str:
        return None
    
    try:
        # Handle different input types
        if isinstance(date_str, datetime):
            dt = date_str
        else:
            # Convert to string if it's not already
            date_str = str(date_str)
            
            # Remove any timezone indicators that might cause issues
            date_str = date_str.replace('Z', '+00:00')
            
            # Handle different date formats
            try:
                # Try parsing as full ISO format first
                dt = datetime.fromisoformat(date_str)
            except ValueError:
                # If that fails, try common formats
                if len(date_str) == 10 and date_str.count('-') == 2:
                    # YYYY-MM-DD format
                    year, month, day = map(int, date_str.split('-'))
                    dt = datetime(year, month, day)
                elif len(date_str) == 10 and date_str.count('/') == 2:
                    # MM/DD/YYYY or DD/MM/YYYY format
                    parts = date_str.split('/')
                    if len(parts) == 3:
                        # Assume YYYY-MM-DD for simplicity
                        # In a real app, you'd use user preferences here
                        if len(parts[2]) == 4:  # Assuming year is last
                            year = int(parts[2])
                            month = int(parts[0])
                            day = int(parts[1])
                            dt = datetime(year, month, day)
                        else:
                            raise ValueError(f"Unrecognized date format: {date_str}")
                else:
                    # Try pandas to_datetime as fallback
                    import pandas as pd
                    dt = pd.to_datetime(date_str).to_pydatetime()
        
        # Ensure we have a datetime object
        if not isinstance(dt, datetime):
            raise ValueError(f"Could not parse date: {date_str}")
        
        # If it's just a date (no time component), add appropriate time
        if dt.hour == 0 and dt.minute == 0 and dt.second == 0 and dt.microsecond == 0:
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            # else keep as start of day (already 00:00:00)
        
        # Assume the date is in user's local timezone and convert to UTC
        return local_to_utc(dt)
        
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None