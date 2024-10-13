import os
import json
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
# from gtts import gTTS

# Load environment variables from the .env file
load_dotenv()

# Get the Mistral API key from the environment
mistral_api_key = os.getenv("MISTRAL_API_KEY")

if not mistral_api_key:
    raise ValueError("MISTRAL_API_KEY not found in the environment variables!")

# Step 1: Initialize Mistral Model
def generate_script(article_text):
    # Initialize Mistral API
    llm = ChatMistralAI(
        model="mistral-large-latest",
        api_key=mistral_api_key,  # Pass API key to authenticate
        temperature=0.7,
        max_retries=2,
    )
    
    # Step 2: Craft a strong prompt for podcast script
    prompt = f"""You are an expert scriptwriter for podcasts on health and medical-related topics. I want you to create an engaging, conversational podcast script based on the following article text. The podcast should have multiple speakers, with at least one host and one guest who is a medical professional. The tone should be informative but easy to understand, and the conversation should be lively, filled with insights, relatable examples, and moments of interaction like humor or personal anecdotes.

    The output format should be in JSON format as follows:
    {{
      "podcast_title": "",
      "intro_music": "[Intro music description]",
      "host_name": "",
      "guest_name": "",
      "conversation": [
          {{"host": "Text spoken by the host"}},
          {{"guest": "Text spoken by the guest"}},
          {{"host": "Text spoken by the host"}},
          {{"guest": "Text spoken by the guest"}}
      ],
      "outro_music": "[Outro music description]",
      "end_of_show": "End of podcast."
    }}

    Ensure that the podcast includes the following:
    - Length: The script should be structured to generate a podcast of at least 5000 words.
    - Flow: Ensure a clear introduction, middle, and conclusion, covering the topic in depth.
    - Host & Guest: The host should be friendly, curious, and ask relevant questions, while the guest should be a knowledgeable medical professional, providing insightful, accurate, and approachable responses.
    - Audience Engagement: Use tips, relatable examples, and address common health concerns. Include moments of humor or personal stories to make the conversation engaging.
    - Content: Break the conversation into smaller parts to ensure smooth transitions and varied pacing.

    Here is the article text to use as the basis for the podcast script:
    {article_text}
    """
    
    # Step 3: Call the model and get the response using 'invoke()'
    try:
        # Use 'invoke' method to generate the script
        response = llm.invoke(prompt)  
        script = response.content
        
        return script

    except Exception as e:
        print(f"Error generating script: {e}")
        return None

# Save the generated podcast script to a JSON file
def save_script_to_json(script, filename='podcast_script.json'):
    # Ensure the directory exists
    os.makedirs('results', exist_ok=True)
    script= script.strip()
    script= script[7:-3]
    dict= json.loads(script)
    
    # Create the full file path
    file_path = os.path.join('results', filename)
    
    # Write the script to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(dict, json_file, indent=4)

    print(f"Podcast script saved to {file_path}")

if __name__ == "__main__":
    article = """\n\n            Cancer Currents: An NCI Cancer Research Blog\n    \n\nA blog featuring news and research updates from the National Cancer Institute. Learn more about\u00a0Cancer Currents.\nFDA recently approved the Shield test, the first blood test for the primary screening of people at average risk of colorectal cancer. Where does it fit in with other screening options for the disease, including colonoscopy and stool tests?\nContinue Reading >\nSome women who receive a false-positive result on a mammogram may not come back for routine breast cancer screening in the future, a new study finds. Better doctor\u2013patient communication about the screening process is needed, several researchers said.\nContinue Reading >\nResults from a French clinical trial have identified what experts say should now be the recommended initial treatment of advanced leiomyosarcoma. In the trial, the combination of trabectedin (Yondelis) and doxorubicin improved survival by a median of 9 months.\nContinue Reading >\nOsteonecrosis of the jaw was thought to be a rare side effect of drugs like denosumab (Xgeva) that lessen bone problems when cancer has spread to the bone. But a new study has found that the painful side effect is more common than once thought.\nContinue Reading >\nA new study may provide important new insights into breast cancer metastasis. Blood vessels within tumors release a molecule that draws sensory nerves closer to the tumors, the study shows. This close proximity turns on genes in the cancer cells that drive metastasis.\nContinue Reading >\nTrial participants who stopped imatinib had a more rapid worsening of disease, a shorter time until resistance, and did not live as long as participants who continued the therapy uninterrupted.\nContinue Reading >\nResearchers have identified hundreds of promising targets for existing drugs or potential new cancer drugs. The findings relied heavily on proteogenomic data from more than 1,000 tumors representing 10 types of cancer released last year by NCI's CPTAC program.\nContinue Reading >\nDNA fragments from retroviruses that are millions of years old appear to be active in a variety of cancers, a new study found. One virus-derived DNA fragment in particular, known as LTR10, turns on cancer-related genes in multiple types of cancer.\nContinue Reading >\nNCI Director Dr. Kimryn Rathmell and Division of Cancer Biology Director Dr. Dan Gallahan explain how the R15 grant program supports researchers at smaller institutions and encourages students to pursue careers in cancer research.\nContinue Reading >\nFDA approved afami-cel (Tecelra) to treat metastatic synovial sarcoma, a type of soft tissue sarcoma. The approval is for patients who have already received chemo and whose tumors are positive for MAGE-A4. Afami-cel is the first T-cell receptor therapy approved for cancer.\nContinue Reading >\nScientists have developed a strategy for treating cancer that takes advantage of tumors\u2019 ability to rapidly evolve and turns it against them. It involves intentionally making some tumor cells resistant to a specific treatment from the get-go.\nContinue Reading >\nTwo new studies in mice show that adding chemotherapy to the experimental KRAS inhibitor MRTX1133 greatly reduced tumor growth and spread compared with either treatment alone.\nContinue Reading >\nNCI periodically provides updates on new websites and other online content of interest to the cancer community. See selected content that has been added as of August 2024.\nContinue Reading >\nIn late 2023, FDA announced it was investigating instances of second cancers following treatment with CAR T-cell therapies. In this Q&A, NCI\u2019s Dr. Stephanie Goff explains what\u2019s known about the issue, stressing that second cancers \u201cof any kind are rare.\u201d\nContinue Reading >\nScientists have been searching for ways to make immune checkpoint inhibitors work for more patients. In two trials, researchers explored a possible role for JAK inhibitors, which dampen chronic inflammation.\nContinue Reading >\nPeople with advanced endometrial cancer now have new FDA-approved treatment options: pembrolizumab and durvalumab, paired with chemotherapy, for tumors with a genetic change called mismatch repair deficiency. The agency also expanded the approved uses of dostarlimab for the disease. \nContinue Reading >\nRegular imaging tests to monitor the pancreas may help detect pancreatic cancer at an early stage in people who are at high risk, a new study suggests. This type of surveillance could also help improve how long these patients live. \nContinue Reading >\nThe expanded approval of two HPV tests allows the patient to collect a vaginal sample themselves in a health care setting, rather than a health provider collecting a sample during a pelvic exam. The availability of a self-collection option in health care settings could help widen access to cervical cancer screening.\nContinue Reading >\nWhile treating people\u2019s health-related social needs has always been a part of health care in one form or other, cancer centers and community cancer clinics increasingly are viewing the people they treat through a social lens and addressing social needs\u2014including transportation, food, and housing\u2014as part of patient care.\nContinue Reading >\nLorlatinib (Lorbrena) is superior to crizotinib (Xalkori) as an initial treatment for people with ALK-positive advanced non-small cell lung cancer, according to new clinical trial results. Treatment with lorlatinib also helped prevent new brain metastases.\nContinue Reading >\nFeatured Posts\n\n                           August 22, 2024,\n                              by                              Carmen Phillips\n                                                   \n\n                           July 24, 2024,\n                              by                              Sharon Reynolds\n                                                   \n\n                           July 9, 2024,\n                              by                              Linda Wang\n                                                   \nCategories\n\n          Archive        \n\n              2024\n            \n\n              2023\n            \n\n              2022\n            \n\n              2021\n            \n\n              2020\n            \n\n              2019\n            \n\n              2018\n            \n\nNational Cancer Institute \nat the National Institutes of Health\n\n
    """

    podcast_script = generate_script(article)

    if podcast_script:
        # Save the script to JSON
        save_script_to_json(podcast_script)
    else:
        print("Failed to generate podcast script.")