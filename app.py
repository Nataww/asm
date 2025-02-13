import streamlit as st
import os
import requests
import openai
from io import BytesIO

# Function to get API keys from environment variables
def get_api_keys():
    if st.secrets:  # For deployed app
        return st.secrets["GITHUB_API_KEY"], st.secrets["GITHUB_API_ENDPOINT"], st.secrets["GITHUB_API_MODEL_NAME"]
    else:  # For local development
        return os.getenv("GITHUB_API_KEY"), os.getenv("GITHUB_API_ENDPOINT"), os.getenv("GITHUB_API_MODEL_NAME")

# Function to get YouTube transcript (placeholder)
def get_youtube_transcript(video_url):
    # Implement the logic to fetch transcript here
    return "00:00:00 This is the first section.\n00:01:30 This is the second section."

# Function to generate summary using GPT-4o-mini
def generate_summary(transcript, model_name, api_key, language):
    openai.api_key = api_key
    prompt = f"Please summarize the following transcript in {language}, dividing it into sections with timestamps:\n{transcript}"
    
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

def generate_detailed_summary(transcript, model_name, api_key, language, section):
    openai.api_key = api_key
    prompt = f"Please provide a more detailed summary of the following section of the transcript in {language}:\n{section}"
    
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

def generate_concise_summary(transcript, model_name, api_key, language, section):
    openai.api_key = api_key
    prompt = f"Please provide a more concise summary of the following section of the transcript in {language}:\n{section}"
    
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

def generate_fun_summary(transcript, model_name, api_key, language, section):
    openai.api_key = api_key
    prompt = f"Make the following summary more fun and add emojis in {language}:\n{section}"
    
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

def format_sections(summary, video_url):
    sections = summary.split('\n')
    formatted_sections = []
    
    for section in sections:
        if section.strip():
            timestamp, text = section.split(' ', 1)
            video_time = timestamp.strip()
            link = f"{video_url}&t={convert_to_seconds(video_time)}"
            formatted_sections.append({
                "timestamp": video_time,
                "text": text.strip(),
                "link": link,
                "transcript": get_youtube_transcript(video_url)  # Placeholder for actual transcript fetching
            })
    
    return formatted_sections

def download_summary_as_html(sections):
    """Generate HTML for the sections and download."""
    html_content = "<html><body><h1>YouTube Summary</h1>"
    
    for section in sections:
        html_content += f"<h2>{section['timestamp']} - {section['text']}</h2>"
        html_content += f"<p><a href='{section['link']}'>Watch on YouTube</a></p>"
    
    html_content += "</body></html>"
    return html_content

def convert_to_seconds(timestamp):
    """Convert hh:mm:ss format to seconds."""
    h, m, s = map(int, timestamp.split(':'))
    return h * 3600 + m * 60 + s

def main():
    st.title("YouTube Summarizer")

    # Input for YouTube URL
    video_url = st.text_input("Enter YouTube Video URL:")
    
    # Language selection
    language = st.selectbox(
        "Select Language for Summary:",
        options=["English (en)", "Traditional Chinese (zh-TW)", "Simplified Chinese (zh-CN)"]
    )
    
    if st.button("Generate Summary"):
        github_api_key, github_endpoint, api_model_name = get_api_keys()
        
        # Fetch transcript
        transcript = get_youtube_transcript(video_url)
        
        # Generate summary
        summary = generate_summary(transcript, api_model_name, github_api_key, language)

        # Format sections with timestamps and hyperlinks
        formatted_sections = format_sections(summary, video_url)

        # Display sections
        for section in formatted_sections:
            st.subheader(section['timestamp'])
            edited_text = st.text_area("Edit Summary:", value=section['text'], key=section['timestamp'])
            st.write(f"[Watch on YouTube]({section['link']})")

            # Show transcript
            with st.expander("Show Transcript"):
                st.write(section['transcript'])

            # Button to generate more detailed summary
            if st.button("More Detail", key=f"detail_{section['timestamp']}"):
                detailed_summary = generate_detailed_summary(section['transcript'], api_model_name, github_api_key, language, section['transcript'])
                st.write("Detailed Summary:")
                st.write(detailed_summary)

            # Button to generate more concise summary
            if st.button("More Concise", key=f"concise_{section['timestamp']}"):
                concise_summary = generate_concise_summary(section['transcript'], api_model_name, github_api_key, language, section['transcript'])
                st.write("Concise Summary:")
                st.write(concise_summary)

            # Button to generate more fun summary
            if st.button("More Fun", key=f"fun_{section['timestamp']}"):
                fun_summary = generate_fun_summary(section['transcript'], api_model_name, github_api_key, language, section['transcript'])
                st.write("Fun Summary:")
                st.write(fun_summary)

            # Download functionality
            html_summary = download_summary_as_html(formatted_sections)
            st.download_button("Download Summary as HTML", data=html_summary, file_name="summary.html", mime="text/html")

if __name__ == "__main__":
    main()