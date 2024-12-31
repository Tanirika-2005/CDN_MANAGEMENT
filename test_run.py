from flask import Flask, request, jsonify
from collections import OrderedDict, deque
import cohere  # Install using: pip install cohere

# Initialize Flask app and Cohere client
app = Flask(__name__)

cohere_client = cohere.Client('vE1Dkwt4h88KMxapx1gcKcw7sHwaS4AauhTIaCpO')  # Replace with your Cohere API key

# Edge node caches, with region-based naming
edge_nodes = {
    "node_us": OrderedDict(),  # US region node
    "node_eu": OrderedDict(),  # EU region node
    "node_asia": OrderedDict(),  # Asia region node
}
node_cache_size_limit = 5  # Cache size limit per node
region_histories = {  # Maintain separate histories for each region
    "us": deque(maxlen=5),
    "eu": deque(maxlen=5),
    "asia": deque(maxlen=5),
}

# Function to generate predictions from Cohere API
def get_predictions_from_cohere(history, genre,region):
    # Prepare the prompt to send to Cohere for genre predictions
    prompt = f"Given the user's genre history: {', '.join(history)} and the current genre preference: {genre},and current region{region}, suggest the next 3 genres no verbose explanation just the genre separated by commas no serial numbers needed."
    
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
def get_assigned_edge_node(user_id, region):
    return f"node_{region.lower()}"

# Function to synchronize caches within the same region
def synchronize_caches(region, new_predictions):
    for node_name, node_cache in edge_nodes.items():
        if node_name.startswith(f"node_{region.lower()}"):
            # Ensure the region's cache list is initialized
            if region not in node_cache:
                node_cache[region] = []

            # Add each predicted genre to the cache if not already present
            for prediction in new_predictions:
                if prediction not in node_cache[region]:
                    node_cache[region].append(prediction)

            # Evict LRU if cache exceeds size limit
            while len(node_cache[region]) > node_cache_size_limit:
                node_cache[region].pop(0)

@app.route("/request", methods=["POST"])
def handle_request():
    data = request.json
    user_id = data["user_id"]
    entered_genre = data["genre"].lower()
    region = data["region"].lower()

    # Assign user to a region-based edge node
    assigned_node_name = get_assigned_edge_node(user_id, region)
    assigned_node = edge_nodes[assigned_node_name]

    # Ensure the region's cache is initialized
    if region not in assigned_node:
        assigned_node[region] = []

    # Check if the genre is in the local cache
    if entered_genre in assigned_node[region]:
        # Move the genre to the most recently used position
        assigned_node[region].append(assigned_node[region].pop(assigned_node[region].index(entered_genre)))
        return jsonify({"status": "cache_hit", "node": assigned_node_name, "genre": entered_genre})
    else:
        # Generate predictions based on region-specific history
        new_predictions = get_predictions_from_cohere(region_histories[region], entered_genre,region)

        # Add new predictions and the entered genre to the region's cache
        synchronize_caches(region, [entered_genre] + new_predictions)

        # Update region history
        region_histories[region].append(entered_genre)

        return jsonify({"status": "cache_miss", "node": assigned_node_name, "predictions": new_predictions})

@app.route("/cache_status", methods=["GET"])
def cache_status():
    # Return cache status for all edge nodes
    return jsonify({node_name: list(cache.values()) for node_name, cache in edge_nodes.items()})

if __name__ == "__main__":
    app.run(debug=True)
