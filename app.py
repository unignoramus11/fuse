from flask import (
    Flask,
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

# from tqdm import tqdm

app = Flask(__name__)
env = dotenv_values(".env")


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
        if os.path.exists(f"uploads/{username}/{project_id}/images"):
            images = os.listdir(f"uploads/{username}/{project_id}/images")
            if images:
                projects[i] = projects[i] + (images[0],)
            else:
                projects[i] = projects[i] + ("",)
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
Please use a desktop to access this feature.",
            )
        )
    user = database.getUser(token["username"])
    return render_template("project-editor.html", name=user[2])


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

    # get the files from the uploads/username folder and move them to
    # the uploads/username/project_id folder
    # move the images to uploads/username/project_id/images
    # move the audio to uploads/username/project_id/audio

    os.makedirs(f"uploads/{username}/{project_id}/images")
    os.makedirs(f"uploads/{username}/{project_id}/audio")

    # now go to the uploads/username/images folder and move all the files to
    # the uploads/username/project_id/images folder
    for file in os.listdir(f"uploads/{username}/images"):
        os.rename(
            f"uploads/{username}/images/{file}",
            f"uploads/{username}/{project_id}/images/{file}",
        )
    # now go to the uploads/username/audio folder and move all the files to
    # the uploads/username/project_id/audio folder
    for file in os.listdir(f"uploads/{username}/audio"):
        os.rename(
            f"uploads/{username}/audio/{file}",
            f"uploads/{username}/{project_id}/audio/{file}",
        )

    # open a new thread to create the video, on render.py create_video function
    # create_video(username, project_id)

    # create a new thread to create the video
    thread = Thread(target=create_video, args=(username, str(project_id)))
    thread.start()

    return redirect(url_for("dashboard"))


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

        # replace all whitespace with underscores
        # also do this for file names with multiple dots
        # first get the filename with all dots replaced with underscores
        fname = file.filename.replace(" ", "_")
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

    # get the video name and format from json file in the project folder
    with open(f"uploads/{username}/{project_id}/project_data.json") as json_file:
        project_json = json.load(json_file)
        project_name = project_json["name"]
        video_format = project_json["format"]

    video_name = f"{project_name}.{video_format}"
    # check if the video exists
    if not os.path.exists(f"uploads/{username}/{project_id}/{video_name}"):
        return redirect(
            url_for(
                "error", error="The video does not exist. Please try again later.")
        )
    return send_from_directory(
        f"uploads/{username}/{project_id}", video_name, as_attachment=True
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


if __name__ == "__main__":
    app.run()
