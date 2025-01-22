import requests

def setup_demo(url):
    """Setups demo for the channels server."""

    # Create a default room
    response = requests.get(url + "/create_room/default/")
    
    # Create two endpoints for the default room
    response = requests.get(url + "/add_endpoint/default/readwrite/?identity=endpoint1")
    if response.status_code != 200:
        print("Error - check url, server and api key")
        return

    # Get the endpoint code
    endpoint_code1 = response.json()["code"]

    response = requests.get(url + "/add_endpoint/default/readwrite/?identity=endpoint2")

    # Get the endpoint code
    endpoint_code2 = response.json()["code"]

    # Print the room urls for the setup
    print(f"Room URL for endpoint1: {url}/room/{endpoint_code1}/")
    print(f"Room URL for endpoint2: {url}/room/{endpoint_code2}/")
    print("Try to send messages and see the responses")
    print()
    print(f"Link to see the list of rooms: {url}/list_rooms/")
    print(f"Link to see the list of endpoints: {url}/list_endpoints/default/")

setup_demo("http://127.0.0.1:8000")