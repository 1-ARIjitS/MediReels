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
    initial_sidebar_state="expanded"
)

# Streamlit UI
st.title("MediReels Search")

# Divide the page into two columns
col1, col2 = st.columns([2, 3])  # Adjust the width ratios as needed

# Initialize session state to store search results, summaries, and video generation message
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None

if 'summary' not in st.session_state:
    st.session_state['summary'] = None

if 'video_generation_message' not in st.session_state:
    st.session_state['video_generation_message'] = ""

# First Column: Search Interface and Search Results
with col1:
    st.header("Search Interface")
    
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
                    st.session_state['video_generation_message'] = ""  # Reset video generation message

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

    st.markdown("---")  # Separator

    # Display Search Results
    st.header("Search Results")

    # Check if search results are available
    if st.session_state['search_results']:
        search_results = st.session_state['search_results']
        results = search_results.get("results", [])

        if results:
            st.subheader(f"Results for: {search_results.get('query', topic)}")

            # Display each result as an expander with clickable titles and an "Explore" button
            for idx, result in enumerate(results):
                with st.expander(f"{result['title']}"):
                    # Display the URL as a clickable link
                    st.markdown(f"[Visit this result]({result['url']})")
                    
                    # Display the content in the expanded section
                    st.write(f"**Content**: {result['content']}")

                    # "Explore" button for this specific result
                    if st.button("Explore", key=f"explore_{idx}"):
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
                            st.session_state['video_generation_message'] = ""  # Reset video generation message

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

# Second Column: Display the Summary and Generate Video
with col2:
    st.header("Summary")

    # Check if a summary is available
    if st.session_state['summary']:
        summary = st.session_state['summary']

        if isinstance(summary, list) and all(isinstance(item, dict) for item in summary):
            # Display each summary with a "Generate Video" button
            for idx, item in enumerate(summary):
                title = item.get("title", "No Title")
                script = item.get("script", "No Script Available")
                
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
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with button_col:
                        # "Generate Video" button for this specific summary
                        if st.button("Generate Video", key=f"generate_{idx}"):
                            selected_title = title
                            selected_script = script

                            # Placeholder for video generation functionality
                            # For now, we'll just set the video generation message
                            st.session_state['video_generation_message'] = f"Video generation started for: {selected_title}"

            st.markdown("---")  # Separator

            # Display Video Generation Message
            if st.session_state['video_generation_message']:
                st.markdown(f"**{st.session_state['video_generation_message']}**")
        else:
            st.warning("Unexpected summary format received.")
    else:
        st.info("No summary to display. Please explore a search result.")
