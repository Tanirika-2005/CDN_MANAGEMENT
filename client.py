import requests

server_url = "http://127.0.0.1:5000"  # Make sure the server URL is correct

# Function to make a user request
def user_request(user_id, genre, region):
    response = requests.post(f"{server_url}/request", json={"user_id": user_id, "genre": genre, "region": region})

    # Check the response status and content
    if response.status_code == 200:
        try:
            print("\nServer Response:", response.json())  # Attempt to parse the JSON
        except ValueError:
            print("Failed to parse JSON response. Raw response:", response.text)
    else:
        print(f"Error: Received status code {response.status_code}. Raw response:", response.text)

# Function to check cache status
def check_cache_status():
    response = requests.get(f"{server_url}/cache_status")

    # Check the response status and content
    if response.status_code == 200:
        print("\nCache Status:", response.json())
    else:
        print(f"Error: Received status code {response.status_code}. Raw response:", response.text)

def main():
    while True:
        print("\n1. Make a request")
        print("2. Check cache status")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            user_id = int(input("Enter your user ID: "))
            genre = input("Enter the genre you're interested in: ")
            region = input("Enter your region (us, eu, asia): ")
            user_request(user_id, genre, region)
        elif choice == '2':
            check_cache_status()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
