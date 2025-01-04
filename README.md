# Intelligent Movie Recommendation Caching System

This project implements an intelligent caching system for movie recommendations, optimizing performance by caching frequently accessed data and predicting the next movie genres a user might be interested in. The system intelligently predicts genres and movies based on user behavior and location, providing an efficient cache management strategy.

## Features

- **Intelligent Caching**: Caches movie recommendations based on genres, storing only the most frequently requested ones to optimize performance.
- **Cache Eviction**: Implements an LRU (Least Recently Used) eviction strategy to keep the cache size manageable while prioritizing recently requested genres.
- **User-Specific History**: Maintains a history of each user’s movie requests, dynamically updating with each new request.
- **Location-Based Edge Servers**: Selects the optimal edge server based on the user’s location, improving response times.
- **Cache Hit/Miss Handling**: Determines whether the requested genre is already in the cache (cache hit) or needs to be fetched (cache miss), providing immediate results when possible.

---

## Getting Started

### Prerequisites

To run this project, ensure you have:

- Python 3.7 or higher.
- A valid [Cohere API key](https://cohere.ai/) to make genre and movie predictions.


Here's a README.md focusing on the Intelligent Caching aspect of your project:

markdown
Copy code
# Intelligent Movie Recommendation Caching System

This project implements an intelligent caching system for movie recommendations, optimizing performance by caching frequently accessed data and predicting the next movie genres a user might be interested in. The system intelligently predicts genres and movies based on user behavior and location, providing an efficient cache management strategy.

## Features

- **Intelligent Caching**: Caches movie recommendations based on genres, storing only the most frequently requested ones to optimize performance.
- **Cache Eviction**: Implements an LRU (Least Recently Used) eviction strategy to keep the cache size manageable while prioritizing recently requested genres.
- **User-Specific History**: Maintains a history of each user’s movie requests, dynamically updating with each new request.
- **Location-Based Edge Servers**: Selects the optimal edge server based on the user’s location, improving response times.
- **Cache Hit/Miss Handling**: Determines whether the requested genre is already in the cache (cache hit) or needs to be fetched (cache miss), providing immediate results when possible.

---

## Getting Started

### Prerequisites

To run this project, ensure you have:

- Python 3.7 or higher.
- A valid [Cohere API key](https://cohere.ai/) to make genre and movie predictions.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
Create and activate a virtual environment (optional but recommended):

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Replace the placeholder YOUR_COHERE_API_KEY in app.py with your actual API key.

Configuration
Update the EDGE_SERVERS dictionary in test_run.py if necessary. This will define the available edge servers based on user locations (e.g., North America, Asia).
Optionally, you can configure a .env file to securely store sensitive information such as your API key.
How It Works
1. Requesting Movie Recommendations
Users can send a request with a movie title or genre, and the system will:

Predict the genre from the movie title (if provided).
Check if the requested genre is already cached.
If cached, the server returns the cached movies, indicating a cache hit.
If not cached, the system predicts movie recommendations for the genre, adds the genre to the cache, and evicts the least recently used genre if necessary, resulting in a cache miss.
2. Location-Based Edge Server Selection
Based on the user's location (e.g., Asia, Europe), the system selects the optimal edge server from a predefined list of servers. This reduces latency by directing the user’s request to the nearest server.

3. User-Specific History
The system maintains a user-specific history, tracking the last 5 requests. The history is updated dynamically with each new request, and genres are predicted based on the user's history of movie titles.

4. Cache Eviction Strategy
To maintain an efficient cache size, an LRU (Least Recently Used) eviction strategy is implemented. When the cache exceeds the specified limit (5 genres per user), the least recently used genre is removed from the cache.
