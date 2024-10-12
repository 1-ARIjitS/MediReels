import streamlit as st
import requests

# Streamlit UI
st.title("MediReels Search")

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
        response = requests.post(backend_url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse and display the results
            search_results = response.json()

            st.subheader(f"Search Results for: {topic}")

            # Display each result as a flashcard with clickable titles
            for idx, result in enumerate(search_results.get("results", [])):
                # Create an expander for each search result, acting as a flashcard
                with st.expander(f"{result['title']}"):
                    # Display the URL as a clickable link
                    st.markdown(f"[Visit this result]({result['url']})")
                    
                    # Display the content in the expanded section
                    st.write(f"**Content**: {result['content']}")

        else:
            st.error(f"Error: {response.status_code}, {response.text}")
    else:
        st.warning("Please enter a topic to search.")
