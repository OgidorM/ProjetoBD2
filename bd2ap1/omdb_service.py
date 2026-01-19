import os
import requests

OMDB_API_KEY = os.getenv('OMDB_API_KEY', '30f195b7')  # Use the user's provided API key
OMDB_URL = "http://www.omdbapi.com/?i=tt3896198&apikey=30f195b7"

def fetch_movie_data(title):
    """
    Fetches movie metadata from OMDb API by title.
    """
    if not OMDB_API_KEY:
        return {"error": "OMDb API Key not configured."}

    params = {
        #'apikey': OMDB_API_KEY,
        't': title,
        'plot': 'full'
    }

    try:
        response = requests.get(OMDB_URL, params=params)
        data = response.json()

        if data.get('Response') == 'False':
            return {"error": data.get('Error', 'Movie not found')}

        # Map OMDb data to our format
        # Duration format is "123 min" -> 123
        duration_str = data.get('Runtime', '0 min')
        duration = int(duration_str.split(' ')[0]) if 'min' in duration_str else 0

        poster = data.get('Poster')
        if poster == 'N/A':
            poster = None

        return {
            "titulo": data.get('Title'),
            "datalancamento": data.get('Released'), 
            "duracao": duration,
            "realizador": data.get('Director'),
            "produtora": data.get('Production'),
            "sinopse": data.get('Plot'),
            "poster": poster,
            "rating": data.get('imdbRating'),
            "year": data.get('Year')
        }

    except Exception as e:
        return {"error": str(e)}
