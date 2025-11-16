import requests

def main():
    print("Hello from uv!")



    # Define the URL to make the request to
    url = "https://httpbin.org/get"

    try:
        # Make a GET request
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("Request successful!")
            # Print the response content (usually JSON for httpbin.org)
            print("Response JSON:")
            print(response.json())
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response text: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")


if __name__ == "__main__":
    main()
