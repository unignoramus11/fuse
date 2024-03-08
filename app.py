from flask import (
    redirect,
    url_for,
    render_template,
    request,
    send_from_directory,
)
from dotenv import dotenv_values
import os
import jwt
import hashlib
import database
import json
from render import create_video
from threading import Thread
from flask_commons import app

env = dotenv_values(".env")


def processJSON(jsonOBJ):
    [imageFile.update({"file": imageFile["file"].replace('.', '_')[
                      ::-1].replace('_', '.', 1)[::-1]}) for imageFile in jsonOBJ["images"]]
    [audioFile.update({"file": audioFile["file"].replace('.', '_')[
                      ::-1].replace('_', '.', 1)[::-1]}) for audioFile in jsonOBJ["audio"]]


@app.route("/", methods=["POST", "GET"])
def home():
    # Check if JWT exists
    token = request.cookies.get("token")
    if token:
        try:
            data = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
            if data["username"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("dashboard"))
        except jwt.InvalidTokenError:
            pass

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":
            data = jwt.encode(
                {"username": "admin"}, env["SECRET_KEY"], algorithm="HS256"
            )
            response = redirect(url_for("admin"))
            response.set_cookie("token", data)
            return response

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if not database.authenticate(username, hashed_password):
            return redirect(url_for("error", error="Invalid username or password"))

        # Store the username as a jwt token
        data = jwt.encode({"username": username},
                          env["SECRET_KEY"], algorithm="HS256")
        response = redirect(url_for("dashboard"))
        response.set_cookie("token", data)
        return response

    n_users, n_projects = database.getStats()
    return render_template("index.html", n_users=n_users, n_projects=n_projects)


@app.route("/signin")
def signin():
    return render_template("sign-in.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if database.userExists(username):
            return redirect(url_for("error", error="User already exists"))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Add user to database
        database.createUser(username, name, email, hashed_password)

        data = jwt.encode({"username": username},
                          env["SECRET_KEY"], algorithm="HS256")
        response = redirect(url_for("dashboard"))
        response.set_cookie("token", data)
        return response
    else:
        return render_template("sign-up.html")


# Create a new route for admin
@app.route("/admin")
def admin():
    # check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    user = database.getUser(token["username"])
    if user[1] != "admin":
        return redirect(url_for("home"))

    # get all users from the database with their username,
    #                                            name,
    #                                            email,
    #                                            no of projects
    users = database.getAdminView()
    n_users = len(users)
    n_projects = sum([user[3] for user in users])
    return render_template(
        "admin-dashboard.html", users=users, n_users=n_users, n_projects=n_projects
    )


@app.route("/dashboard")
def dashboard():
    # Check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return redirect(url_for("home"))
    if token["username"] == "admin":
        return redirect(url_for("admin"))
    user = database.getUser(token["username"])

    # get all projects from the database with their
    # project_name from the database
    projects = database.getProjects(user[1])
    # in each project, add an element to the tuple, which is the name of the
    # first file in the folder uploads/<username>/<project_id>/images
    for i in range(len(projects)):
        project_id = projects[i][0]
        username = user[1]

        thumbnail = database.getThumbnail(project_id)
        if thumbnail:
            # now check if the thumbnail is in the folder, name of thumbnail is thumbnail and format is thumbnail[2].split(".")[-1]
            thumb_name = f"thumbnail.{thumbnail[2].split('.')[-1]}"
            if not os.path.exists(f"uploads/{username}/{project_id}/{thumb_name}"):
                if not os.path.exists(f"uploads/{username}/{project_id}"):
                    if not os.path.exists(f"uploads/{username}"):
                        os.makedirs(f"uploads/{username}")
                    os.makedirs(f"uploads/{username}/{project_id}")
                with open(f"uploads/{username}/{project_id}/{thumb_name}", "wb") as f:
                    f.write(thumbnail[-1])
            projects[i] = projects[i] + (thumb_name,)
        else:
            projects[i] = projects[i] + ("",)

    # also check if the project is in the tasks table (still being processed)
    # and add a flag to the tuple using getTaskByProjectID
    for i in range(len(projects)):
        project_id = projects[i][0]
        task = database.getTaskByProjectID(project_id)
        if task:
            projects[i] = projects[i] + (False,)
        else:
            projects[i] = projects[i] + (True,)

    # get a random image from unplash and add it to the static/pfp folder with the name as username
    # if the image already exists, don't download it again

    if not os.path.exists("static/pfp"):
        os.makedirs("static/pfp")

    if not os.path.exists(f"static/pfp/{user[1]}.jpg"):
        import requests
        from PIL import Image
        from io import BytesIO

        response = requests.get("https://source.unsplash.com/random/200x200")
        img = Image.open(BytesIO(response.content))
        img.save(f"static/pfp/{user[1]}.jpg")

    return render_template(
        "dashboard.html", username=user[1], name=user[2], projects=projects
    )


@app.route("/project-editor", methods=["POST", "GET"])
def create():
    # Check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Convert token to bytes
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return redirect(url_for("home"))
    if token["username"] == "admin":
        return redirect(url_for("admin"))

    # Check if the user is on a mobile device
    user_agent = request.user_agent.string.lower()
    if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
        return redirect(
            url_for(
                "error",
                error="This feature is not available on mobile devices. \
Please use a desktop or desktop mode to access this feature.",
            )
        )
    user = database.getUser(token["username"])

    # Clear the uploads/username/-1 folder
    if os.path.exists(f"uploads/{user[1]}/-1"):
        os.system(f"rm -rf uploads/{user[1]}/-1")

    # create the above folder
    os.makedirs(f"uploads/{user[1]}/-1")
    os.makedirs(f"uploads/{user[1]}/-1/images")
    os.makedirs(f"uploads/{user[1]}/-1/audio")

    # get all the audio files from the static/audio folder and copy them to username/-1/audio
    for file in os.listdir(os.path.join(app.static_folder, 'audio')):
        os.system(f"cp {os.path.join(app.static_folder, 'audio')}" +
                  f"/{file} uploads/{user[1]}/-1/audio/{file}")

    # get all the existing images and audio files from the database and copy
    # them to username/-1/images and username/-1/audio
    files = database.getFiles(user[1])
    for file in files:
        if file[2].split(".")[-1] in ['apng', 'avif', 'bmp', 'gif', 'ico', 'cur', 'jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'png', 'svg', 'webp']:
            with open(f"uploads/{user[1]}/-1/images/{file[2]}", "wb") as f:
                f.write(file[3])
        else:
            with open(f"uploads/{user[1]}/-1/audio/{file[2]}", "wb") as f:
                f.write(file[3])

    images = ','.join(os.listdir(f"uploads/{user[1]}/-1/images"))
    audio = ','.join(os.listdir(f"uploads/{user[1]}/-1/audio"))

    return render_template("project-editor.html", name=user[2], images=images, audio=audio, server_bad=(env["SERVER_BAD"] == "YES"))


@app.route("/submit", methods=["POST"])
def submit():
    # Check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return redirect(url_for("home"))
    if token["username"] == "admin":
        return redirect(url_for("admin"))

    user = database.getUser(token["username"])
    username = user[1]

    # get the json file as a text field sent from the form
    project_json = json.loads(request.form.get("json"))
    processJSON(project_json)

    project_id = database.createProject(
        project_json["name"], username
    )  # also adds it to tasks

    # If folder doesn't exist
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists(f"uploads/{username}"):
        os.makedirs(f"uploads/{username}")
    if not os.path.exists(f"uploads/{username}/{project_id}"):
        os.makedirs(f"uploads/{username}/{project_id}")
    with open(f"uploads/{username}/{project_id}/project_data.json", "w") as json_file:
        json.dump(project_json, json_file)

    os.makedirs(f"uploads/{username}/{project_id}/images")
    os.makedirs(f"uploads/{username}/{project_id}/audio")

    for file in os.listdir(f"uploads/{username}/-1/images"):
        os.system(
            f"cp uploads/{username}/\"-1\"/images/{file} uploads/{username}/\"{project_id}\"/images/{file}")

    for file in os.listdir(f"uploads/{username}/-1/audio"):
        os.system(
            f"cp uploads/{username}/\"-1\"/audio/{file} uploads/{username}/\"{project_id}\"/audio/{file}")

    thread = Thread(target=create_video, args=(username, str(project_id)))
    thread.start()

    os.system(f"rm -rf uploads/{username}/\"-1\"")

    return redirect(url_for("dashboard"))


@app.route("/preview", methods=["POST"])
def preview():
    # Check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return "Not authorised.", 400
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return "Not authorised.", 400
    if token["username"] == "admin":
        return "Not authorised.", 400

    user = database.getUser(token["username"])
    username = user[1]

    # get the json file as a text field sent from the above fetch request
    project_json = request.json
    processJSON(project_json)

    project_id = -1

    # If folder doesn't exist
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    if not os.path.exists(f"uploads/{username}"):
        os.makedirs(f"uploads/{username}")
    if not os.path.exists(f"uploads/{username}/images"):
        os.makedirs(f"uploads/{username}/images")
    if not os.path.exists(f"uploads/{username}/audio"):
        os.makedirs(f"uploads/{username}/audio")
    if not os.path.exists(f"uploads/{username}/{project_id}"):
        os.makedirs(f"uploads/{username}/{project_id}")
    with open(f"uploads/{username}/{project_id}/project_data.json", "w") as json_file:
        json.dump(project_json, json_file)

    # get the files from the uploads/username folder and move them to
    # the uploads/username/project_id folder
    # move the images to uploads/username/project_id/images
    # move the audio to uploads/username/project_id/audio

    if not os.path.exists(f"uploads/{username}/{project_id}/images"):
        os.makedirs(f"uploads/{username}/{project_id}/images")
    if not os.path.exists(f"uploads/{username}/{project_id}/audio"):
        os.makedirs(f"uploads/{username}/{project_id}/audio")

    # go to the uploads/username/images folder and copy all the files to
    # the uploads/username/project_id/images folder
    for file in os.listdir(f"uploads/{username}/images"):
        os.system(
            f"cp uploads/{username}/images/{file} uploads/{username}/\"{project_id}\"/images/{file}")
    # go to the uploads/username/audio folder and copy all the files to
    # the uploads/username/project_id/audio folder
    for file in os.listdir(f"uploads/{username}/audio"):
        os.system(
            f"cp uploads/{username}/audio/{file} uploads/{username}/\"{project_id}\"/audio/{file}")

    # create a new thread to create the video
    thread = Thread(target=create_video, args=(username, str(project_id)))
    thread.start()

    # wait for the thread to stop
    thread.join()

    return "Preview successfully rendered", 200


@app.route("/upload_files", methods=["POST"])
def upload_files():
    # Check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return redirect(url_for("home"))
    if token["username"] == "admin":
        return redirect(url_for("admin"))

    user = database.getUser(token["username"])
    username = user[1]

    # check if the post request has the file part
    if "file" not in request.files:
        return "No file part in the request.", 400

    files = request.files.getlist("file")

    for file in files:
        if file.filename == "":
            pass
        # If folder doesn't exist
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
        if not os.path.exists(f"uploads/{username}"):
            os.makedirs(f"uploads/{username}")
        if (not os.path.exists(f"uploads/{username}/images")
                or not os.path.exists(f"uploads/{username}/audio")):
            os.makedirs(f"uploads/{username}/images")
            os.makedirs(f"uploads/{username}/audio")

        # do equivalent of file.name.replace(/[^a-zA-Z0-9_.]/g, '')
        fname = "".join(
            [c for c in file.filename if c.isalnum() or c in ["_", "."]]
        )
        fname = fname.replace(".", "_")
        fname = fname[::-1].replace("_", ".", 1)[::-1]
        # Check the MIME type of the file
        if file.content_type.startswith("image/"):
            file.save(f"uploads/{username}/images/" + fname)
        elif file.content_type.startswith("audio/"):
            file.save(f"uploads/{username}/audio/" + fname)
        else:
            return (
                "Unsupported file type: "
                + file.name
                + "! Please upload an image or audio file."
            )
        # read the file and save it to the database
        file.seek(0)
        file = file.read()
        database.saveFile(username, fname, file)

    return "Files successfully uploaded", 200


@app.route("/signout")
def signout():
    response = redirect(url_for("home"))
    response.set_cookie("token", expires=0)
    return response


@app.route("/error/<error>")
def error(error):
    return render_template("error.html", error=error)


@app.route("/uploads/<username>/<project_id>/<media_type>/<filename>")
def uploaded_file(username, project_id, media_type, filename):
    # first check if user is authenticated
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return redirect(url_for("home"))
    if token["username"] == "admin":
        return redirect(url_for("admin"))

    # check if user is the owner of the project
    if token["username"] != username:
        return redirect(
            url_for("error", error="You are not authorized to view this file")
        )
    return send_from_directory(
        f"uploads/{username}/{project_id}/{media_type}", filename
    )


@app.route("/download/<username>/<project_id>")
def download(username, project_id):
    database.getThumbnail(project_id)
    # first check if user is authenticated
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return redirect(url_for("home"))
    if token["username"] == "admin":
        return redirect(url_for("admin"))

    # check if user is the owner of the project
    if token["username"] != username:
        return redirect(
            url_for("error", error="You are not authorized to download this project")
        )

    # check if the project is in the tasks table (still being processed)
    task = database.getTaskByProjectID(project_id)
    if task:
        return redirect(
            url_for(
                "error",
                error="The project is still being processed. Please try again later.",
            )
        )

    result = database.getVideo(project_id)
    if not result:
        return redirect(
            url_for(
                "error", error="The video does not exist. Please try again later.")
        )
    video_blob, json_data = result[2], result[3]

    # Parse the json data to get the video name and format
    data = json.loads(json_data)
    video_name = data['name']
    video_format = data['format']

    # Create the directory if it doesn't exist
    # directory is uploads/username/project_id
    directory = f"uploads/{username}/{project_id}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the video blob to a file
    video_path = os.path.join(directory, f'{video_name}.{video_format}')
    with open(video_path, 'wb') as f:
        f.write(video_blob)

    return send_from_directory(
        directory, f"{video_name}.{video_format}", as_attachment=True
    )


@app.route("/delete/<username>/<project_id>")
def delete(username, project_id):
    # first check if user is authenticated
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return redirect(url_for("home"))
    if token["username"] == "admin":
        return redirect(url_for("admin"))

    # check if user is the owner of the project
    if token["username"] != username:
        return redirect(
            url_for("error",
                    error="You are not authorized to delete this project")
        )

    # check if the project is in the tasks table (still being processed)
    task = database.getTaskByProjectID(project_id)
    if task:
        return redirect(
            url_for(
                "error",
                error="The project is still being processed. Please try again later.",
            )
        )

    # delete the project from the database
    database.deleteProject(project_id)

    # delete the project folder
    # first check if the folder exists
    if os.path.exists(f"uploads/{username}/{project_id}"):
        os.system(f"rm -rf uploads/{username}/{project_id}")

    return redirect(url_for("dashboard"))


@app.route("/get_preview")
def get_preview():
    # first check if user is authenticated
    token = request.cookies.get("token")
    if not token:
        return "Not authorised.", 400
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return "Not authorised.", 400
    if token["username"] == "admin":
        return "Not authorised.", 400

    user = database.getUser(token["username"])
    username = user[1]

    # send the preview video to the user, from the uploads/username/-1 folder
    # if the video exists
    if os.path.exists(f"uploads/{username}/-1"):
        # get the project name
        with open(f"uploads/{username}/-1/project_data.json") as json_file:
            project_json = json.load(json_file)
            project_name = project_json["name"]
            video_format = project_json["format"]

        return send_from_directory(
            f"uploads/{username}/-1", f"{project_name}.{video_format}"
        )
    else:
        return "The preview does not exist.", 400


@app.route("/get_thumbnail/<username>/<project_id>/<filename>")
def get_thumbnail(username, project_id, filename):
    # first check if user is authenticated
    token = request.cookies.get("token")
    if not token:
        return "Not authorised.", 400
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return "Not authorised.", 400
    if token["username"] == "admin":
        return "Not authorised.", 400

    # check if user is the owner of the project
    if token["username"] != username:
        return "Not authorised.", 400

    # return the thumbnail
    return send_from_directory(
        f"uploads/{username}/{project_id}", filename
    )


@app.route("/get_samples/<media_type>/<filename>")
def get_samples(media_type, filename):
    # first check if user is authenticated
    token = request.cookies.get("token")
    if not token:
        return "Not authorised.", 400
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    if not database.userExists(token["username"]):
        return "Not authorised.", 400
    if token["username"] == "admin":
        return "Not authorised.", 400

    if os.path.exists(f"uploads/{token['username']}/-1/{media_type}/{filename}"):
        return send_from_directory(
            f"uploads/{token['username']}/-1/{media_type}", filename
        )
    else:
        return "The sample does not exist.", 400


if __name__ == "__main__":
    app.run()
