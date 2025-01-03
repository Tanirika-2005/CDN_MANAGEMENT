from flask import Flask, request, jsonify
import random
import cohere

# Initialize Flask app and Cohere client
app = Flask(__name__)
cohere_client = cohere.Client('vE1Dkwt4h88KMxapx1gcKcw7sHwaS4AauhTIaCpO')  # Replace with your Cohere API key

cache = {}  # Cache structure

def predict_genre(movie_title):
    """Predict the genre for a given movie title using Cohere."""
    try:
        response = cohere_client.generate(
            model='command',
            prompt=f"Given the movie title '{movie_title}', predict its genre. Only output the genre name (e.g., action, romance, comedy) , no addition explanantion no intro needed",
            max_tokens=10,
            temperature=0.5,
        )
        return response.generations[0].text.strip().lower()
    except Exception as e:
        print(f"Error with Cohere genre prediction: {e}")
        return None

def predict_movies(genre):
    """Predict movie titles for a given genre using Cohere."""
    try:
        response = cohere_client.generate(
            model='command',
            prompt=f"List 5 popular movies in the {genre} genre. Only output the movie titles separated by commas no need to even tell 'here are the' type things, no additional explanation no need for intro also ",
            max_tokens=50,
            temperature=0.7,
        )
        movies = [movie.strip() for movie in response.generations[0].text.split(",") if movie.strip()]
        return movies[:5]  # Ensure exactly 5 movies
    except Exception as e:
        print(f"Error with Cohere movie prediction: {e}")
        return []

@app.route('/make_request', methods=['POST'])
def make_request():
    data = request.json
    user_id = str(data["user_id"])
    movie_title = data.get("movie_title")
    genre = data.get("genre")

    # Initialize cache for user
    if user_id not in cache:
        cache[user_id] = {}

    if movie_title:
        genre = predict_genre(movie_title)
        if not genre:
            return jsonify({"error": "Movie genre not found"}), 404

    if genre:
        if genre in cache[user_id]:
            return jsonify({
                "genre": genre,
                "movies": cache[user_id][genre],
                "status": "cache_hit"
            })

        # Cache miss: Predict movies for the genre
        movies = predict_movies(genre)
        cache[user_id][genre] = movies

        # Add predictions for 4 additional genres
        other_genres = []
        while len(other_genres) < 4:
            random_genre = predict_genre(f"Random Genre Seed {random.randint(1, 10000)}")
            if random_genre and random_genre not in other_genres and random_genre != genre:
                other_genres.append(random_genre)

        for g in other_genres:
            if g not in cache[user_id]:
                cache[user_id][g] = predict_movies(g)

        return jsonify({
            "genre": genre,
            "movies": movies,
            "predictions": {g: cache[user_id][g] for g in [genre] + other_genres},
            "status": "cache_miss"
        })

    return jsonify({"error": "Invalid request"}), 400

@app.route('/cache_status', methods=['GET'])
def cache_status():
    return jsonify(cache)

if __name__ == '__main__':
    app.run(debug=True)
