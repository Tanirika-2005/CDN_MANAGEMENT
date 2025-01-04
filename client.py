import requests
import json

# Base URL for the Flask API (adjust this if the Flask server is hosted elsewhere)
BASE_URL = 'http://127.0.0.1:5000'  # Localhost if running locally, update if hosted on a server

def make_request(user_id, movie_title=None, genre=None, location="North America"):
    """Function to send a request to the Flask server to get movie recommendations."""
    
    # Prepare the data that we want to send to the server
    data = {
        "user_id": user_id,        # The unique identifier for the user
        "movie_title": movie_title, # The movie title we want to check (optional)
        "genre": genre,             # The genre we want recommendations for (optional)
        "location": location       # The location of the user (used for edge server decision)
    }
    
    # Sending a POST request to the /make_request endpoint of our Flask API
    response = requests.post(f"{BASE_URL}/make_request", json=data)
    
    # Check if the response is successful (status code 200)
    if response.status_code == 200:
        print("Response from server:")
        print(json.dumps(response.json(), indent=4))  # Pretty print the response JSON
    else:
        print(f"Error: {response.status_code}")
        print(response.json())  # Print error details if the request failed

def get_cache_status(user_id):
    """Function to fetch the current cache status for a specific user from the Flask server."""
    
    # Sending a GET request to the /cache_status endpoint of our Flask API with user_id as a parameter
    response = requests.get(f"{BASE_URL}/cache_status?user_id={user_id}")
    
    # Check if the response is successful (status code 200)
    if response.status_code == 200:
        print("Cache Status:")
        print(json.dumps(response.json(), indent=4))  # Pretty print the cache status JSON
    else:
        print(f"Error: {response.status_code}")
        print(response.json())  # Print error details if the request failed

# Main block to interact with the user and perform actions
if __name__ == '__main__':
    print("Welcome to the Movie Recommendation System!")

    while True:
        print("\nSelect an option:")
        print("1. Make a request for movie recommendations")
        print("2. View cache status")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == '1':
            # Option to make a movie or genre request
            user_id = input("\nEnter your user ID: ")
            location = input("Enter your location (e.g., North America, Europe, Asia): ").strip()

            # Ask the user if they want to enter a movie title or a genre
            choice = input("Do you want to enter a movie title or a genre? (Enter 'movie' or 'genre'): ").strip().lower()

            if choice == 'movie':
                # If the user chooses movie title, ask for the title
                movie_title = input("Enter the movie title: ").strip()
                print("\nMaking a request with a movie title...")
                make_request(user_id, movie_title=movie_title, location=location)

            elif choice == 'genre':
                # If the user chooses genre, ask for the genre
                genre = input("Enter the genre (e.g., action, comedy, drama): ").strip().lower()
                print("\nMaking a request with a genre...")
                make_request(user_id, genre=genre, location=location)

            else:
                print("Invalid choice! Please restart the program and choose 'movie' or 'genre'.")
        
        elif choice == '2':
            # Option to view cache status
            user_id = input("\nEnter your user ID to view cache status: ").strip()
            print("\nFetching cache status...")
            get_cache_status(user_id)

        elif choice == '3':
            # Exit the program
            print("\nExiting the program. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a valid option (1/2/3).")
