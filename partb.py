import streamlit as st
import json, os, toml
from openai import OpenAI
import requests

# get GitHub API key
github_key = os.getenv('GITHUB_API_KEY')
openrouter_key = os.getenv('OPENROUTER_API_KEY')

# get GitHub API endpoint
github_endpoint = os.getenv('GITHUB_API_ENDPOINT')
openrouter_endpoint = os.getenv('OPENROUTER_API_ENDPOINT')

# get GitHub API model name
github_model = os.getenv('GITHUB_API_MODEL_NAME')
openrouter_model = os.getenv('OPENROUTER_API_MODEL_NAME')


# get the video title
def get_video_title(video_url):
    video_id = video_url.split("v=")[-1]
    video_info_url = f"https://yt.vl.comp.polyu.edu.hk/transcript?password=for_demo&video_id={video_id}"
    response = requests.get(video_info_url)
    if response.status_code == 200:
        video_info = response.json()
        title = video_info.get("video_title")
        print(f"Video Title: {title}")
        return title
    else:
        return "Video Title"

def format_time(seconds):
    # convert the timestamp to hh:mm:ss format
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# https://yt.vl.comp.polyu.edu.hk/transcript?language_code=zh-Hant&password=for_demo&video_id=ZqB2xbE5zF0
def fetch_transcript(video_url):
    video_id = video_url.split("v=")[-1]
    
    # Fetch available language codes
    lang_url = f"https://yt.vl.comp.polyu.edu.hk/lang?password=for_demo&language=en&video_id={video_id}"
    lang_response = requests.get(lang_url)
    
    if lang_response.status_code == 200:
        language = lang_response.json()
        print(f"Available language code in video: {language}")
        
        # Extract available language codes
        available_languages = [lang['language_code'] for lang in language if 'language_code' in lang]
        if available_languages == []:
            print("Set default language to English (en).")
            language_code = "en"
        else:
            language_code = available_languages[0]
            print(f"Using language code: {language_code}")

    # Fetch the transcript
    transcript_url = f"https://yt.vl.comp.polyu.edu.hk/transcript?language_code={language_code}&password=for_demo&video_id={video_id}"
    response = requests.get(transcript_url)
    
    if response.status_code == 200:
        transcript_data = response.json().get("transcript", [])
        
        transcript = []
        for entry in transcript_data:
            if "start" in entry and "duration" in entry:
                start_time = float(entry["start"])
                text = entry["text"]
                start_time = format_time(start_time)
                transcript.append(f"({start_time}) {text}")
                print(f"({start_time}) {text}") # debug
        
        return transcript
    
    st.error(f"Failed to fetch transcript.")
    return None

    
def answers(system_prompt, user_prompt):
    # create an instance of OpenAI
    client = OpenAI(
        base_url=github_endpoint,
        api_key=github_key,
    )
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=github_model
    )
    with st.expander("Show LLM Output", expanded=False):
        st.write(response)
    
    return response.choices[0].message.content

def generate_summary(language, video_url):
    transcript = fetch_transcript(video_url)
    system_prompt = f"You are helpful assistant."
    user_prompt = f"Summarize the transcript by generate summary depend on selected language {language}. Transcript: {transcript}"
    
    with st.expander("Show Prompt", expanded=False):
        st.write(user_prompt)  # Display the raw response for debugging
    
    results = answers(system_prompt, user_prompt)
    return results

def generate_summary_handler():
    language = st.session_state["language"]
    video_url = st.session_state["video_url"]  # Assuming video_url is stored in session state

    # Generate summary
    app = generate_summary(language, video_url)
    title_text = get_video_title(video_url)

    # Display the extracted information
    st.subheader(f"{title_text}")
    st.write(f"Video URL: {video_url}")
    st.write(f"{app}")
    
def generate_detailed_summary_handler():
    language = st.session_state["language"]
    video_url = st.session_state["video_url"]  # Assuming video_url is stored in session state

    # Generate summary
    app = generate_summary(language, video_url)
    title_text = get_video_title(video_url)

    # Display the extracted information
    st.subheader(f"{title_text}")
    st.write(f"Video URL: {video_url}")
    st.write(f"{app}")
    
# Streamlit App Layout
st.set_page_config(page_title="YouTube Summarizer App", layout="wide")
video_url = st.sidebar.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=SLwpqD8n3d0")
language = st.sidebar.selectbox("Language", options=["en", "zh-TW", "zh-CN"])

# session state for generating summary
st.session_state["summary"] = ""  # Default value
st.session_state["language"] = language  # Default value
st.session_state["video_url"] = video_url  # Default value

button1 = st.sidebar.button("Generate Summary", on_click=generate_summary_handler)
button2 = st.sidebar.button("Generate Detailed Summary", on_click=generate_detailed_summary_handler)