import srt

from langchain_core.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI


def parse_srt(file_path):
    """
    Parse the SRT file and return a list of subtitles.
    """
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
    """
    Generate an image prompt based on the subtitle text using the LLM chain.
    """
    input_text = subtitle_text.strip()
    input_text += "DO NOT ADD ANY TEXT."
    prompt = llm_chain.predict(subtitle=input_text)
    return prompt.strip()

def load_mistral_chain():
    """
    Load the Mistral LLM chain with the specified prompt template.
    """
    # Initialize the Mistral model via LangChain
    llm = ChatMistralAI(
        model="mistral-small-latest",
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
    llm_chain = prompt_template | llm
    return llm_chain
