from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError
import datetime
from dateutil.relativedelta import relativedelta


def pluralize(word, number):
    """String method version of django pluralize template feature"""
    if number == 1:
        return word
    return word + "s"


def days_to_string(days):
    """Convert total days back into a readable time format"""
    reference_date = datetime.datetime(
        2017, 1, 1)  # Same reference date used in get_prep_value
    target_date = reference_date + \
        timedelta(days=days)  # Calculate target date

    diff = relativedelta(target_date, reference_date)

    years = diff.years
    months = diff.months
    weeks = (diff.days // 7)
    days = diff.days % 7

    result = []
    if years > 0:
        result.append(f"{years} {pluralize('year', years)}")
    if months > 0:
        result.append(f"{months} {pluralize('month', months)}")
    if weeks > 0:
        result.append(f"{weeks} {pluralize('week', weeks)}")
    if days > 0:
        result.append(f"{days} {pluralize('day', days)}")

    return ", ".join(result) if result else "0 days"


def string_to_days(value):
    """Coverts string representation to microsecond value"""
    if not value:
        # For use outside of already validated data values
        raise ValidationError("Invalid input for conversion to days.")

    return TimeFrameField(max_length=35).get_prep_value(value)


class TimeFrameField(models.CharField):
    description = "a string field to represent a period of time either (years, months, weeks, days)"

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 35  # max lifespan multiple years
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        """specifing field data type for database"""
        return 'bigint unsigned not null'

    def get_prep_value(self, value):
        """converting string to value appropriate for db insertion"""
        if value is None:
            return None

        times = value.split(', ')
        total = datetime.datetime(2017, 1, 1)
        for time in times:
            time = time.split()

            if len(time) != 2:
                raise ValidationError(
                    'number and timeframe must be seperated by a single space')

            try:
                num = int(time[0])
            except ValueError:
                raise ValidationError('must have an numeric date')

            if num < 0:
                raise ValidationError("value must be greater than 0")

            timeframe = time[1].lower()
            if timeframe == 'day' or timeframe == 'days':
                total += timedelta(days=num)

            elif timeframe == 'week' or timeframe == 'weeks':
                total += timedelta(weeks=num)

            elif timeframe == 'month' or timeframe == 'months':
                total += relativedelta(months=num)
            elif timeframe == 'year' or timeframe == 'years':
                total += relativedelta(years=num)

            else:
                raise ValidationError(
                    'timeframe must be days/weeks/months/years')
        total -= datetime.datetime(2017, 1, 1)
        total = total.days
        return total

    def from_db_value(self, value, expression, connection):
        """Converting db inserted values to TimeFrameField objects"""
        if value is None:
            return None

        return days_to_string(value)
