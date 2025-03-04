import requests


def setup_demo(url):
    """Setups demo for the channels server."""

    # Create a default room
    json_data = {"room_name": "default"}
    response = requests.post(
        url + "/create_room/", json=json_data, 
    )
    if response.status_code != 200:  # Check if the request was successful
        print("Error - check url, server and api key")
        print(response.text)
        return
    else:
        print("Default room created")
        print(response.text)

    # Create two endpoints for the default room
    json_data = {
        "identity": "endpoint1",
        "permissions": "readwrite",
        "room_name": "default",
    }
    response = requests.post(
        url + "/add_endpoint/", json=json_data, 
    )
    if response.status_code != 200:
        print("Error - check url, server and api key")
        return

    # Get the endpoint code
    endpoint_code1 = response.json()["code"]

    # Create the second endpoint
    json_data = {
        "identity": "endpoint2",
        "permissions": "readwrite",
        "room_name": "default",
    }
    response = requests.post(
        url + "/add_endpoint/", json=json_data, 
    )

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
