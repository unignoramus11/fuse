from moviepy.editor import *
import csv
import random

user = "admin"
projectID = 1


def createVideo(user, projectID, codec="libx264"):
    """Convert the given images and audio in the uploads/{user} folder to a video"""

    # Get the list of images in the uploads/{user}/{projectID}/ folder
    images = os.listdir(f"uploads/{user}/{projectID}/images")

    # Create a list to store the images
    imageList = []

    # Loop through the images and add them to the list
    for image in images:
        # Random duration
        duration = random.randint(1, 5)
        imageList.append(
            ImageClip(f"uploads/{user}/{projectID}/images/{image}").set_duration(
                duration
            )
        )

    # Create a video from the images
    video = concatenate_videoclips(imageList, method="compose")

    # Get the list of audios from CSV
    # audioList = [
    #     f"uploads/{user}/{projectID}/audio/{audio}"
    #     for audio in os.listdir(f"uploads/{user}/{projectID}/audio")
    # ]

    # Add the audio to the video
    # if audioList:
    #     audio = AudioFileClip(audioList[0])
    #     video = video.set_audio(audio)

    # Save the video to the uploads/{user} folder
    video.write_videofile(f"uploads/{user}/{projectID}.mp4", fps=30, codec=codec)

    # Return the path to the video
    return f"uploads/{user}/{projectID}.mp4"


createVideo(user, projectID)

