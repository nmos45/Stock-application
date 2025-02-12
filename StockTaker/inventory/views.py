from django.shortcuts import render
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import StockInstance, StockFood, Food
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

class StockInstanceListView(LoginRequiredMixin, generic.ListView):
    """class-based list view for StockInstances"""
    model = StockInstance
    
    def get_queryset(self):
        """Overiding the query for StockInstanceListView"""
        return StockInstance.objects.filter(user=self.request.user)
    

class StockInstanceDetailView(LoginRequiredMixin, generic.DetailView):
    """class-based detail view for specific StockInstance"""
    model = StockInstance

    def get_object(self,queryset=None):
        """Overide get_object to verify logged in user created stockInstance"""
        stockinstance_obj  = super().get_object(queryset)
        if stockinstance_obj.user != self.request.user:
            raise PermissionDenied("You are not authorized to access this inventory")
        return stockinstance_obj

class StockInstanceCreate(LoginRequiredMixin, CreateView):
    """generic-edit view to create a StockInstance using forms"""
    model=StockInstance
    fields = ['user','name']

    def get_form(self,form_class=None):
        """Overiding get_form to initialise form valuer"""
        form = super().get_form(form_class)
        form.fields['user'].initial = self.request.user
        form.fields['user'].disabled = True
        return form

class StockInstanceUpdate(LoginRequiredMixin, UpdateView):
    """generic-edit view to update a StockInstance using forms"""
    model=StockInstance
    fields = ['user','name']

    def get_object(self,queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockInstance_obj = super().get_object(queryset)
        if StockInstance_obj.user != self.request.user:
            raise PermissionDenied("You are not authorized to delete this StockInstance")
        return stockFood_obj

class StockInstanceDelete(LoginRequiredMixin, DeleteView):
    """generic-edit view to delete a StockInstance using forms"""
    model=StockInstance
    success_url = reverse_lazy('homepage')   

    def get_object(self,queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockInstance_obj = super().get_object(queryset)
        if StockInstance_obj.user != self.request.user:
            raise PermissionDenied("You are not authorized to delete this StockInstance")
        return StockInstance_obj



class StockFoodDetail(LoginRequiredMixin, generic.DetailView):
    """class-based detail view to display specific StockFood instance"""
    model=StockFood

    def get_object(self,queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockFood_obj = super().get_object(queryset)
        if StockFood_obj.stock_instance.user != self.request.user:
            raise PermissionDenied("You are not authorized to access this stockfood")
        return StockFood_obj

class StockFoodCreate(LoginRequiredMixin, CreateView):
    """generic-edit view to create a stockfood instance using forms"""
    model=StockFood 
    fields=['stock_instance','food','quantity','expiry_date']

    def get_form(self,form_class=None):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(form_class)
        
        form.fields['stock_instance'].initial = self.kwargs.get('pk')
        form.fields['stock_instance'].disabled = True
        return form

class StockFoodUpdate(LoginRequiredMixin, UpdateView):
    """generic-edit view to update a StockFood instance using forms"""
    model=StockFood 
    fields=['stock_instance','food','quantity','expiry_date']

    def get_object(self,queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockFood_obj = super().get_object(queryset)
        if StockFood_obj.stock_instance.user != self.request.user:
            raise PermissionDenied("You are not authorized to change this stockfood")
        return StockFood_obj


class StockFoodDelete(LoginRequiredMixin, DeleteView):
    """generic-edit view to delete a StockFood using forms"""
    model=StockFood
    success_url = reverse_lazy('')

    def get_success_url(self):
        stockinstance = self.object.stock_instance 
        return reverse('stockInstance-detail', kwargs={'pk':stockinstance.id})

    def get_object(self,queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockFood_obj = super().get_object(queryset)
        if StockFood_obj.stock_instance.user != self.request.user:
            raise PermissionDenied("You are not authorized to delete this stockfood")
        return StockFood_obj


class FoodListView(generic.ListView):
    """class-based list view for Food objects"""
    model = Food
    
    def get_queryset(self):
        """Overiding queryset for search result"""
        query = self.request.GET.get('q')
        if query:
            object_list = Food.objects.filter(
                Q(name__icontains=query) |
                Q(category__category_type__icontains=query)
        ).distinct()
            return object_list
        return Food.objects.all()
    

class FoodDetailView(generic.DetailView):
    """class-based detail view for specific Food instance"""
    model=Food



class FoodCreate(LoginRequiredMixin, CreateView):
    """generic-edit view to create a food instance using forms"""
    model=Food
    fields = ['user','name','category','shelf_life']

    def get_form(self,form_class=None):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(form_class)
        form.fields['user'].initial = self.request.user # set user to the logged in user instance
        form.fields['user'].disabled = True     # Prevent user from selecting other user
        return form


class FoodUpdate(LoginRequiredMixin, generic.UpdateView):
    """generic-edit view to update a Food instance using forms"""
    model=Food
    fields = ['user','name','category','shelf_life']

    def get_object(self, queryset=None):
        """Overide get_object to verify logged in user created Food"""
        food_obj = super().get_object(queryset)
        if food_obj.user != self.request.user:
            raise PermissionDenied('You are not authorized to update this food')
        return food_obj

    def get_form(self,form_class=None):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(form_class)
        form.fields['user'].disabled = True     
        return form

class FoodDelete(LoginRequiredMixin,generic.DeleteView):
    """generic-edit view to delete a Food instance using forms"""
    model=Food
    success_url = reverse_lazy('all-foods')

    def get_object(self, queryset=None):
        """Overide get_object to verify logged in user created Food"""
        food_obj = super().get_object(queryset)
        if food_obj.user != self.request.user:
            raise PermissionDenied('You are not authorized to delete this food')
        return food_obj



