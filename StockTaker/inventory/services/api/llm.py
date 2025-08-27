from decouple import config
from google import genai
from pydantic import BaseModel, ConfigDict
from typing import Literal
from google.genai import types
from inventory.models import Food, Category
from .images import call_image_api
from celery import shared_task
import json

import redis


class RecipeModel(BaseModel):
    recipe_number: int
    name: str
    ingredients: list[str]
    categories: list[str]
    portion_size: Literal['g', 'kg', 'oz', 'ml']
    portion_quantity: int
    instructions: str


# @shared_task
def call_llm_api(job_id, ingredients, user_prompt):
    """function to generate recipes from llm api"""

    r = redis.Redis(host=config('REDIS_HOST'),
                    port=6379, decode_responses=True)

    client = genai.Client(
        http_options=types.HttpOptions(api_version='v1alpha')
    )

    # r.set(f'recipes:{job_id}', "[]")
    # r.set(f'recipes:{job_id}:done', 'False')
    # for chunk in client.models.generate_content_stream(
    #     model="gemini-2.5-flash",
    #     contents=[
    #         """
    #                 find 10 recipes that use only the ingredients passed in this request, the recipe ingredients should only
    #                 contain the food name. The ingredients foods should only include the foods passed in the request and should have the exact same name.
    #                 Only reference the amount of each ingredient for the recipe in the instructions.
    #                 The portion_quantity should refer to the entire recipe quantity. I have also attached some specific user
    #                 input for what type of recipes to generate.                    """,
    #         ingredients,
    #         user_prompt
    #     ],
    #     config={
    #         "response_mime_type": "application/json",
    #         "response_schema": list[RecipeModel]
    #     },
    # ):
    #     previous_chunks = r.get(
    #         f"recipes:{str(job_id)}")
    #     previous_chunks = previous_chunks if previous_chunks is not None else ""
    #     r.set(f'recipes:{job_id}', previous_chunks + chunk.text)
    # r.set(f'recipes:{job_id}:done', 'True')
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            """
                find 10 recipes that use only the ingredients passed in this request, the recipe ingredients should only
                contain the food name. The ingredients foods should only include the foods passed in the request and should have the exact same name.
                Only reference the amount of each ingredient for the recipe in the instructions.
                The portion_quantity should refer to the entire recipe quantity. I have also attached some specific user
                input for what type of recipes to generate.
        """,
            ingredients,
            user_prompt
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": list[RecipeModel],
        },
    )

    pydanticRecipes = validate_recipes(response.parsed)
    r.set(f'recipes:{job_id}', json.dumps(pydanticRecipes))
    # parsed is model representation of data in python objects
    # return validate_recipes(response.parsed)


def validate_recipes(responseModelList):
    """validates pydanic model in response from llm call"""
    recipes = []
    for recipe in responseModelList:
        recipe_dict = recipe.dict()
        recipe_dict['ingredients'] = list(Food.objects.filter(
            name__in=recipe_dict['ingredients']).values_list('name', flat=True))

        recipe_dict['categories'] = list(Category.objects.filter(
            category_type__in=recipe_dict['categories']).values_list('category_type', flat=True))
        recipes.append(recipe_dict)
        image = call_image_api(recipe_dict['name'])
        if image:
            recipe_dict['image'] = image
    return recipes
