from flask import Flask, request, jsonify
from collections import OrderedDict, deque
import cohere  # Install using: pip install cohere

# Initialize Flask app and Cohere client
app = Flask(__name__)

cohere_client = cohere.Client('vE1Dkwt4h88KMxapx1gcKcw7sHwaS4AauhTIaCpO')  # Replace with your Cohere API key

# Edge node caches, with region-based naming
edge_nodes = {
    "node_us": {},
    "node_eu": {},
    "node_asia": {},
}
node_cache_size_limit = 5  # Cache size limit per node
region_histories = {  # Maintain separate histories for each region and user
    "us": {},
    "eu": {},
    "asia": {},
}

# Function to generate predictions from Cohere API
def get_predictions_from_cohere(history, genre, region):
    # Prepare the prompt to send to Cohere for genre predictions
    prompt = f"Given the user's genre history: {', '.join(history)} and the current genre preference: {genre}, and current region {region}, suggest the next 3 genres no verbose explanation, just the genres separated by commas, no serial numbers needed."
    
    response = cohere_client.generate(  
        model='command',
        prompt=prompt,
        max_tokens=10,
        temperature=0.7
    )
    
    # Extract predicted genres from the response text
    predictions = response.generations[0].text.strip().split(", ")
    return predictions

# Assign user to a region-based edge node
def get_assigned_edge_node(region):
    return f"node_{region.lower()}"

# Function to synchronize caches for a specific user
def synchronize_user_cache(region, user_id, new_entries):
    node_name = get_assigned_edge_node(region)
    node_cache = edge_nodes[node_name]

    # Ensure user-specific cache is initialized
    if user_id not in node_cache:
        node_cache[user_id] = deque(maxlen=node_cache_size_limit)

    # Add new entries to the user's cache
    for entry in new_entries:
        if entry in node_cache[user_id]:
            node_cache[user_id].remove(entry)  # Remove existing entry to re-add it
        node_cache[user_id].append(entry)

@app.route("/request", methods=["POST"])
def handle_request():
    data = request.json
    user_id = data["user_id"]
    entered_genre = data["genre"].lower()
    region = data["region"].lower()

    # Assign user to a region-based edge node
    assigned_node_name = get_assigned_edge_node(region)
    assigned_node = edge_nodes[assigned_node_name]

    # Ensure user-specific cache is initialized
    if user_id not in assigned_node:
        assigned_node[user_id] = deque(maxlen=node_cache_size_limit)

    # Check if the genre is in the user's cache
    if entered_genre in assigned_node[user_id]:
        # Move the genre to the most recently used position
        assigned_node[user_id].remove(entered_genre)
        assigned_node[user_id].append(entered_genre)
        return jsonify({"status": "cache_hit", "node": assigned_node_name, "user": user_id, "genre": entered_genre})
    else:
        # Generate predictions based on user-specific history
        user_history = list(region_histories[region].get(user_id, []))
        new_predictions = get_predictions_from_cohere(user_history, entered_genre, region)

        # Update user-specific and region histories
        synchronize_user_cache(region, user_id, [entered_genre] + new_predictions)
        if user_id not in region_histories[region]:
            region_histories[region][user_id] = deque(maxlen=node_cache_size_limit)
        region_histories[region][user_id].append(entered_genre)

        return jsonify({"status": "cache_miss", "node": assigned_node_name, "user": user_id, "predictions": new_predictions})

@app.route("/cache_status", methods=["GET"])
def cache_status():
    # Return cache status for all edge nodes and user-specific caches
    return jsonify({node_name: {user_id: list(cache) for user_id, cache in node_cache.items()} for node_name, node_cache in edge_nodes.items()})

if __name__ == "__main__":
    app.run(debug=True)
