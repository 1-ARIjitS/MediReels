from pydantic import BaseModel, Field
from typing import List
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate

llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.5,
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
   - For each of the five identified topics, write a concise (approximately 150 words) educational script suitable for a 1-minute video reel.
   - Each script should:
     - Teach the audience something valuable or insightful about the topic.
     - Use clear and engaging language appropriate for a general audience.
     - Highlight interesting facts, explanations, or tips related to the topic.
     - Encourage the audience to think more deeply or take action related to the subject.

4. **Reflection Questions:**
   - For each of the five topics, create a thought-provoking, open-ended question that encourages critical thinking, reflection, or discussion.
   - Each question should:
     - Be related directly to the corresponding topic.
     - Invite diverse perspectives and engagement.
     - Stimulate deeper understanding or exploration of the topic.

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
    return "true" in content


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
