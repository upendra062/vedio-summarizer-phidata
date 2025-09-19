
import streamlit as st 
from phi.agent import Agent 
from phi.model.google import Gemini 
from phi.tools.duckduckgo import DuckDuckGo 
from google.generativeai import upload_file, get_file 
import google.generativeai as genai 
import time 
import os 
from pathlib import Path 
import tempfile 
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GOOGLE_API_KEY')

if API_KEY is None: 
    genai.configure(api_key=API_KEY)

st.set_page_config(
    page_title="Video Summarizer Agent", 
    page_icon="🧊", 
    layout="wide", 


)
st.title("Video Summarizer Agent🧊")
st.header("This app is powered by Gemini")


# Create an agent 
def initialzie_agent(): 
    return Agent(
        name="Video Summarizer Agent", 
        model=Gemini(
            id="gemini-2.0-flask-exp"
        ),
        tools=[DuckDuckGo()], 
        markdown=True 
    )

multimodal_Agent = initialzie_agent()

video_file = st.file_uploader(
    "Upload a video file here", type=['mp4', 'mov', 'avi'], help="Upload a video for AI Analysis."
)

if video_file: 
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(video_file.read())
        video_path = temp_video.name 
        
    st.video(video_path, format="video/mp4", start_time=0)

    user_query = st.text_area(
        "What insights do you seeking from the video?", 
        placeholder="Ask anything abou the video content. The AI agent will analyze and gather additional context if needed.",  
        help="Provide specific questions or insights you want to from the video."
    )

    if st.button("🧊 Analyze Video", key="analyze_video_button"): 
        if not user_query: 
            st.warning("Please provide a question or insight to analyze the video.")
        else: 
            try: 
                with st.spinner("Processing video and gathering insights..."): 
                    processed_video = upload_file(video_path)
                    while processed_video.state.name == "PROCESSING": 
                        time.sleep(1)
                        processed_video = get_file(processed_video.name)

                    # Prompt generation for analysis 
                    analysis_prompt = (
                        f"""
                        Analyze the uploaded video for content and context.
                        Respond to the following query using video insights and supplementary web research:
                        {user_query}
                        
                        Provide a detailed, user-friendly, and actionable response.
                        """
                    )

                    # AI agent processing 
                    response = multimodal_Agent.run(analysis_prompt, videos=[processed_video])
                # Display the result 
                st.subheader("Analysis Results:")
                st.markdown(response.content)

            except Exception as e: 
                st.error(f"An error occured during analysis:")
            finally: 
                Path(video_path).unlink(missing_ok=True)

    else: 
        st.info("Upload a video file to begin analysis.")

# Customize text area height 
st.markdown( 
    """
    <style> 
    .stTextArea {
        height: 100px;
    }
    </style> 
    """, 
    unsafe_allow_html=True 
)