import requests
from config import search_engine_id_google, google_tokenAPI


def get_nasa_photo(api_key):
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        photo_url = data.get('url')
        explanation = data.get('explanation')
        return photo_url, explanation
    else:
        return None, None


def search(query):
    url = f'https://www.googleapis.com/customsearch/v1?key={google_tokenAPI}&cx={search_engine_id_google}&q={query}'

    response = requests.get(url)
    results = response.json()['items'] if 'items' in response.json() else []

    return results

