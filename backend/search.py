# Import necessary modules
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import json
from backend.summarize import summarize_article, query_is_valid

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

# Define a Pydantic model for the summarize request body
class SummarizeRequest(BaseModel):
    title: str  # Title of the search result to summarize

# Define the GET endpoint to check if the query is valid
@app.get("/is_valid")
async def is_valid_query(topic: str):
    # Check if the query is valid
    return {"is_valid": query_is_valid(topic)}

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
        if not os.path.exists("results"):
            os.makedirs("results")
        with open("results/search_results.json", "w") as json_file:
            json.dump(search_results, json_file, indent=4)

        # Return the search results to the client as well
        return search_results

    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


# Define the POST endpoint for summarization
@app.post("/summarize")
async def summarize_content(request: SummarizeRequest):
    # Path to the search results JSON file
    results_file = "results/search_results.json"

    # Check if the search results file exists
    if not os.path.exists(results_file):
        raise HTTPException(status_code=404, detail="Search results not found. Please perform a search first.")

    # Load the search results
    try:
        with open(results_file, "r") as json_file:
            search_results = json.load(json_file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to decode search results JSON.")

    # Find the result with the matching title
    result = next((item for item in search_results.get("results", []) if item.get("title") == request.title), None)

    if not result:
        raise HTTPException(status_code=404, detail=f"No search result found with title: {request.title}")

    raw_content = result.get("raw_content")

    if not raw_content:
        raise HTTPException(status_code=404, detail="Raw content not available for the selected title.")

    # Call the summarize function on the raw_content
    try:
        titles_scripts_questions = summarize_article(raw_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")

    # Return the result
    results = []
    for result in titles_scripts_questions:
        results.append({"title": result.title, "script": result.script, "follow_up_question": result.follow_up_question})

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

