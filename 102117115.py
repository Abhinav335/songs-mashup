import re
import os
from googleapiclient.discovery import build
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pytube import YouTube
from moviepy.editor import VideoFileClip, concatenate_audioclips

def get_youtube_service(api_key):
    return build('youtube', 'v3', developerKey=api_key)

def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def download_videos(api_key, singer_name, num_videos):
    print(f"Downloading {num_videos} videos of {singer_name} from YouTube using API...")

    youtube_service = get_youtube_service(api_key)
    query = f"{singer_name} songs"

    # Search for videos using the YouTube Data API
    search_response = youtube_service.search().list(
        q=query,
        type='video',
        part='id',
        maxResults=num_videos
    ).execute()

    video_ids = [item['id']['videoId'] for item in search_response['items']]

    for i, video_id in enumerate(video_ids):
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"Downloading Video {i + 1} - ID: {video_id}")
            YouTube(video_url).streams.get_highest_resolution().download()
        except Exception as e:
            print(f"Error downloading Video {i + 1}: {e}")

def convert_to_audio():
    print("Converting videos to audio...")
    for file in os.listdir():
        if file.endswith(".mp4"):
            video = VideoFileClip(file)
            audio = video.audio
            audio.write_audiofile(file.replace(".mp4", ".mp3"))
            video.close()
            audio.close()

def cut_audio(duration):
    print(f"Cutting first {duration} seconds from all downloaded audios...")
    for file in os.listdir():
        if file.endswith(".mp3"):
            audio = AudioFileClip(file)
            audio = audio.subclip(0, duration)
            audio.write_audiofile(file)
            audio.close()

def merge_audios(output_filename):
    print("Merging all audios into a single output file...")
    audio_clips = [AudioFileClip(file) for file in os.listdir() if file.endswith(".mp3")]
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(output_filename)

def mashup(api_key, singer_name, num_videos, audio_duration, output_filename):
    try:
        download_videos(api_key, singer_name, num_videos)
        convert_to_audio()
        cut_audio(audio_duration)
        merge_audios(output_filename)
        print(f"Mashup completed! Output file: {output_filename}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":

    api_key = 'AIzaSyAJq5t7IavGMSQQTuUdOtaYjMh4lO4Lzp0'
    singer_name = "EdSheeran"
    num_videos = 2
    audio_duration = 30
    output_filename = "mashup_output.mp3"

    mashup(api_key, singer_name, num_videos, audio_duration, output_filename)
