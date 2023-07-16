import requests

def send_file_via_api(file_path, api_url):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(api_url, files=files)
        return response