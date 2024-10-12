# generate_images_from_srt_with_mistral.py

import os
import srt
import uuid
import time
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_mistralai import ChatMistralAI
from google.cloud.aiplatform.gapic import PredictionServiceClient

# Load environment variables from .env file
load_dotenv()

# Get variables from environment
PROJECT_ID = os.getenv('PROJECT_ID')
REGION = os.getenv('REGION')
ENDPOINT_ID = os.getenv('ENDPOINT_ID')

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    subtitles = list(srt.parse(srt_content))
    parsed_subtitles = []
    for sub in subtitles:
        parsed_subtitles.append({
            'index': sub.index,
            'start_time': sub.start,
            'end_time': sub.end,
            'content': sub.content.replace('\n', ' ')
        })
    return parsed_subtitles

def generate_prompt(subtitle_text, llm_chain):
    # Use the LLM chain to generate the image prompt using 'predict'
    input_text = subtitle_text.strip()
    prompt = llm_chain.predict(subtitle=input_text)
    return prompt.strip()

def load_mistral_chain():
    # Initialize the Mistral model via LangChain
    llm = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0,
        max_retries=2,
    )

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["subtitle"],
        template="""
You are an AI assistant that generates detailed and creative image prompts for an AI image generator based on subtitles from a video script.

Given the subtitle:
"{subtitle}"

Generate a clear, informative, and engaging image prompt that accurately represents the key concepts of the subtitle. Avoid adding unnecessary or bizarre elements. Ensure the prompt is suitable for generating an image that effectively visualizes the subtitle's content.
Image Prompt:
""".strip()
    )

    # Create the LLM chain
    llm_chain = LLMChain(prompt=prompt_template, llm=llm)
    return llm_chain

def generate_image(prediction_client, endpoint, index, prompt):
    # Prepare the instance for prediction
    instance = {
        "prompt": prompt,
        "width": 512,
        "height": 512,
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "num_images": 1,  # Uncomment if the model supports this parameter
    }
    #instances = [instance]

    # Send the prediction request
    response = prediction_client.predict(
        endpoint=endpoint,
        instances=instance
    )

    # Handle the response
    if response.predictions:
        # Get only the first prediction
        prediction = response.predictions[0]

        # Decode the base64 image
        import base64
        from PIL import Image
        from io import BytesIO

        image_data = base64.b64decode(prediction)
        image = Image.open(BytesIO(image_data))

        # Generate a filename with index
        image_filename = f"{index}.png"
        image_path = os.path.join(RESULTS_DIR, image_filename)

        # Check if the file exists
        if os.path.exists(image_path):
            # Append a timestamp to make it unique
            timestamp = int(time.time())
            image_filename = f"{index}_{timestamp}.png"
            image_path = os.path.join(RESULTS_DIR, image_filename)

        # Save the image
        image.save(image_path)
        print(f"Image saved to {image_path}\n")
    else:
        print(f"No predictions received for subtitle {index}")

def main():
    # Record the start time
    start_time = time.time()

    # Path to your SRT file
    srt_file_path = './results/output2.srt'  # Replace with the path to your SRT file

    # Parse the SRT file
    subtitles = parse_srt(srt_file_path)

    # Ensure the results directory exists
    global RESULTS_DIR  # Declare as global since we're using it in another function
    RESULTS_DIR = 'results/images/'
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Load the Mistral LLM chain
    llm_chain = load_mistral_chain()

    # Initialize the Vertex AI Prediction client
    client_options = {"api_endpoint": f"{REGION}-aiplatform.googleapis.com"}
    prediction_client = PredictionServiceClient(client_options=client_options)

    endpoint = prediction_client.endpoint_path(PROJECT_ID, REGION, ENDPOINT_ID)
    print(f"Using endpoint: {endpoint}")

    # Step 1: Generate prompts for all subtitles
    prompts = []
    for sub in subtitles:
        index = sub['index']
        content = sub['content']

        # Generate image prompt using Mistral model
        prompt = generate_prompt(content, llm_chain)
        print(f"Subtitle {index}: {content}")
        print(f"Generated Prompt: {prompt}\n")

        # Store the prompt with its index
        prompts.append({'index': index, 'prompt': prompt})

    # Step 2: Generate images from the prompts
    for item in prompts:
        index = item['index']
        prompt = item['prompt']

        # Generate image via Vertex AI Prediction
        try:
            generate_image(prediction_client, endpoint, index, prompt)
        except Exception as e:
            print(f"Error during prediction for subtitle {index}: {e}")
            continue  # Proceed to the next prompt

    # Record the end time
    end_time = time.time()

    # Calculate and print the total execution time
    total_time = end_time - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")

if __name__ == '__main__':
    main()
