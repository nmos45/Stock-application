# chat/consumers.py
import json
from google import genai
from google.genai import types
from inventory.models import Category
from channels.db import database_sync_to_async
import asyncio
import textile
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from decouple import config
import redis.asyncio as redis


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print("determining connnection")
        # Called on connection.
        # To accept the connection call:
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']

            client = genai.Client(
                http_options=types.HttpOptions(api_version='v1alpha'),
            )
            system_prompt = """
            The user is coming from a stockTaking application, they will ask you to generate a recipe with a possible list
            of ingredients from their household passed as context. Your 
            response should be text based, like in a conversation and you can give a discription of the recipe and ingredients
            as well as linking urls to an external video or entire recipe.
            """

            # get previous chats
            history = await self.get_from_session(
                f"chat:{self.conversation_id}")
            if history:
                history = json.loads(history)
            chat = client.chats.create(
                model='gemini-2.0-flash',
                config={"system_instruction": system_prompt},
                history=history,
            )
            self.chat = chat
            self.history = history if history else []

            await self.accept()
        else:
            await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        # Called with either text_data or bytes_data for each frame
        # You can call:
        text_data_json = json.loads(text_data)
        prompt = text_data_json.get('prompt', None)
        ingredients = text_data_json.get('ingredients', None)
        create_recipe = text_data_json.get('createRecipe', None)

        if create_recipe:
            message = """convert the recipe you just described into the response_schema and include all fields
                         including portion_size and portion_quantity"""

            response = self.chat.send_message(
                message=message,
                config=await self.getConfig(),
            )
            # don't pickle for now
            key = f'recipe_create:{self.conversation_id}'
            recipe = json.dumps(response.parsed)
            await self.save_to_session(key, recipe)

            # send redirect url to frontend
            url = f"/inventory/recipe/create/?conversation_id={
                self.conversation_id}"
            message = {
                'action': 'redirect',
                'url': url,
            }
            # send_json closes socket
            await self.send_json(content=message, close=True)

        if prompt and ingredients:
            # async client only for vertexAI
            message = f"prompt: {prompt}, ingredients chosen: {
                str(ingredients)}, note: the response should be in textile format"
            new_prompt = self.create_content_dict(prompt, 'user')
            self.history.append(new_prompt)

            full_text_response = ""

            # render initial textile text and only convert entire response to html
            for chunk in self.chat.send_message_stream(message):
                full_text_response += chunk.text
                message = {
                    'action': 'response-stream',
                    'text': chunk.text,
                }
                await self.send_json(content=message, close=False)
                await asyncio.sleep(1)

            html_response = textile.textile(full_text_response)
            print(html_response)

            message = {
                'action': 'html-response',
                'html': html_response,
            }

            await self.send_json(content=message, close=False)

            # save response to session
            new_response = self.create_content_dict(
                html_response, 'model')

            self.history.append(new_response)
            if len(self.history) > 10:
                self.history = self.history[:10]

            await self.save_to_session(
                f'chat:{self.conversation_id}', json.dumps(self.history))
        else:
            print("no payload")
            await self.close()

    async def getConfig(self):
        categories = await database_sync_to_async(
            lambda:                 [
                category.category_type for category in Category.objects.all()]
        )()
        return {
            'response_mime_type': 'application/json',
            'response_schema': {
                'type': 'object',
                'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'the name of the recipe',
                        },
                    'ingredients': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'description': 'single word foods'
                    },
                    'categories': {
                            'type': 'array',
                            'items': {
                                    'type': 'string',
                                    'enum': categories,
                            },
                            'description': 'categories the recipe is in',
                    },
                    'portion_size': {
                            'type': 'string',
                            'enum': ['g', 'kg', 'oz', 'ml'],
                    },
                    'portion_quantity': {
                            'type': 'integer',
                            'description': 'the quanity of size portion_size the recipe provides',
                    },
                    'instructions': {
                            'type': 'string',
                            'description': 'the recipe cooking instructions',
                    }
                }
            }
        }

    def create_content_dict(self, text, role):
        return {
            'parts': [{
                'text': text,
            }],
            'role': role,
        }

    @database_sync_to_async
    def get_from_session(self, key):
        """async wrapper to make session gets"""
        return self.scope['session'].get(key)

    @database_sync_to_async
    def save_to_session(self, key, value):
        """async wrapper to make session saves """
        self.scope['session'][key] = value
        self.scope['session'].save()

    # async def disconnect(self, close_code):
    #     # Called when the socket closes
