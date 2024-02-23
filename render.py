import argparse
import ffmpeg
import json
from database import removeTask
import os

# TODO: if video already exists, overwrite it


def create_video(username, project_id):
    print("Creating video for project", project_id)
    # Define paths
    base_path = "uploads/" + username + "/" + project_id + "/"
    json_file = base_path + "project_data.json"
    # Load JSON data
    with open(json_file, "r") as f:
        data = json.load(f)

    output_file = base_path + data["name"] + "." + data["format"]

    if os.path.exists(output_file):
        os.remove(output_file)

    # Extract video parameters
    FPS = 30
    height = data["height"]
    width = data["width"]

    # Extract image and audio information
    images = data["images"]
    audio = data.get("audio", [])

    # Define a list to store input streams
    streams = []

    # Create input streams for each image with respective durations
    for idx, image_info in enumerate(images):
        file = base_path + "images/" + image_info["file"]
        duration_s = image_info["duration_ms"] / 1000

        # Apply loop filter with specified duration and number of frames
        # Calculate the number of frames to loop
        loop_frames = int(FPS * duration_s)
        stream = (
            ffmpeg.input(file)
            .filter(
                "scale", width, height
            )  # Ensure all images have the same dimensions
            # Set the sample aspect ratio to the simplest ratio
            .filter("setsar", sar="1:1")
            # Set pixel format to a non-deprecated one
            .filter("loop", loop=loop_frames, size=1)
        )

        # Add transitions
        transition = image_info["transition"]
        if transition == "fade":
            stream = stream.filter("fade", type='in', duration=0.5)
        if transition == "blur":
            stream = stream.filter(
                "boxblur", luma_power=1, enable='between(t,0,0.5)')
        if transition == "rotate":
            stream = stream.filter(
                "rotate", angle='360*mod(t,128)', fillcolor="black", enable='between(t,0,0.5)')

        streams.append(stream)

    # Concatenate the input streams
    video = ffmpeg.concat(
        *streams, v=1, a=0, n=len(streams)
    )

    # Add audio if available
    if audio:
        audio_streams = []
        for audio_info in audio:
            audio_file = base_path + "audio/" + audio_info["file"]
            audio_duration_s = audio_info["duration_ms"] / 1000
            audio_stream = ffmpeg.input(audio_file).filter(
                "atrim", duration=audio_duration_s
            )
            audio_streams.append(audio_stream)
        audio_stream = ffmpeg.concat(
            *audio_streams, v=0, a=1, n=len(audio_streams))

        video = ffmpeg.output(
            video,
            audio_stream,
            output_file,
            shortest=None,
            f=data["format"],
            r=FPS
        )
    else:
        video = ffmpeg.output(video, output_file, f=data["format"], r=FPS)

    ffmpeg.run(video)

    # -1 is a special project_id to indicate that the video is a preview
    if project_id != -1:
        removeTask(project_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a video.')
    parser.add_argument('username', type=str, help='The username.')
    parser.add_argument('project_id', type=str, help='The project ID.')
    args = parser.parse_args()

    create_video(args.username, args.project_id)
