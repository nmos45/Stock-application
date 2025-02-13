from django.db import models
from django.db.models import CharField,ManyToManyField,DurationField,ForeignKey,BigIntegerField,PositiveSmallIntegerField,DateTimeField,TextField,BooleanField
from .fields import TimeFrameField, pluralize, string_to_days
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.db.models.functions import Lower
from django.contrib.auth.models import User
from django.urls import reverse


class Food(models.Model):
    """Model representing a specific food item"""
    user = ForeignKey(User,on_delete=models.SET_NULL,null=True,db_index=True)
    name = CharField(max_length=200)
    category = ManyToManyField('Category',help_text="Enter the foods category e.g(milk)")
    shelf_life = TimeFrameField(help_text='Enter the number and timeframe (days/weeks/months/years), e.g. 4 weeks')
    verified = BooleanField(null=True)
    
    def __str__(self):
        """String representation of a food object"""
        return self.name
           
    def get_absolute_url(self):
        """returns url for particular Food instance"""
        return reverse('food-detail',args=[str(self.id)])

    def display_category(self):
        """creating a string for category as ManyToManyField cost in admin model list_display"""
        return ', '.join(category.category_type for category in self.category.all() )
    display_category.short_description = 'Categories' # default description for category fields in admin



class Category(models.Model):
    """Model representing food categories"""
    category_type = CharField(max_length=200,unique=True,help_text='Enter the category type e.g (keto,vegan)',db_index=True)
    description = TextField(help_text='Enter summary on category type: e.g(vegan: health benefits, environmental impact)')

    def __str__(self):
        """String representation of a Category object"""
        return self.category_type
    
    def get_absolute_url(self):
        """returns the url to access a particular Category instance"""
        return reverse('category-detail', args= [str(self.id)] )

    class Meta:
        constraints= [
        UniqueConstraint(
                Lower('category_type'),
                name = 'Category_category_type_case_insensitive_unique',
                violation_error_message="Category already exsists (case insensitive match)"
                      ),
        ]
       
class StockFood(models.Model):
    """Model representing a StockInstance Food object"""
    stock_instance = ForeignKey('StockInstance',on_delete=models.CASCADE,db_index=True)
    food = ForeignKey(Food,on_delete=models.CASCADE)
    quantity = PositiveSmallIntegerField(default=1)
    added_date = DateTimeField(auto_now_add=True) #remember to exclude in forms
    expiry_date = DateTimeField(help_text='Enter the expiry date (optional)',blank=True,null=True)

    def __str__(self):
        """String representation of a stockFood"""
        return self.food.name

    def get_absolute_url(self):
        """returns the url to access a particular StockFood instance"""
        return reverse('stockFood-detail', args=[ str(self.id)] )

    def save(self, *args, **kwargs):
        """Save method overided to calculate expiry_date"""
        super().save(*args,**kwargs)
        if self.expiry_date is None:
            shelf_life_days = string_to_days(self.food.shelf_life)
            shelf_life_timedelta = timedelta(days=shelf_life_days)
            self.expiry_date = self.added_date + shelf_life_timedelta
            super().save(update_fields=['expiry_date']) # optimised query to just save()
        self.update_food_verification(self.food)
       
    def delete(self,*args,**kwargs):
        """Overiding delete method to update food field"""
        food_instance = self.food
        super().delete(*args,**kwargs)
        self.update_food_verification(food_instance)

    @staticmethod
    def update_food_verification(food_instance):
        """method to update the verification status of a food instance specified in StockFood instance"""
        count = StockFood.objects.filter(food=food_instance).count()
        if count >= 10 and not food_instance.verified: 
            food_instance.verified = True
            food_instance.save(update_fields=['verified'])

        elif count<10 and food_instance.verified:
            food_instance.verified = False
            food_instance.save(update_fields=['verified'])

class StockInstance(models.Model):
    """Model representing a specific users stock"""
    user = ForeignKey(User,on_delete=models.CASCADE,db_index=True)
    name = CharField(max_length=200,default= 'stockroom')
    
    def __str__(self):
        """String representation of a stockInstance object"""
        return self.name

    def get_absolute_url(self):
        """returns the url to access a particular stockInstance object"""
        return reverse('stockInstance-detail', args=[str(self.id)] )

    @property
    def num_items(self):
        """returns the number of StockFood objects associated with stockInstance"""
        num = 0
        query = stockFood.objects.all().filter(stock_instance_id=self.id)
        if query:
            for food in query:
                num += food.quantity
        return num
        
    def save(self, *args, **kwargs):
        """Overiding save method to produce a customised default StockInstance name"""
        super().save(*args, **kwargs)
        if self.name == 'stockroom':
            self.name = self.user.username + " stockroom"
            super().save(update_fields=['name'])
   
class Recipe(models.Model):
    """Model representing a Recipe object"""
    user = ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    name = CharField(max_length=200)
    ingredients = ManyToManyField(Food, help_text='Enter the recipes ingredients')
    category = ManyToManyField(Category, help_text='Enter the dietary category e.g Vegan, Gluten Free') 
    serving_sizes = (
        ('g','grams'),
        ('kg','kilograms'),
        ('oz', 'ounces'),
        ('ml', 'milliliters')
    )
    portion_size = CharField(max_length=2,
                             choices=serving_sizes,
                             blank=True,
                             default='g',
                             help_text='Enter the measurement for portion of recipe')
    portion_quantity = PositiveSmallIntegerField(default=250)
    instructions = TextField(help_text='Enter a clear concise method for making this recipe.')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        """String representation of a Recipe object"""
        return self.name
    
    def get_absolute_url(self):
        """returns a url to access a particular Recipe instance"""
        return reverse('recipe-detail', args =[str(self.id)] )


