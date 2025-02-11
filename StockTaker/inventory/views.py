from django.shortcuts import render
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import StockInstance, StockFood, Food
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import Http404

class StockInstanceListView(LoginRequiredMixin, generic.ListView):
    """class-based list view for StockInstances"""
    model = StockInstance
    
    def get_queryset(self):
        """Overiding the query for StockInstanceListView"""
        return StockInstance.objects.filter(user=self.request.user)

class StockInstanceDetailView(generic.DetailView):
    """class-based detail view for specific StockInstance"""
    model = StockInstance

class StockInstanceCreate(LoginRequiredMixin, CreateView):
    """generic-edit view to create a StockInstance using forms"""
    model=StockInstance
    fields = ['user','name']

class StockInstanceUpdate(LoginRequiredMixin, UpdateView):
    """generic-edit view to update a StockInstance using forms"""
    model=StockInstance
    fields = ['user','name']

class StockInstanceDelete(LoginRequiredMixin, DeleteView):
    """generic-edit view to delete a StockInstance using forms"""
    model=StockInstance
    success_url = reverse_lazy('homepage')   


class StockFoodDetail(LoginRequiredMixin, generic.DetailView):
    """class-based detail view to display specific StockFood instance"""
    model=StockFood

class StockFoodCreate(LoginRequiredMixin, CreateView):
    """generic-edit view to create a stockfood instance using forms"""
    model=StockFood 
    fields=['stock_instance','food','quantity','expiry_date']
    #
    # def get_initial(self):
    #     """Set initial field values in form"""
    #     initial = super().get_initial()
    #     stock_instance_id = self.kwargs.get('pk')
    #     if stock_instance_id:
    #         initial['stock_instance'] = stock_instance_id
    #     return initial
    #
    # def get_form(self,form_class=None):
    #     """Overiding get_form to modify the forms fields"""
    #     form = super().get_form(form_class)
    #     # form.fields['stock_instance'].initial = self.kwargs.get('pk')
    #     form.fields['stock_instance'].disabled = True

class StockFoodUpdate(LoginRequiredMixin, UpdateView):
    """generic-edit view to update a StockFood instance using forms"""
    model=StockFood 
    fields=['stock_instance','food','quantity','expiry_date']


class StockFoodDelete(LoginRequiredMixin, DeleteView):
    """generic-edit view to delete a StockFood using forms"""
    model=StockFood
    success_url = reverse_lazy('')

    def get_success_url(self):
        stockinstance = self.object.stock_instance 
        return reverse('stockInstance-detail', kwargs={'pk':stockinstance.id})

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

    def get_form(self, *args, **kwargs):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(*args,**kwargs)
        form.fields['user'].initial = self.request.user # set user to the logged in user instance
        form.fields['user'].disabled = True     # Prevent user from selecting other user
        return form


class FoodUpdate(LoginRequiredMixin, generic.UpdateView):
    """generic-edit view to update a Food instance using forms"""
    model=Food
    fields = ['user','name','category','shelf_life']

    def get_object(self, queryset=None):
        """Overide get_object to verify loggedin user created Food"""
        food_obj = super().get_object(queryset)
        if food_obj.user != self.request.user:
            raise Http404('You are not authorized to update this food')
        return food_obj

    def get_form(self, *args, **kwargs):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(*args,**kwargs)
        form.fields['user'].disabled = True     
        return form
