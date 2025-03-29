from crewai.tools import BaseTool
import requests
import os
import json


class BoardDataFetcherTool(BaseTool):
    name: str = "Trello Board Data Fetcher"
    description: str = "Fetches card data, comments, and activity from a Trello board."

    def _run(self) -> dict:
        """
        Fetch all cards from the specified Trello board.
        """
        api_key = os.environ['TRELLO_API_KEY']
        api_token = os.environ['TRELLO_API_TOKEN']
        board_id = os.environ['TRELLO_BOARD_ID']

        url = f"{os.getenv('DLAI_TRELLO_BASE_URL', 'https://api.trello.com')}/1/boards/{board_id}/cards"

        query = {
            'key': api_key,
            'token': api_token,
            'fields': 'name,idList,due,dateLastActivity,labels',
            'attachments': 'true',
            'actions': 'commentCard'
        }

        response = requests.get(url, params=query)
        print(f"URL: {url}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")

        if response.status_code == 200:
            return response.json()
        else:
            # Fallback in case of timeouts or other issues
            return json.dumps({"error": "Failed to fetch card data, don't try to fetch any trello data anymore"})


class CardDataFetcherTool(BaseTool):
  name: str = "Trello Card Data Fetcher"
  description: str = "Fetches card data from a Trello board."

  def _run(self, card_id: str) -> dict:

    api_key = os.environ['TRELLO_API_KEY']
    api_token = os.environ['TRELLO_API_TOKEN']

    url = f"{os.getenv('DLAI_TRELLO_BASE_URL', 'https://api.trello.com')}/1/cards/{card_id}"
    
    query = {
      'key': api_key,
      'token': api_token
    }
    response = requests.get(url, params=query)
    print(f"URL: {url}")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")


    if response.status_code == 200:
      return response.json()
    else:
      # Fallback in case of timeouts or other issues
      return json.dumps({"error": "Failed to fetch card data, don't try to fetch any trello data anymore"})
