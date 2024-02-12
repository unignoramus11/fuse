import ffmpeg
import json


def create_video(username, project_id):
    # Define paths
    base_path = (
        "uploads/" + username + "/" + project_id + "/"
    )
    json_file = (
        base_path + "project_data.json"
    ) 
    output_file = base_path + project_id + ".mp4"

    # Load JSON data
    with open(json_file, "r") as f:
        data = json.load(f)

    # Extract video parameters
    video_name = data["name"]
    video_format = data["format"]
    fps = data["fps"]
    height = data["height"]
    width = data["width"]

    # Extract image and audio information
    images = data["images"]
    audio = data.get("audio", [])

    # Define a list to store input streams
    streams = []

    # Create input streams for each image with respective durations and transitions
    for idx, image_info in enumerate(images):
        file = base_path + image_info["file"].lstrip(
            "/"
        )  # Remove the slash from the image file name
        duration_ms = (
            image_info["duration_ms"] / 1000
        )  # Convert milliseconds to seconds
        transition = image_info["transition"]

        # Apply loop filter with specified duration and number of frames
        loop_frames = int(fps * duration_ms)  # Calculate the number of frames to loop
        stream = (
            ffmpeg.input(file)
            .filter("loop", loop=1, size=loop_frames)
            .filter("trim", duration=duration_ms)
        )

        if idx > 0 and transition == "fade":
            stream = stream.filter(
                "fade", type="in", duration=1
            )  # Apply fade transition for all images except the first one

        streams.append(stream)

    # Concatenate the input streams
    video = ffmpeg.concat(*streams, v=1, a=0)

    # Add audio if available
    if audio:
        audio_file = base_path + audio[0]["file"]
        audio_duration_ms = (
            audio[0]["duration_ms"] / 1000
        )  # Convert milliseconds to seconds
        audio_stream = ffmpeg.input(audio_file).filter(
            "atrim", duration=audio_duration_ms
        )
        video = ffmpeg.output(video, audio_stream, output_file, shortest=None)
    else:
        video = ffmpeg.output(video, output_file)

    # Run ffmpeg command
    ffmpeg.run(video)


username = "admin"
project_id = "1"
create_video(username, project_id)