from email.message import Message

import streamlit as st
from pytube import YouTube
from moviepy.editor import VideoFileClip, concatenate_audioclips
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
import os
import re


def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None


def download_videos(singer_name, num_videos):
    st.write(f"Downloading {num_videos} videos of {singer_name} from YouTube...")

    query = f"{singer_name} songs"
    search_results = YouTube(f"https://www.youtube.com/results?search_query={query}")
    videos = search_results.streams.filter(type="video").first(num_videos)

    for i, video in enumerate(videos):
        try:
            video_url = video.url
            video_id = get_video_id(video_url)

            if video_id:
                st.write(f"Downloading Video {i + 1} - ID: {video_id}")
                YouTube(f"https://www.youtube.com/watch?v={video_id}").streams.get_highest_resolution().download()
            else:
                st.write(f"Error extracting Video {i + 1} ID from URL: {video_url}")
        except Exception as e:
            st.write(f"Error downloading Video {i + 1}: {e}")


def convert_to_audio():
    st.write("Converting videos to audio...")
    for file in os.listdir():
        if file.endswith(".mp4"):
            video = VideoFileClip(file)
            audio = video.audio
            audio.write_audiofile(file.replace(".mp4", ".mp3"))
            video.close()
            audio.close()


def cut_audio(duration):
    st.write(f"Cutting first {duration} seconds from all downloaded audios...")
    for file in os.listdir():
        if file.endswith(".mp3"):
            audio = AudioFileClip(file)
            audio = audio.subclip(0, duration)
            audio.write_audiofile(file)
            audio.close()


def merge_audios(output_filename):
    st.write("Merging all audios into a single output file...")
    audio_clips = [AudioFileClip(file) for file in os.listdir() if file.endswith(".mp3")]
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(output_filename)


def send_email(email, attachment_path):
    msg = Message('Mashup Result', sender='your_email@gmail.com', recipients=[email])
    msg.body = 'Please find attached the mashup result.'
    with app.open_resource(attachment_path) as attachment:
        msg.attach('result.zip', 'application/zip', attachment.read())

    mail.send(msg)


def mashup(singer_name, num_videos, audio_duration, email):
    try:
        download_videos(singer_name, num_videos)
        convert_to_audio()
        cut_audio(audio_duration)

        # Save the output to a temporary directory
        output_filename = "output.mp3"
        merge_audios(output_filename)

        # Create a zip file with the output file
        with NamedTemporaryFile(delete=False) as temp_file:
            with ZipFile(temp_file, 'w') as zip_file:
                zip_file.write(output_filename)

        # Send email with the zip file attachment
        send_email(email, temp_file.name)

        st.success('Mashup completed! Check your email for the result.')

    except Exception as e:
        st.error(f'Error: {e}')


# Streamlit UI
st.title('Mashup Web App')

singer_name = st.text_input('Enter Singer Name:')
num_videos = st.slider('Number of Videos:', min_value=10, max_value=20, value=10)
audio_duration = st.slider('Audio Duration (seconds):', min_value=20, max_value=60, value=20)
email = st.text_input('Enter Your Email:')

if st.button('Create Mashup'):
    mashup(singer_name, num_videos, audio_duration, email)
