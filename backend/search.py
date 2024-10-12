# Import necessary modules
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import json

# Step 1: Load environment variables from the .env file
load_dotenv()

# Step 2: Retrieve the API key from the environment variables
api_key = os.getenv("SEARCH_API_KEY")

# Step 3: Check if the API key was loaded successfully
if not api_key:
    raise ValueError("API key not found. Please set SEARCH_API_KEY in your .env file.")

# Initialize FastAPI app
app = FastAPI()

# Define a Pydantic model for the request body
class SearchRequest(BaseModel):
    topic: str  # Only the topic comes from the frontend

# Define the POST endpoint for Tavily search
@app.post("/search")
async def search_tavily(request: SearchRequest):
    # Define the Tavily API endpoint
    url = "https://api.tavily.com/search"

    # Prepare the payload for the Tavily request
    payload = {
        "api_key": api_key,
        "query": "Trending topics in " + request.topic,
        "search_depth": "advanced",  # default
        "topic": "general",  # default
        "days": 180,  # default
        "max_results": 5,  # default
        "include_images": False,  # default
        "include_image_descriptions": False,  # default
        "include_answer": False,  # default
        "include_raw_content": True,  # default
        "include_domains": [],  # default
        "exclude_domains": []  # default
    }

    try:
        # Send the POST request to the Tavily API
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        search_results = response.json()

        # Write the response to a JSON file
        with open("results/search_results.json", "w") as json_file:
            json.dump(search_results, json_file, indent=4)

        # Return the search results to the client as well
        return search_results

    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
