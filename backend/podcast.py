import os
import gender_guesser.detector as gender
from dotenv import load_dotenv
import json
from pydub import AudioSegment
import edge_tts
import asyncio

# Load environment variables from the .env file
load_dotenv()

# Load JSON data from a file
def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Retrieve objects from the loaded JSON data
def retrieve_podcast_info(data):
    podcast_title = data["podcast_title"]
    host_name = data["host_name"]
    guest_name = data["guest_name"]
    conversation = data["conversation"]
    return podcast_title, host_name, guest_name, conversation

# Determine the gender from the name using gender-guesser
def get_gender_from_name(name):
    d = gender.Detector()
    gender_of_person = d.get_gender(name.split()[0])  # Use the first name to guess gender
    return gender_of_person

# Map gender to appropriate voice
def get_voice_for_gender(gender):
    if gender in ['male', 'mostly_male']:
        return "en-US-GuyNeural"  # Male voice
    elif gender in ['female', 'mostly_female']:
        return "en-US-JennyNeural"  # Female voice
    else:
        return "en-US-AriaNeural"  # Neutral/fallback voice

# Function to generate audio using edge-tts
async def generate_audio(text, filename, voice):
    communicate = edge_tts.Communicate(text, voice)
    if not os.path.exists("podcast_audio"):
        os.makedirs("podcast_audio")
    await communicate.save(f"podcast_audio/{filename}")

# Function to append audio files
def append_audio(audio_files, output_filename):
    combined_audio = AudioSegment.empty()
    for file in audio_files:
        if file.split("/")[0]=="podcast_audio":
            audio = AudioSegment.from_mp3(file)
        else:
            audio = AudioSegment.from_mp3(os.path.join("podcast_audio", file))
        combined_audio += audio
    combined_audio.export(output_filename, format="mp3")

# Main function to generate the podcast
async def generate_podcast(podcast_data):

    # Get host and guest names
    host_name = podcast_data['host_name']
    guest_name = podcast_data['guest_name']

    # Determine the gender of the host and guest
    host_gender = get_gender_from_name(host_name)
    guest_gender = get_gender_from_name(guest_name)

    # Select voices based on gender
    host_voice = get_voice_for_gender(host_gender)
    guest_voice = get_voice_for_gender(guest_gender)

    # List to hold the audio files that will be concatenated
    audio_files = []

    retrieve_podcast_info(podcast_data)

    # Add intro music
    audio_files.append("podcast_audio/music/intro_music/intro_music_1.mp3")

    # Host and guest conversation
    conversation = podcast_data.get("conversation", [])

    # Iterate over the conversation array
    for i, dialogue in enumerate(conversation):
        if 'host' in dialogue:
            host_filename = f"host_{i}.mp3"
            await generate_audio(dialogue['host'], host_filename, host_voice)
            audio_files.append(host_filename)
        if 'guest' in dialogue:
            guest_filename = f"guest_{i}.mp3"
            await generate_audio(dialogue['guest'], guest_filename, guest_voice)
            audio_files.append(guest_filename)

    # Add outro music
    audio_files.append("podcast_audio/music/outro_music/outro_music_1.mp3")

    # Combine all audio files into one final podcast file
    final_podcast_file = "results/podcast_final.mp3"
    append_audio(audio_files, final_podcast_file)
    print(f"Podcast saved as {final_podcast_file}")

if __name__ == "__main__":
    filename = "podcast_res/podcast_script.json"  # Path to your JSON file
    podcast_data = load_json(filename)  # Load JSON data
    podcast_info = retrieve_podcast_info(podcast_data)  # Retrieve specific data

    # Print the retrieved information
    podcast_title, host_name, guest_name, conversation = podcast_info
    print(f"Podcast Title: {podcast_title}")
    print(f"Host Name: {host_name}")
    print(f"Guest Name: {guest_name}")
    print("Conversation:")
    for exchange in conversation:
        for speaker, text in exchange.items():
            print(f"{speaker.capitalize()}: {text}")

    # Run the podcast generation asynchronously
    asyncio.run(generate_podcast(podcast_data))