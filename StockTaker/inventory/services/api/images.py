from decouple import config
import requests


def call_image_api(query):
    """function to generate recipes from llm api"""
    headers = {
        'Authorization': config('UNSPLASH_API_KEY')
    }
    params = {
        'query': query,
        'per_page': 1,
    }
    response = requests.get(
        'https://api.unsplash.com/search/photos', headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        url = data['results'][0]['urls']['raw']
        return url

    return None
