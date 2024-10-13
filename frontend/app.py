import streamlit as st
import requests

# Function to validate the search query
def is_valid(query):
    # Send GET request to /is_valid endpoint
    try:
        response = requests.get("http://127.0.0.1:8000/is_valid", params={"topic": query})
        if response.status_code == 200:
            return response.json().get("is_valid", False)
        return False
    except Exception as e:
        st.error(f"Error validating query: {e}")
        return False

# Set the page configuration to wide layout
st.set_page_config(
    page_title="MediReels Search",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💬"
)

# Center the logo and title
st.image("frontend/logo.jpg", width=100)
st.title("MediReels")

# Initialize session state to store search results, summaries, and generated video path
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None

if 'summary' not in st.session_state:
    st.session_state['summary'] = None

if 'generated_video_path' not in st.session_state:
    st.session_state['generated_video_path'] = None

# --- Search Interface ---
st.header("Search")

# Input field for topic
topic = st.text_input("Enter a topic for search:", "")

# When the user clicks the "Search" button
if st.button("Search"):
    if topic:
        # Check if the query is valid
        if is_valid(topic):
            # Backend FastAPI URL
            backend_url = "http://127.0.0.1:8000/search"

            # Prepare the request payload (only the topic is sent from the frontend)
            payload = {
                "topic": topic
            }

            # Send the request to the FastAPI backend
            try:
                with st.spinner('Searching...'):
                    response = requests.post(backend_url, json=payload)
                    response.raise_for_status()  # Raise an error for bad status codes

                # Parse and store the results in session state
                st.session_state['search_results'] = response.json()
                st.session_state['summary'] = None  # Reset summary when a new search is performed
                st.session_state['generated_video_path'] = None  # Reset generated video path

                st.success(f"Search completed for topic: {topic}")

            except requests.exceptions.HTTPError as http_err:
                # Attempt to extract more detailed error message
                try:
                    error_detail = response.json().get('detail', str(http_err))
                except:
                    error_detail = str(http_err)
                st.error(f"HTTP error occurred: {error_detail}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            # Display error message for invalid query
            st.error("Query is not relevant to healthcare.")
    else:
        st.warning("Please enter a topic to search.")


# --- Trending Topics ---
st.markdown("---")  # Separator

# --- Search Results ---
# st.header("Search Results")
st.subheader("Trending Topics")

# Check if search results are available
if st.session_state['search_results']:
    search_results = st.session_state['search_results']
    results = search_results.get("results", [])

    if results:
        # Display each result as an expander with clickable titles and an "Explore" button
        for idx, result in enumerate(results):
            with st.expander(f"{result['title']}"):
                # Display the URL as a clickable link
                st.markdown(f"[Visit this result]({result['url']})")
                
                # Display the content in the expanded section
                st.write(f"**Content**: {result['content']}")

                if st.button("Explore long-form content", key=f"explore_{idx}"):
                    selected_title = result['title']
                    # Backend Summarize API URL
                    backend_summarize_url = "http://127.0.0.1:8000/summarize"

                    # Prepare the payload with the selected title
                    payload = {"title": selected_title}

                    try:
                        with st.spinner('Exploring...'):
                            summarize_response = requests.post(backend_summarize_url, json=payload)
                            summarize_response.raise_for_status()
                            summary = summarize_response.json()
                        
                        # Store the summary in session state
                        st.session_state['summary'] = summary
                        st.session_state['generated_video_path'] = None  # Reset generated video path

                        st.success(f"Exploration completed for: {selected_title}")

                    except requests.exceptions.HTTPError as http_err:
                        # Attempt to extract more detailed error message
                        try:
                            error_detail = summarize_response.json().get('detail', str(http_err))
                        except:
                            error_detail = str(http_err)
                        st.error(f"HTTP error occurred: {error_detail}")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

                # "Explore" button for this specific result
                if st.button("Explore short-form content", key=f"explore_{idx}"):
                    selected_title = result['title']
                    # Backend Summarize API URL
                    backend_summarize_url = "http://127.0.0.1:8000/summarize"

                    # Prepare the payload with the selected title
                    payload = {"title": selected_title}

                    try:
                        with st.spinner('Exploring...'):
                            summarize_response = requests.post(backend_summarize_url, json=payload)
                            summarize_response.raise_for_status()
                            summary = summarize_response.json()
                        
                        # Store the summary in session state
                        st.session_state['summary'] = summary
                        st.session_state['generated_video_path'] = None  # Reset generated video path

                        st.success(f"Exploration completed for: {selected_title}")

                    except requests.exceptions.HTTPError as http_err:
                        # Attempt to extract more detailed error message
                        try:
                            error_detail = summarize_response.json().get('detail', str(http_err))
                        except:
                            error_detail = str(http_err)
                        st.error(f"HTTP error occurred: {error_detail}")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
    else:
        st.info("No results found for the given topic.")
else:
    st.info("No search results to display. Please perform a search.")

st.markdown("---")  # Separator

# --- Summary Section ---
st.header("Summary")

# Check if a summary is available
if st.session_state['summary']:
    summary = st.session_state['summary']

    if isinstance(summary, list) and all(isinstance(item, dict) for item in summary):
        # Display each summary with a "Generate Video" button
        for idx, item in enumerate(summary):
            title = item.get("title", "No Title")
            script = item.get("script", "No Script Available")
            caption = item.get("caption", "No Caption Available")
            
            with st.container():
                # Create two columns: one for the summary and one for the button
                summary_col, button_col = st.columns([4, 1])
                
                with summary_col:
                    # Styled summary box
                    st.markdown(f"""
                    <div style="
                        border:1px solid #444444;
                        border-radius:5px;
                        padding:15px;
                        margin-bottom:15px;
                        background-color:#2c2c2c;
                        color:#ffffff;
                    ">
                        <h4 style="color:#1e90ff;">{title}</h4>
                        <p>{script}</p>
                        <p><strong>Caption: </strong><em>{caption}</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with button_col:
                    # "Generate Video" button for this specific summary
                    if st.button("Generate Video", key=f"generate_{idx}"):
                        selected_title = title
                        selected_script = script

                        try:
                            # Step 1: Send POST request to /transcribe
                            with st.spinner('Generating subtitles for video'):
                                transcribe_url = "http://127.0.0.1:8000/transcribe"
                                transcribe_payload = {"title": selected_title}
                                transcribe_response = requests.post(transcribe_url, json=transcribe_payload)
                                transcribe_response.raise_for_status()

                            # Step 2: Send GET request to /generate_images
                            with st.spinner('Generating images'):
                                generate_images_url = "http://127.0.0.1:8000/generate_images"
                                generate_images_response = requests.get(generate_images_url)
                                generate_images_response.raise_for_status()

                            # Step 3: Send GET request to /generate_video
                            with st.spinner('Generating reel'):
                                generate_video_url = "http://127.0.0.1:8000/generate_video"
                                generate_video_response = requests.get(generate_video_url)
                                generate_video_response.raise_for_status()

                            # Assuming the video is saved at './results/output_video.mp4'
                            st.session_state['generated_video_path'] = "results/output_video.mp4"

                            # Immediately display the generated video
                            st.success(f"Video generation completed for: {selected_title}")
                            
                        except requests.exceptions.HTTPError as http_err:
                            # Attempt to extract more detailed error message
                            try:
                                error_detail = generate_video_response.json().get('detail', str(http_err))
                            except:
                                error_detail = str(http_err)
                            st.error(f"HTTP error occurred: {error_detail}")
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
    else:
        st.info("No summary data available.")
else:
    st.info("No summary to display. Please explore a search result.")

st.markdown("---")  # Separator

# --- Generated Video Section ---
st.header("Generated Video")

# Display Generated Video if available
if st.session_state['generated_video_path']:
    try:
        st.video(st.session_state['generated_video_path'], format="video/mp4")
    except FileNotFoundError:
        st.error("Generated video file not found.")
    except Exception as e:
        st.error(f"An error occurred while loading the video: {e}")
else:
    st.info("No video generated yet. Please generate a video from the summary section.")
