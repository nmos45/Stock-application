from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import StockInstance, StockFood
from django.utils.safestring import mark_safe
import json


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = "chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        recipe_context = self.get_recipe_context()
        conversation_id = self.kwargs['conversation_id']

        # for jinja use
        context['foods'] = recipe_context['foods']
        # for js frontend options
        context['recipe_context'] = mark_safe(json.dumps(recipe_context))
        context['conversation_id'] = conversation_id

        previous_chat = self.request.session.get(f'chat:{conversation_id}')
        if previous_chat:
            print(previous_chat)
            context['previous_chat'] = json.loads(previous_chat)
        return context

    def get_recipe_context(self):
        """returns html safe json string of recipe related data for llm chat"""
        stock_instances = StockInstance.objects.filter(user=self.request.user)
        stockfoods = StockFood.objects.filter(
            stock_instance__in=stock_instances).select_related('food', 'stock_instance')

        # verified and non verified foods included for now
        # RecipeCreate will validate
        inventory_to_foods = {}
        foods = set()
        for sf in stockfoods:
            inventory = sf.stock_instance
            if inventory.id not in inventory_to_foods:
                # instances may have same name
                inventory_to_foods[inventory.id] = {
                    'id': inventory.id, 'name': inventory.name, 'foods': set()}
            foods.add(sf.food.name)
            inventory_to_foods[inventory.id]['foods'].add(sf.food.name)
        # for all option in select
        inventory_to_foods[0] = {
            'id': 0, 'name': 'all', 'foods': foods
        }

        # serialize to json suported types
        inventories = [{'id': inventory['id'], 'name': inventory['name'], 'foods': list(
            inventory['foods'])} for inventory in inventory_to_foods.values()]
        foods = list(foods)
        print(foods)

        recipe_context = {
            'inventories': inventories,
            'foods': foods,
        }
        return recipe_context
