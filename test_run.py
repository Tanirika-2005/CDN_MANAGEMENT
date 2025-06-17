from flask import Flask, request, jsonify
import cohere
from collections import OrderedDict, deque

# Initialize Flask app and Cohere client
app = Flask(__name__)
cohere_client = cohere.Client('put ur own key')  # Replace with your Cohere API key

# Cache setup
cache = {}
CACHE_LIMIT = 5  # Max number of genres in the cache per user

# User request history setup
request_history = {}  # Dictionary to store each user's request history (as a deque)
HISTORY_LIMIT = 5  # Max number of requests to keep in user history

# Predefined edge servers based on user location
EDGE_SERVERS = {
    'north america': 'Edge Server 1',
    'europe': 'Edge Server 2',
    'asia': 'Edge Server 3',
    'south america': 'Edge Server 4',
    'africa': 'Edge Server 5',
    'australia': 'Edge Server 6'
}

def predict_genre(movie_title):
    """Predict the genre for a given movie title using Cohere."""
    try:
        response = cohere_client.generate(
            model='command',
            prompt=(
                f"Based on the movie title '{movie_title}', provide the genre as one word "
                f"(e.g., action, romance, comedy). No extra text, no explanations, only output the genre name."
            ),
            max_tokens=10,
            temperature=0.5,
        )
        return response.generations[0].text.strip().lower()  # Standardize to lowercase
    except Exception as e:
        print(f"Error with Cohere genre prediction: {e}")
        return None

def predict_movies(genre):
    """Predict movie titles for a given genre using Cohere."""
    try:
        response = cohere_client.generate(
            model='command',
            prompt=(
                f"Provide exactly 5 popular movie titles in the {genre} genre. Format the output as a comma-separated list. "
                f"No introductions, and no explanations.please avoid things like 'Here are 5 popular movie titles in the action genre',just output the movie title for example 'The Notebook'"
            ),
            max_tokens=50,
            temperature=0.7,
        )
        movies = [movie.strip() for movie in response.generations[0].text.split(",") if movie.strip()]
        return movies[:5]  # Ensure exactly 5 movies
    except Exception as e:
        print(f"Error with Cohere movie prediction: {e}")
        return []

def evict_cache(edge_server, user_id):
    """Evict the least recently used item from the cache if the cache exceeds the size limit."""
    if len(cache[edge_server][user_id]) > CACHE_LIMIT:
        cache[edge_server][user_id].popitem(last=False)  # Remove the first (least recently used) item

def get_edge_server(location):
    """Select the edge server based on user location."""
    return EDGE_SERVERS.get(location.lower(), 'Edge Server 1')  # Default to 'Edge Server 1' if location is not found

@app.route('/make_request', methods=['POST'])
def make_request():
    data = request.json
    user_id = str(data.get("user_id"))
    movie_title = data.get("movie_title")
    genre = data.get("genre")
    location = data.get("location")

    # Select the edge server based on the location
    edge_server = get_edge_server(location)
    if edge_server not in cache:
        cache[edge_server] = {}
    if user_id not in cache[edge_server]:
        cache[edge_server][user_id] = OrderedDict()
    if user_id not in request_history:
        request_history[user_id] = deque(maxlen=HISTORY_LIMIT)  # Create a deque with a fixed max size

    # Add the current request to user history
    request_info = {"movie_title": movie_title, "genre": genre.lower() if genre else None}
    request_history[user_id].append(request_info)

    if movie_title:
        genre = predict_genre(movie_title)
        if not genre:
            return jsonify({"error": "Movie genre not found"}), 404

    if genre:
        genre = genre.lower()  # Normalize genre to lowercase
        # Check if genre exists in cache
        if genre in cache[edge_server][user_id]:
            cache[edge_server][user_id].move_to_end(genre)
            return jsonify({
                "genre": genre,
                "movies": cache[edge_server][user_id][genre],
                "status": "cache_hit",
                "history": list(request_history[user_id])
            })

        # Cache miss: Predict movies for the genre
        movies = predict_movies(genre)
        cache[edge_server][user_id][genre] = movies
        evict_cache(edge_server, user_id)

        # Predict additional genres using AI based on user history
        try:
            user_requests = [str(req['movie_title']) for req in list(request_history[user_id])]
            response = cohere_client.generate(
                model='command',
                prompt=(
                    f"Based on these movie titles the user requested: {', '.join(user_requests)}, "
                    "provide exactly 4 valid genres separated by commas. Only valid genres like action, comedy, thriller, etc. "
                    "Do not include movie names, explanations, or any extra text. "
                    "Output format: genre1, genre2, genre3, genre4."
                ),
                max_tokens=10,
                temperature=0.5,
            )
            other_suggestions = [s.strip().lower() for s in response.generations[0].text.split(",") if s.strip()]
            valid_genres = {'action', 'comedy', 'drama', 'romance', 'thriller', 'sci-fi', 'horror', 'adventure', 'animation'}
            other_suggestions = [genre for genre in other_suggestions if genre in valid_genres]
        except Exception as e:
            print(f"Error with AI suggestion prediction: {e}")
            other_suggestions = []

        cleaned_predictions = {}
        for suggestion in other_suggestions:
            if suggestion not in cache[edge_server][user_id]:
                valid_movies = predict_movies(suggestion)
                if valid_movies:
                    cache[edge_server][user_id][suggestion] = valid_movies

            cleaned_predictions[suggestion] = cache[edge_server][user_id].get(suggestion, [])

        evict_cache(edge_server, user_id)

        return jsonify({
            "genre": genre,
            "movies": movies,
            "predictions": cleaned_predictions,
            "status": "cache_miss",
            "history": list(request_history[user_id]),
            "edge_server": edge_server
        })

    return jsonify({"error": "Invalid request"}), 400

@app.route('/cache_status', methods=['GET'])
def cache_status():
    return jsonify(cache)

@app.route('/history_status', methods=['GET'])
def history_status():
    return jsonify({user_id: list(history) for user_id, history in request_history.items()})

if __name__ == '__main__':
    app.run(debug=True)
