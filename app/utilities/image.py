# get image urls from webservice
import requests


class Image():
    def __init__(self) -> None:
        pass

    async def get_images():
        url = "https://photo-voting.hiring.ipums.org/images/"

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request(
            "GET", url, headers=headers).json()

        with open("images.txt", mode="w") as f:
            for url in response['data']:
                f.write(url + '\n')
        return response
