from django import forms
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import StockInstance, StockFood, Food, Recipe
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.db.models import Prefetch
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.utils import timezone
from decouple import config
import requests


class StockInstanceListView(LoginRequiredMixin, generic.ListView):
    """class-based list view for StockInstances"""
    model = StockInstance

    def get_queryset(self):
        """Overiding the query for StockInstanceListView"""
        return StockInstance.objects.filter(user=self.request.user)


class StockInstanceDetailView(LoginRequiredMixin, generic.DetailView):
    """class-based detail view for specific StockInstance"""
    model = StockInstance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        foods = StockFood.objects.filter(
            stock_instance=self.kwargs['pk']).distinct()

        # filtering foods
        food_type = self.request.GET.get('q')
        filter = self.request.GET.get('filter')
        if food_type:
            print(f"food type is {food_type}")
            id = Q(stock_instance=self.kwargs['pk'])
            name_category = Q(food__name__icontains=food_type) | Q(
                food__category__category_type__icontains=food_type)
            filtered_foods = StockFood.objects.filter(
                Q(id & name_category)
            ).distinct()
            foods = filtered_foods
        if filter:
            foods = foods.filter(expiry_date__lt=timezone.now())
        # paginate
        paginator = Paginator(foods, 8)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context

    def get_object(self, queryset=None):
        """Overide get_object to verify logged in user created stockInstance"""
        stockinstance_obj = super().get_object(queryset)
        if stockinstance_obj.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to access this inventory")
        return stockinstance_obj


class StockInstanceCreate(LoginRequiredMixin, CreateView):
    """generic-edit view to create a StockInstance using forms"""
    model = StockInstance
    fields = ['user', 'name']

    def get_form(self, form_class=None):
        """Overiding get_form to initialise form valuer"""
        form = super().get_form(form_class)
        form.fields['user'].initial = self.request.user
        form.fields['user'].widget = forms.HiddenInput()
        return form


class StockInstanceUpdate(LoginRequiredMixin, UpdateView):
    """generic-edit view to update a StockInstance using forms"""
    model = StockInstance
    fields = ['user', 'name']

    def get_object(self, queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockInstance_obj = super().get_object(queryset)
        if StockInstance_obj.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to delete this StockInstance")
        return StockInstance_obj


class StockInstanceDelete(LoginRequiredMixin, DeleteView):
    """generic-edit view to delete a StockInstance using forms"""
    model = StockInstance
    success_url = reverse_lazy('homepage')

    def get_object(self, queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockInstance_obj = super().get_object(queryset)
        if StockInstance_obj.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to delete this StockInstance")
        return StockInstance_obj


class StockFoodDetail(LoginRequiredMixin, generic.DetailView):
    """class-based detail view to display specific StockFood instance"""
    model = StockFood

    def get_object(self, queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockFood_obj = super().get_object(queryset)
        if StockFood_obj.stock_instance.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to access this stockfood")
        return StockFood_obj


class StockFoodForm(forms.ModelForm):
    food_display = forms.CharField(label="Food", disabled=True, required=False)

    class Meta:
        model = StockFood
        fields = ['food', 'quantity', 'expiry_date']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-select form-control'}),
        }


class StockFoodCreate(LoginRequiredMixin, CreateView):
    """generic-edit view to create a stockfood instance using forms"""
    model = StockFood
    form_class = StockFoodForm

    def get_object(self, queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockFood_obj = super().get_object(queryset)
        if StockFood_obj.stock_instance.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to change this stockfood")
        return StockFood_obj

    def get_form(self, form_class=None):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(form_class)
        request_stock_instance = StockInstance.objects.get(
            id=self.kwargs['pk'])
        form.instance.stock_instance = request_stock_instance

        if self.request.GET.get('food'):
            food = Food.objects.get(
                id=self.request.GET.get('food')
            )
            form.initial['food'] = food
            # form.fields['food'].widget = forms.HiddenInput()
            # form.initial['food_display'] = str(food)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instance'] = self.kwargs['pk']
        return context


class StockFoodUpdate(LoginRequiredMixin, UpdateView):
    """generic-edit view to update a StockFood instance using forms"""
    model = StockFood
    form_class = StockFoodForm

    def get_object(self, queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockFood_obj = super().get_object(queryset)
        if StockFood_obj.stock_instance.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to change this stockfood")
        return StockFood_obj

    def get_form(self, form_class=None):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(form_class)
        form.initial['food_display'] = str(self.get_object().food)
        if self.request.GET.get('food'):
            food = Food.objects.get(
                id=self.request.GET.get('food')
            )
            form.initial['food'] = food
            form.initial['food_display'] = str(food)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object()
        context['instance'] = object.stock_instance.id
        return context


class StockFoodDelete(LoginRequiredMixin, DeleteView):
    """generic-edit view to delete a StockFood using forms"""
    model = StockFood
    success_url = reverse_lazy('')

    def get_success_url(self):
        stockinstance = self.object.stock_instance
        return reverse('stockInstance-detail', kwargs={'pk': stockinstance.id})

    def get_object(self, queryset=None):
        """Overiding get_object method to prevent unauthorized access"""
        StockFood_obj = super().get_object(queryset)
        if StockFood_obj.stock_instance.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to delete this stockfood")
        return StockFood_obj


class FoodListView(generic.ListView):
    """class-based list view for Food objects"""
    model = Food
    paginate_by = 12

    def get_queryset(self):
        """Overiding queryset for search result"""
        query = self.request.GET.get('q')
        if query:
            print(query)
            object_list = Food.objects.filter(
                Q(name__icontains=query) |
                Q(category__category_type__icontains=query)
            ).distinct()
            return object_list
        return Food.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['instance'] = self.kwargs['pk']
        context['next'] = self.request.GET.get('next')
        return context


class FoodDetailView(generic.DetailView):
    """class-based detail view for specific Food instance"""
    model = Food


class FoodForm(forms.ModelForm):

    class Meta:
        model = Food
        fields = ['user', 'name', 'category', 'shelf_life']
        widgets = {
            'user': forms.HiddenInput(),
            'category': forms.SelectMultiple(attrs={'class': 'form-select form-control'}),
        }


class FoodCreate(LoginRequiredMixin, CreateView):
    """generic-edit view to create a food instance using forms"""
    model = Food
    form_class = FoodForm

    def get_form(self, form_class=None):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(form_class)
        form.fields['user'].initial = self.request.user
        form.fields['category'].help_text = None
        return form

    def form_valid(self, form):
        """Overiding form_valid to save food image url"""
        form_response = super().form_valid(form)
        obj = form.instance
        food = obj.name
        headers = {
            'Authorization': config('UNSPLASH_API_KEY')
        }
        params = {
            'query': food,
            'per_page': 1,
        }
        response = requests.get(
            'https://api.unsplash.com/search/photos', headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            url = data['results'][0]['urls']['raw']
            if url:
                obj.image = url
                obj.save()
        return form_response


class FoodUpdate(LoginRequiredMixin, generic.UpdateView):
    """generic-edit view to update a Food instance using forms"""
    model = Food
    fields = ['user', 'name', 'category', 'shelf_life']

    def get_object(self, queryset=None):
        """Overide get_object to verify logged in user created Food"""
        food_obj = super().get_object(queryset)
        if food_obj.user != self.request.user:
            raise PermissionDenied(
                'You are not authorized to update this food')
        return food_obj

    def get_form(self, form_class=None):
        """Overiding get_form to modify the forms fields"""
        form = super().get_form(form_class)
        form.fields['user'].disabled = True
        return form

    def form_valid(self, form):
        """Overiding form_valid to save food image url"""
        form_response = super().form_valid(form)
        obj = form.instance
        food = obj.name
        headers = {
            'Authorization': 'Client-ID DV_wK_AsntKhoszARoxfujWnAN6ABcgsspgCEBlqgI0'
        }
        params = {
            'query': food,
            'per_page': 1,
        }
        response = requests.get(
            'https://api.unsplash.com/search/photos', headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            url = data['results'][0]['urls']['raw']
            if url:
                obj.image = url
                obj.save()
        return form_response


class FoodDelete(LoginRequiredMixin, generic.DeleteView):
    """generic-edit view to delete a Food instance using forms"""
    model = Food
    success_url = reverse_lazy('all-foods')

    def get_object(self, queryset=None):
        """Overide get_object to verify logged in user created Food"""
        food_obj = super().get_object(queryset)
        if food_obj.user != self.request.user:
            raise PermissionDenied(
                'You are not authorized to delete this food')
        return food_obj


class RecipeListView(generic.ListView):
    """class-based List view for recpipes"""
    model = Recipe
    paginate_by = 6

    def get_queryset(self):
        recipe_filter = self.request.GET.get("q")
        if recipe_filter:
            filter_query = Q(name__icontains=recipe_filter) | Q(
                category__category_type__icontains=recipe_filter)
            recipe_filter = Recipe.objects.filter(filter_query).distinct()
            print(recipe_filter)
            return recipe_filter
        return Recipe.objects.all()


class RecipeDetailView(generic.DetailView):
    """class-based detail view for specific Recipe isntance"""
    model = Recipe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()
        context['instruction_list'] = recipe.instructions.splitlines()

        return context


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ['user', 'name', 'ingredients', 'category',
                  'portion_size', 'portion_quantity', 'instructions']
        widgets = {
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-select form-control'}),
            'category': forms.SelectMultiple(attrs={'class': 'form-select form-control'}),
            'portion_size': forms.Select(attrs={'class': 'form-select form-control'}),
        }


class RecipeCreate(LoginRequiredMixin, generic.CreateView):
    """generic-edit view to create a Recipe instance using forms"""
    model = Recipe
    form_class = RecipeForm

    def get_form(self, form_class=None):
        """Overiding get_form to modify form fields"""
        form = super().get_form(form_class)
        form.fields['user'].initial = self.request.user
        form.fields['user'].widget = forms.HiddenInput()
        form.fields['category'].help_text = None
        form.fields['portion_size'].help_text = None
        form.fields['ingredients'].help_text = None
        form.fields['instructions'].help_text = None

        return form


class RecipeUpdate(LoginRequiredMixin, generic.UpdateView):
    """generic-edit view to update a recipe instance using forms"""
    model = Recipe
    fields = ['user', 'name', 'ingredients', 'category',
              'portion_size', 'portion_quantity', 'instructions']

    def get_object(self, queryset=None):
        """overide get_object to verify logged in user created Recipe"""
        recipe_obj = super().get_object(queryset)
        if recipe_obj.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to update this recipe")
        return recipe_obj

    def get_form(self, form_class=None):
        """Overiding get_form to modify form fields"""
        form = super().get_form(form_class)
        form.fields['user'].initial = self.request.user
        form.fields['user'].widget = forms.HiddenInput()
        form.fields['category'].help_text = None
        form.fields['portion_size'].help_text = None
        form.fields['ingredients'].help_text = None
        form.fields['instructions'].help_text = None

        return form


class RecipeDelete(LoginRequiredMixin, generic.DeleteView):
    """generic-edit view to delete a recipe instance using forms"""
    model = Recipe
    success_url = reverse_lazy('all-recipes')

    def get_object(self, queryset=None):
        """override get_object to verify logged in user created Recipe"""
        recipe_obj = super().get_object(queryset)
        if recipe_obj.user != self.request.user:
            raise PermissionDenied(
                "You are not authorized to delete this recipe")
        return recipe_obj
