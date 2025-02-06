from django.contrib import admin
from .models import Food, Category, StockInstance, StockFood, Recipe

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    """Admin model class for Food model object"""
    list_display =  ('name','display_category','shelf_life')
    list_filter = ('category', 'shelf_life')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin model class for Food model object"""
    list_display =('category_type', 'description') 

class StockFoodInline(admin.TabularInline):
    """Inline model to display all stockFoods related to a StockInstance"""
    model = StockFood
    extra = 0


@admin.register(StockInstance)
class StockInstanceAdmin(admin.ModelAdmin):
    """Admin model class for StockInstance model object"""
    list_display = ('user','name')
    inlines = [StockFoodInline]

@admin.register(StockFood)
class StockFoodAdmin(admin.ModelAdmin):
    """Admin model class for StockFood model object"""
    list_display = ('stock_instance','food','quantity')
    list_filter = ('stock_instance',)
    fieldsets = (
        (None,{
            'fields': ('stock_instance',)
        }),

        (None,{
            'fields': ('food','quantity','expiry_date')
        })
    )

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin model class for Recipe moodel object"""
    list_display = ('user','name')
    list_filter = ('user',)
    fieldsets = (
        ('Overview',{
            'fields': ('user','name')
        }),
        ('Type',{
            'fields': ('ingredients','category')
        }),
        ('Details',{
            'fields':('portion_size','portion_quantity','instructions')
        })
    )
