import streamlit as st
import requests

# Function to validate the search query
def is_valid(query):
    # send get request to /is_valid endpoint
    response = requests.get("http://127.0.0.1:8000/is_valid", params={"topic": query})
    if response.status_code == 200:
        return response.json().get("is_valid", False)
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

# Initialize session state to store search results and summaries
if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None

if 'summary' not in st.session_state:
    st.session_state['summary'] = None

# First Column: Search Interface, Search Results, and Explore Option
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

            # Display each result as an expander with clickable titles
            for idx, result in enumerate(results):
                with st.expander(f"{result['title']}"):
                    # Display the URL as a clickable link
                    st.markdown(f"[Visit this result]({result['url']})")
                    
                    # Display the content in the expanded section
                    st.write(f"**Content**: {result['content']}")

            st.markdown("---")  # Separator

            # Option to select a single search result for further exploration
            st.subheader("Explore a Specific Result")

            # Create a list of titles for selection
            titles = [item.get("title", f"Result {i+1}") for i, item in enumerate(results)]

            # Radio buttons for selection
            selected_title = st.radio("Select a title to explore:", titles)

            # "Explore" button
            if st.button("Explore"):
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

# Second Column: Display the Summary
with col2:
    st.header("Summary")

    # Check if a summary is available
    if st.session_state['summary']:
        summary = st.session_state['summary']

        if isinstance(summary, list) and all(isinstance(item, dict) for item in summary):
            # Display each summary in a styled box
            for idx, item in enumerate(summary):
                title = item.get("title", "No Title")
                script = item.get("script", "No Script Available")
                
                # Styled box with dark mode colors
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
            
            st.markdown("---")  # Separator

            # Selection Mechanism: Radio Buttons
            st.subheader("Select a Summary to Generate Video")

            # Create a list of titles for selection
            titles = [item.get("title", f"Summary {i+1}") for i, item in enumerate(summary)]

            # Radio buttons for selection
            selected_title = st.radio("Choose a summary:", titles)

            # Retrieve the corresponding script
            selected_script = next((item['script'] for item in summary if item['title'] == selected_title), None)

            # "Generate Video" Button
            if st.button("Generate Video"):
                if selected_title and selected_script:
                    # For now, just display the selected title and script
                    st.info(f"**Selected Title:** {selected_title}")
                    st.info(f"**Selected Script:** {selected_script}")
                    
                    # Future functionality can be added here to generate the video
                else:
                    st.warning("Please select a valid summary to generate a video.")
        else:
            st.warning("Unexpected summary format received.")
    else:
        st.info("No summary to display. Please explore a search result.")
