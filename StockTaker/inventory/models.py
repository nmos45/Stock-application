from django.db import models
from django.db.models import CharField,ManyToManyField,DurationField
from .fields import TimeFrameField,microseconds_to_date, pluralize
from django.core.exceptions import ValidationError
from datetime import timedelta


class Food(models.Model):
    """Model representing a specific food item"""
    name = CharField(max_length=200)
    category = ManyToManyField('Category',help_text="Enter the foods category e.g(milk)")
    shelf_life = TimeFrameField(help_text="Enter the number and timeframe (days/weeks/months/years), e.g. 4 weeks")

class Category(models.Model):
    pass
