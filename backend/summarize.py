from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from typing import List
from langchain_mistralai import ChatMistralAI

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
)

class ArticleTopic(BaseModel):
    title: str = Field(
        ...,
        title="Topic Title",
        description="The title of one of the key topics extracted from the article.",
        examples=[
            "The Impact of Telemedicine on Rural Healthcare",
            "Advancements in Personalized Medicine",
            "The Role of Artificial Intelligence in Diagnostic Imaging",
            "Mental Health Awareness in the Workplace",
            "Innovations in Minimally Invasive Surgical Techniques",
        ],
    )
    script: str = Field(
        ...,
        title="Educational Script",
        description=(
            "A concise (max 150 words) educational script of the topic suitable for a 1-minute educational social media reel. "
            "It should teach valuable insights, use clear and engaging language, and encourage deeper thinking or action."
        ),
        examples=[
            (
                "Telemedicine has revolutionized access to healthcare in rural areas "
                "by enabling remote consultations, reducing the need for travel, and providing timely medical advice. This innovation "
                "has led to improved patient outcomes and greater convenience for both patients and healthcare providers. Stay tuned to learn "
                "more about how telemedicine is transforming healthcare delivery."
            ),
            (
                "Personalized medicine tailors medical treatment to individual characteristics, "
                "such as genetics, lifestyle, and environment. This approach enhances the effectiveness of therapies and minimizes adverse effects, "
                "marking a significant advancement in patient care. Discover how personalized medicine is shaping the future of healthcare."
            ),
            (
                "AI enhances the accuracy and speed of image analysis, "
                "assisting radiologists in detecting abnormalities early. These AI tools can analyze vast amounts of data quickly, leading to more efficient "
                "and reliable diagnoses. Learn how AI is revolutionizing diagnostic processes in healthcare."
            ),
            (
                "Recognizing and addressing mental health issues among employees is crucial. "
                "Implementing supportive policies and fostering open dialogues can significantly improve overall well-being and productivity. Find out how workplaces "
                "are prioritizing mental health."
            ),
            (
                "Let's discuss Innovations in Minimally Invasive Surgical Techniques. These techniques reduce recovery time and minimize scarring by utilizing "
                "smaller incisions and advanced technology. Innovations in this field lead to fewer complications and better patient outcomes compared to traditional surgery. "
                "Stay with us to learn more about these groundbreaking surgical advancements."
            ),
        ],
    )
    follow_up_question: str = Field(
        ...,
        title="Follow-Up Question",
        description=(
            "A thought-provoking, exploratory question related to the topic that encourages viewers to watch more videos on the subject. "
            "It should introduce a related but distinct aspect of the topic not covered in the script and entice viewers to engage with additional content."
        ),
        examples=[
            "Do you know how telemedicine has evolved with the introduction of wearable health devices?",
            "What are the latest breakthroughs in personalized medicine that could revolutionize treatment plans?",
            "How is artificial intelligence transforming patient care beyond diagnostic imaging?",
            "Can workplace mental health programs reduce employee turnover?",
            "What are the future trends in minimally invasive surgeries that could change patient recovery times? Stay tuned to learn more!",
        ],
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

from langchain_core.prompts import PromptTemplate

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


if __name__ == "__main__":
    article = """8 Mental Health Trends to Watch in 2022\nKeep an eye out for these emerging trends and exciting new research developments in mental health in the new year.\nMental health became an important part of the public conversation in 2021, as Olympic athletes, celebrities, and other public figures came forward about their well-being and helped reduce the stigma.\nAs we enter the third year of the pandemic, we can expect mental health to continue to be a top priority in 2022, particularly as the United States reckons with a growing mental health crisis.\nIn fact, a recent poll by the American Psychiatric Association showed that one-quarter of Americans made a new year\u2019s resolution to improve their mental health in 2022.\nAlthough 2021 wasn\u2019t without its challenges, the past year brought growth, understanding, and hopefully, renewed optimism.\nNew developments in science, such as the COVID-19 vaccines, are a testament to humanity\u2019s commitment to healing.\nOther exciting research studies have shown us how we can improve mental health services, address racial and socioeconomic disparities, and ultimately, enhance our overall well-being from the inside out.\nSuffice it to say, there\u2019s a lot happening in the mental health space \u2014 too much for one article alone. To determine our top mental health trends of 2022, we consulted experts in the field and Psych Central\u2019s Medical Affairs Team.\nNote that some of these trends aren\u2019t yet available, but we expect a continued increase in research and accessibility in the months to come.\n1. Trauma-informed care\nNearly 61% of adults have experienced at least one traumatic event in their lifetimes, according to the Adverse Childhood Experiences (ACES) study.\nAround 1 in 6 adults endure four or more traumatic events during childhood, with women and people from minoritized communities facing a greater risk.\nClinicians, health care practitioners, educators, and mental health professionals are widely embracing a trauma-informed approach to care to address trauma among the broader population.\nTrauma-informed care will only continue to be emphasized in 2022, according to Nathaniel Ivers, PhD, department chair and associate professor at Wake Forest University in Winston-Salem, North Carolina.\nFor trauma-informed care to be effective, Ivers emphasizes the need for a holistic approach that includes treatments and strategies that play to an individual\u2019s strengths versus their weaknesses. In some cases, trauma-informed care could run the risk of hyper-focusing on an individual\u2019s trauma exclusively, rather than homing in on an individual\u2019s strengths to effectively understand and treat them.\n2. Blood tests for mental illness\nSoon, you could have the option to take a blood test to easily detect a mental health condition like depression.\nIn April 2021, researchers at the Indiana University School of Medicine developed a novel blood test for mental illness, suggesting that biological markers for mood disorders can be found within RNA biomarkers.\nThe breakthrough study indicated that a blood test can determine the severity of depression and the risk for developing severe depression and bipolar disorder in the future. The blood test may also help tailor an individual\u2019s medication choices.\n\u201cThis is an exciting prospect for identifying biological markers of depression among researchers, but very preliminary in its understanding and potential for use,\u201d says Matthew Boland, PhD, a clinical psychologist in Reno, Nevada, and a member of Psych Central\u2019s Medical Affairs Team.\nAlthough blood tests for mental illnesses are still in their early development stages, this scientific advancement could change, even improve, how mental health conditions are diagnosed, which is often by trial and error.\n\u201cThis method will remain an adjunctive to traditional diagnostic tools, as mental illnesses are complex and have biological, psychological, and sociocultural etiologies,\u201d Ivers adds.\n3. Advancements in psychedelic research\nPsychedelics have been used for religious, medical, and ceremonial purposes around the world for centuries, predominantly among Indigenous cultures.\nAnd recent research suggests that psychoactive substances like psilocybin, MDMA, LSD, and ketamine can help treat mental health conditions like depression, anxiety, and more.\nAlthough psychedelics are still classified as controlled substances and illegal in many countries, including the United States, laws, policies, and stigma are starting to ease up.\nFor instance, the Drug Enforcement Administration (DEA) recently authorized an increase in the production of psychedelics to meet growing research demands.\nFrom Yale to Johns Hopkins to New York University, to the newly minted Center for Psychedelic Research and Therapy at the University of Texas, research scientists are becoming increasingly interested in the therapeutic value of psychedelics and other psychoactive substances.\nIn addition, emerging research shows the potential mental health benefits of psychedelic-assisted psychotherapy (PAP), a form of therapy combined with ingesting a psychoactive substance.\n\u201cAdjunctive therapy is needed to keep old habits [from] solidifying following dosing,\u201d Boland says. \u201cMore established methods will be slower to adopt, partially due to legality and awaiting increased research findings for efficacy for many specific conditions.\u201d\nWhile psychedelic therapy is still at least a few years away from being offered at your therapist\u2019s office, we\u2019ll likely continue to see more scientific discoveries on the possible benefits.\n4. Setting healthy boundaries with social media\nIf you have a smartphone, you\u2019re probably well aware that limiting your screen time can be a challenge. Not to mention, spending too much time online can negatively affect your well-being.\nAnd if you\u2019ve watched Netflix\u2019s \u201cThe Social Dilemma,\u201d you\u2019re familiar that Facebook, Instagram, and Pinterest specifically designed these apps to hold your attention for as long as possible.\nYou might also recall when a former Facebook employee testified before Congress in October 2021 on the negative effects of Instagram on teens\u2019 mental health, which was dovetailed by a global Facebook outage.\nThe events sparked an overdue dialogue about the potentially harmful effects of social media platforms and the need for taking an occasional break.\nWe can expect to hear more conversations about \u201cdigital wellness\u201d and establishing healthy boundaries with social media, particularly as research continues to shed light on the negative effects on adolescents and adults alike.\n\u201cLarger overall scrutiny of the effects of social media on mental health will likely continue and increase,\u201d Boland says. \u201cWhether or not that translates to definitive action by lawmakers may be a different story.\u201d\nWhat \u201csocial media boundaries\u201d might look like will vary based on the individual, and whether they\u2019re effective is still up for debate. While more research is needed, Boland suggests that setting the following boundaries can be helpful:\nAccording to Ivers, the mental health effects of \u201cdoom scrolling\u201d and virtual privacy could see more traction in 2022 as well.\n\u201cI also believe there will be an increase in discussions about the disproportionate influence of social media on people\u2019s ideas, attitudes, and behaviors, particularly for impressionable youth,\u201d Ivers says.\n5. Artificial intelligence in clinical settings\nAdvancements in artificial intelligence (AI) technologies could improve the future of therapy sessions and mental health diagnoses. According to research published in December 2021, AI motion sensors can be used to detect symptoms of anxiety such as:\nAdditionally, research from October 2021 suggests that AI can help train therapists by evaluating their skills, including whether or not they\u2019re creating an optimal environment for their clients.\nAlthough the use of AI in mental health training and treatment could increase in the new year and beyond, experts say the technology is unlikely to replace traditional mental health services with human beings.\n6. Continued expansion in telehealth services\nTherapy administered via telemental health picked up steam in 2020, sustained in 2021, and is here to stay, according to experts.\n\u201cBecause of the COVID-19 pandemic, many mental health professionals now have the training, experience, confidence, and technology to conduct telemental health services effectively and ethically,\u201d Ivers says. \u201cIt also has the potential to increase mental health treatment access to rural and older adult communities.\u201d\nAccording to Boland, around 60% of mental health practitioners currently have full caseloads solely on telehealth.\n\u201cClients largely appear to enjoy the convenience \u2014 only a few clients have requested in-person,\u201d Boland says. \u201cSome mental health and business analysts project that telemental health could expand even more.\u201d\nVirtual mental health services can be especially helpful for those who:\n7. Increase in transcranial magnetic stimulation\nTranscranial magnetic stimulation (TMS), a non-invasive method of brain stimulation, has been studied extensively in recent years and is being increasingly used to treat certain mental health conditions.\nThe safety and efficacy have been so promising that the Food and Drug Administration (FDA) continues to approve innovative TMS technologies like NeuroStar and BrainsWay. TMS stimulates areas of the brain that are known to be underactive in individuals with mental health conditions such as:\n\u201cIf depression levels continue to increase, I suspect that TMS will be utilized more frequently in 2022, especially for individuals whose depression is not improving with traditional methods,\u201d Ivers says.\n8. Virtual reality for chronic pain and care\nThe FDA recently authorized marketing for a virtual reality (VR) program for chronic pain reduction as an alternative to opioid prescriptions.\nVR treatments could be revolutionary, offering a different type of therapy for folks who wish to avoid pain medication to relieve their symptoms.\n\u201cPeople are put into a virtual world where they conduct movements, learn about the nature of pain sensations in their body, and learn a number of behavioral and cognitive skills on how to effectively respond to pain and cope with the stress associated with it,\u201d Boland says.\n\u201c[VR] is meant to work along with medication, physical treatments, and behavioral clinician work,\u201d he adds.\nAs VR technology becomes more accessible, experts say we\u2019ll see a continued expansion for treatments for different mental health and medical conditions.\n\u201cAs virtual worlds become more prevalent and useful and as the metaverse evolves, I believe that medical and mental health professionals will find ways to help clients through these technologies,\u201d Ivers says.\nLooking ahead\n2021 was an innovative year for scientific research in the mental health space \u2014 and we\u2019re excited to see what 2022 has in store.\nFrom trauma-informed care to psychedelic research to artificial intelligence and virtual reality, there are many exciting developments to be on the lookout for, especially as we all become a little more comfortable talking about our mental health.\nIf you\u2019re curious as to what the future holds, you may wish to check back for more updates. We\u2019ll continue to share the latest research, technologies, therapies, and resources that we believe will revolutionize how we approach our mental wellness.\nIn the meantime, we wish you a happy, healthy, and safe new year and hope you\u2019re able to take good care of yourself in 2022 and beyond.\nLast medically reviewed on\nJanuary 3, 2022\n11 sourcescollapsed\nRead this next\nEditor in chief Faye McCray reflects on Psych Central's first year as part of Healthline Media.\nIt's been over a year since COVID-19 lockdowns were put in place. How is your mental health?\nThe U.S. surgeon general has released an advisory about the pandemic's effects on the youth mental health crisis, especially in marginalized groups.\nChange begins with brave conversations, but just talking about mental health isn't enough to reduce stigma. Here are common stigmas and how to reduce\u2026\nI was a third-year medical student when I discovered my calling to become a psychiatrist. To this day, I remem\nChanging your antidepressant can be an overwhelming task, but there are ways you can manage it and make the best decision for you.\nApps, podcasts, YouTube channels \u2014 we've compiled the 9 best online guided meditation options.\nIf you've noticed a change in your relationship after the pandemic, you\u2019re not alone. But there are ways to get back on track.\nHere's what you need to know about serotonin and how it works in your body, including signs of low and high serotonin levels.\nOUR BRANDS
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
