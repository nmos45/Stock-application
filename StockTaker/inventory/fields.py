from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError

def pluralize(word,number):
    """String method version of django pluralize template feature"""
    if number ==1:
        return word
    return word +"s"

def microseconds_to_date(m_seconds):
    """string representation of a microsecond value in years, months, weeks, days"""
    years = int(m_seconds // 3.154e13)
    remaining_ms = m_seconds % 3.154e13

    months = int((remaining_ms) // 2.628e12)
    remaining_ms %= 2.628e12
    
    weeks = int((remaining_ms) // 6.048e11)
    remaining_ms %= 6.048e11

    days = int((remaining_ms) // 8.64e10)

    return f"{years} {pluralize('Year',years)}, {months} {pluralize('Month',months)}, {weeks} {pluralize('Week',weeks)}, {days} {pluralize('Day',days)}"






class TimeFrameField(models.CharField):
    description= "A string field to represent a period of time either (years, months, weeks, days)"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10 # max lifespan multiple years
        super().__init__(*args, **kwargs)

    def db_type(self,connection):
        """Specifing field data type for database"""
        return 'BIGINT UNSIGNED NOT NULL'

    def get_prep_value(self,value):
        """Converting string to value appropriate for db insertion"""
        if value is None:
            return None
         
        time = value.split()

        if len(time) !=2:
            raise ValidationError('number and timeframe must be seperated by a single space')

        try:
            num = int(time[0])
        except ValueError:
            raise ValidationError('Must have an numeric date')

        if num < 0:
            raise ValidationError("value must be greater than 0")

        timeframe = time[1].lower()
        if timeframe == 'day' or timeframe =='days':
            return timedelta(days=num).total_seconds() * 1e6

        if timeframe  == 'week' or timeframe =='weeks':
            return timedelta(weeks=num).total_seconds() * 1e6

        if timeframe == 'month' or timeframe =='months':
            return timedelta(weeks=num*4).total_seconds() * 1e6

        if timeframe == 'year' or timeframe =='years':
            return timedelta(days=num*365).total_seconds() * 1e6 

        raise ValidationError('timeframe must be days/weeks/months/years')

    def from_db_value(self, value, expression, connection):
        """Converting db inserted values to TimeFrameField objects"""
        if value is None:
            return None
        
        return microseconds_to_date(value)
    
    def string_to_microseconds(self,value):
        """Coverts string representation to microsecond value"""
        if not value:
            raise ValidationError("Invalid input for conversion to microseconds.")

        dates = value.split(", ")
        total_microseconds = 0
        for date in dates:
            total_microseconds += self.get_prep_value(date)
        return total_microseconds

