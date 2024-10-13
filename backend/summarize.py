from pydantic import BaseModel, Field
from typing import List
import os
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
import srt
from PIL import Image
from io import BytesIO
import time


llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
)

class ArticleTopic(BaseModel):
    title: str = Field(
        ...,
        title="Topic Title",
        # description="The title of one of the key topics extracted from the article.",
    )
    script: str = Field(
        ...,
        title="Educational Script",
        # description=(
        #     "A concise (max 150 words) educational script of the topic suitable for a 1-minute educational social media reel. "
        #     "It should teach valuable insights, use clear and engaging language, and encourage deeper thinking or action."
        # ),

    )
    follow_up_question: str = Field(
        ...,
        title="Follow-Up Question",
        # description=(
        #     "A thought-provoking, exploratory question related to the topic that encourages viewers to watch more videos on the subject. "
        #     "It should introduce a related but distinct aspect of the topic not covered in the script and entice viewers to engage with additional content."
        # ),
    )
    caption: str = Field(
        ...,
        title="Social Media Caption",
    )

    def __str__(self):
        return f"{self.title}: {self.summary}. {self.question}"


class ArticleTopics(BaseModel):
    topics: List[ArticleTopic] = Field(
        ...,
        title="List of Article Topics",
        description="A list containing five key topics and their corresponding educational summaries.",
        min_length=3,
        max_length=5,
    )

    def __str__(self):
        return "\n".join(str(topic) for topic in self.topics)

    def __len__(self):
        return len(self.topics)

    def __iter__(self):
        return iter(self.topics)

    def __getitem__(self, i):
        return self.topics[i]


llm_structured = llm.with_structured_output(ArticleTopics)


prompt_template = PromptTemplate(
    input_variables=["article"],
    template="""
1. **Article Analysis:**
   - Read the provided article carefully:

<article>
{article}
</article>

2. **Topic Identification:**
   - Identify **five** key topics of interest discussed in the article.
   - These should be the most significant or intriguing points that would capture an audience's attention for short-form social media content like TikTok reels.

3. **Educational Content:**
   - For each of the five identified topics, write a (atleast 200 words) educational script suitable for a social media short form content.
   - Each script should:
     - Teach the audience something valuable or insightful about the topic.
     - Use clear and engaging language appropriate for a general audience.
     - Highlight interesting facts, explanations, or tips related to the topic.
     - Encourage the audience to think more deeply or take action related to the subject.
     - Do not provide hash tags in the script.

4. **Reflection Questions:**
   - For each of the five topics, create a thought-provoking, open-ended question that encourages critical thinking, reflection, or discussion.
   - Each question should:
     - Be related directly to the corresponding topic.
     - Invite diverse perspectives and engagement.
     - Stimulate deeper understanding or exploration of the topic.

5. **Social media caption for video:**
    - Write a concise social media caption for the video that would be used to promote the video on Instagram or TikTok.
    - This should include hash tags and emojis in addition to the caption.

**Additional Guidelines:**

- **Originality:** Ensure that both summaries and follow-up questions are original and not copied directly from the article. They should be inspired by the article's content.
- **Clarity:** Avoid using technical jargon; if necessary, briefly explain any complex terms.
- **Engagement:** Focus on the most important and engaging aspects of each topic to include in the summaries and questions.
- **Theme Emphasis:** Remember that the content is intended for social media educational platforms. It should be engaging, concise, and optimized for platforms like TikTok reels where attention spans are short.

""".strip()
)

summary_chain = prompt_template | llm_structured

def summarize_article(article: str) -> ArticleTopics:
    result = summary_chain.invoke(input={"article": article})
    return result

def query_is_valid(topic: str) -> bool:
    response =  llm.invoke(f"Is the query relevant to healthcare? Return True if yes, False otherwise. \n Query: {topic}")
    content = response.content.lower()
    return "true" in content or "yes" in content


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
    prompt = llm_chain.invoke({"subtitle": input_text}).content
    return prompt.strip()

def load_mistral_chain():
    """
    Load the Mistral LLM chain with the specified prompt template.
    """
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

transcriber_chain = load_mistral_chain()

async def generate_image(index, prompt, session):
    """
    Generate an image using the Hugging Face API asynchronously and save it to the results/image/ folder.
    """
    API_URL = "https://a39i6lutw4cmb1ag.us-east-1.aws.endpoints.huggingface.cloud/"
    headers = {
        "Accept": "image/png",
        "Content-Type": "application/json",
        # Include authorization if required
        # "Authorization": f"Bearer {API_TOKEN}",
    }

    async def query(payload):
        async with session.post(API_URL, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.read()

    try:
        payload = {
            "inputs": prompt,
            "parameters": {}
        }

        output = await query(payload)

        # Open the image from bytes
        image = Image.open(BytesIO(output))

        # Ensure the results directory exists
        image_dir = 'results/images/'
        os.makedirs(image_dir, exist_ok=True)

        # Generate a filename with index
        image_filename = f"{index}.png"
        image_path = os.path.join(image_dir, image_filename)

        # Check if the file exists
        if os.path.exists(image_path):
            # Append a timestamp to make it unique
            timestamp = int(time.time())
            image_filename = f"{index}{timestamp}.png"
            image_path = os.path.join(image_dir, image_filename)

        # Save the image
        image.save(image_path)
        print(f"Image saved to {image_path}\n")

    except Exception as e:
        print(f"Error generating image for subtitle {index}: {e}")

if __name__ == "__main__":
    article = """8 Mental Health Trends to Watch in 2022
""".strip()
    
    print("Summarizing article...")
    result = summary_chain.invoke(input={"article": article})

    for example in result:
        print("===== TITLE =====")
        print(example.title)
        print("===== SUMMARY =====")
        print(example.script)
        print("===== QUESTION =====")
        print(example.follow_up_question)
        print()
