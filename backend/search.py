# Import necessary modules
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import json
import time
import asyncio
from backend.summarize import (
    summarize_article,
    query_is_valid,
    parse_srt,
    generate_prompt,
    generate_image,
    transcriber_chain,
)
from backend.transcriber import Transcriber
from backend.video_render import VideoCreator
from backend.podcast_script import generate_script, save_script_to_json
from backend.podcast import generate_podcast

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
    topic: str


class SummarizeRequest(BaseModel):
    title: str


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
        "exclude_domains": [],  # default
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


# Define the POST endpoint for podcast  generation
@app.post("/generate_podcast")
def generate_podcast_endpoint(request: SummarizeRequest):
    # Path to the search results JSON file
    results_file = "results/search_results.json"

    # Check if the search results file exists
    if not os.path.exists(results_file):
        raise HTTPException(
            status_code=404,
            detail="Search results not found. Please perform a search first.",
        )

    # Load the search results
    try:
        with open(results_file, "r") as json_file:
            search_results = json.load(json_file)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Failed to decode search results JSON."
        )

    # Find the result with the matching title
    result = next(
        (
            item
            for item in search_results.get("results", [])
            if item.get("title") == request.title
        ),
        None,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No search result found with title: {request.title}",
        )

    raw_content = result.get("raw_content")

    if not raw_content:
        raise HTTPException(
            status_code=404, detail="Raw content not available for the selected title."
        )

    # Generate the podcast script
    podcast_script = generate_script(raw_content)
    if not podcast_script:
        raise HTTPException(
            status_code=500, detail="Failed to generate podcast script."
        )
    save_script_to_json(podcast_script)

    filename = "results/podcast_script.json"
    with open(filename, "r") as json_file:
        podcast_data = json.load(json_file)

    # Run the podcast generation asynchronously
    asyncio.run(generate_podcast(podcast_data))


# Define the POST endpoint for summarization
@app.post("/summarize")
async def summarize_content(request: SummarizeRequest):
    # Path to the search results JSON file
    results_file = "results/search_results.json"

    # Check if the search results file exists
    if not os.path.exists(results_file):
        raise HTTPException(
            status_code=404,
            detail="Search results not found. Please perform a search first.",
        )

    # Load the search results
    try:
        with open(results_file, "r") as json_file:
            search_results = json.load(json_file)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Failed to decode search results JSON."
        )

    # Find the result with the matching title
    result = next(
        (
            item
            for item in search_results.get("results", [])
            if item.get("title") == request.title
        ),
        None,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No search result found with title: {request.title}",
        )

    raw_content = result.get("raw_content")

    if not raw_content:
        raise HTTPException(
            status_code=404, detail="Raw content not available for the selected title."
        )

    # Call the summarize function on the raw_content
    try:
        titles_scripts_questions = summarize_article(raw_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")

    # Return the result
    results = []
    for result in titles_scripts_questions:
        results.append(
            {
                "title": result.title,
                "script": result.script,
                "follow_up_question": result.follow_up_question,
                "caption": result.caption,
            }
        )

    with open("results/summaries.json", "w") as json_file:
        json.dump(results, json_file, indent=2)

    return results


# Define the POST endpoint for transcribing
@app.post("/transcribe")
def transcribe(request: SummarizeRequest):
    # Path to the search results JSON file
    results_file = "results/summaries.json"
    with open(results_file, "r") as json_file:
        search_results = json.load(json_file)
    # Find the result with the matching title
    result = next(
        (item for item in search_results if item.get("title") == request.title),
        None,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No search result found with title: {request.title}",
        )

    title = result.get("title")
    script = result.get("script")
    text = f"{title}\n{script}"

    transcriber = Transcriber(
        text,
        "results/output.mp3",
        "results/output_subtitles.vtt",
        "results/output_images.vtt",
        "results/output_subtitles.srt",
        "results/output_images.srt",
    )
    asyncio.run(transcriber.generate_audio_and_convert())
    # transcriber.generate_audio_and_convert()

    return {"message": "Transcription completed successfully."}


# Define the POST endpoint for generating images
@app.get("/generate_images")
async def generate_images():
    if not os.path.exists("results/output_subtitles.srt"):
        raise HTTPException(
            status_code=404,
            detail="Subtitles not found. Please transcribe the content first."
        )

    # Path to your SRT file
    srt_file_path = "results/output_images.srt"

    # Parse the SRT file
    subtitles = parse_srt(srt_file_path)

    # Step 1: Generate prompts for all subtitles
    prompts = []
    for sub in subtitles:
        index = sub['index']
        content = sub['content']

        # Generate image prompt using Mistral model
        prompt = generate_prompt(content, transcriber_chain)
        print(f"Subtitle {index}: {content}")
        print(f"Generated Prompt: {prompt}\n")

        # Store the prompt with its index
        prompts.append({'index': index, 'prompt': prompt})
        await asyncio.sleep(1.5)

    # Remove existing files from results/images
    image_dir = 'results/images'
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            file_path = os.path.join(image_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file: {e}")
    else:
        os.makedirs(image_dir, exist_ok=True)

    # Step 2: Generate images from the prompts asynchronously
    tasks = []
    async with aiohttp.ClientSession() as session:
        for item in prompts:
            index = item['index']
            prompt = item['prompt']

            # Schedule the generate_image coroutine
            task = asyncio.create_task(generate_image(index, prompt, session))
            tasks.append(task)

        # Optionally, limit concurrency using a semaphore
        # semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent tasks
        # async def sem_task(task):
        #     async with semaphore:
        #         await task

        # tasks = [sem_task(task) for task in tasks]

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

    return {"message": "Images generated successfully."}



@app.get("/generate_video")
async def generate_video():
    input_folder = "results/images"
    output_folder = "results/resized_images"
    target_size = (1080, 1920)
    audio_path = "results/output.mp3"
    srt_path = "results/output_subtitles.srt"
    image_srt_path = "results/output_images.srt"
    output_path = "results/output_video.mp4"

    video_creator = VideoCreator(
        input_folder,
        output_folder,
        target_size,
        audio_path,
        srt_path,
        image_srt_path,
        output_path,
    )
    video_creator.render_video()

    return {"message": "Video generated successfully."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
