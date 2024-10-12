import streamlit as st
import requests

# Streamlit UI
# Set the page configuration to wide layout
st.set_page_config(
    page_title="MediReels Search",
    layout="wide",  # Makes the app use the entire browser width
    initial_sidebar_state="expanded"  # Optional: Expands the sidebar by default
)

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
                st.error(f"HTTP error occurred: {http_err}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
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
                    st.error(f"HTTP error occurred: {http_err}")
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
            for item in summary:
                title = item.get("title", "No Title")
                script = item.get("script", "No Script Available")

                st.markdown(f"### {title}")
                st.markdown(f"{script}\n")
        else:
            st.warning("Unexpected summary format received.")
    else:
        st.info("No summary to display. Please explore a search result.")
