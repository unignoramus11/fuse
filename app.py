from flask import Flask, redirect, url_for, render_template, request
from dotenv import dotenv_values
import os
import jwt
import hashlib
import database
import json
from tqdm import tqdm

app = Flask(__name__)
env = dotenv_values(".env")


@app.route("/", methods=["POST", "GET"])
def home():
    # Check if JWT exists
    token = request.cookies.get("token")
    if token:
        try:
            data = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
            return redirect(url_for("dashboard"))
        except jwt.InvalidTokenError:
            pass

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":
            return redirect(url_for("admin"))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if not database.authenticate(username, hashed_password):
            return redirect(url_for("error", error="Invalid username or password"))

        # Store the username as a jwt token
        data = jwt.encode({"username": username},
                          env["SECRET_KEY"], algorithm="HS256")
        response = redirect(url_for("dashboard"))
        response.set_cookie("token", data)
        return response

    return render_template("index.html")


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
    return render_template("admin-dashboard.html")


@app.route("/dashboard")
def dashboard():
    # Check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    user = database.getUser(token["username"])
    return render_template("dashboard.html", username=user[1], name=user[2])


@app.route("/project-editor", methods=["POST", "GET"])
def create():
    # Check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))

    # Check if the user is on a mobile device
    user_agent = request.user_agent.string.lower()
    if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
        return redirect(
            url_for(
                "error",
                error="This feature is not available on mobile devices. \
Please use a computer to access this feature.",
            )
        )
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    user = database.getUser(token["username"])
    return render_template("project-editor.html", name=user[2])


@app.route("/upload_file", methods=["POST"])
def upload_file():
    # Check if JWT exists
    token = request.cookies.get("token")
    if not token:
        return redirect(url_for("home"))
    # Decode the token
    token = jwt.decode(token, env["SECRET_KEY"], algorithms=["HS256"])
    user = database.getUser(token["username"])
    username = user[1]

    # TODO: get project name from the form
    # get the json file as a text field sent from the form
    project_json = json.loads(request.form.get("json"))

    project_id = database.createProject(
        project_json["name"], username
    )  # also adds it to tasks

    # Images here is actually all media files
    if "images" not in request.files:
        return redirect(
            url_for("error", error="Something went wrong! Please try again.")
        )
    files = request.files.getlist("images")
    total_files = len(files)
    progress_bar = tqdm(total=total_files, desc="Uploading files", unit="file")

    for file in files:
        if file.filename == "":
            print(file, end="\n---\n")
        if file:
            # If folder doesn't exist
            if not os.path.exists(f"uploads/{username}"):
                os.makedirs(f"uploads/{username}")
            if not os.path.exists(f"uploads/{username}/{project_id}"):
                os.makedirs(f"uploads/{username}/{project_id}")
                with open(
                    f"uploads/{username}/{project_id}/project_data.json", "w"
                ) as json_file:
                    json.dump(project_json, json_file)
                os.makedirs(f"uploads/{username}/{project_id}/images")
                os.makedirs(f"uploads/{username}/{project_id}/audio")

            # Check the MIME type of the file
            if file.content_type.startswith("image/"):
                file.save(
                    f"uploads/{username}/{project_id}/images/" + file.filename)
            elif file.content_type.startswith("audio/"):
                file.save(
                    f"uploads/{username}/{project_id}/audio/" + file.filename)
            else:
                return (
                    "Unsupported file type: "
                    + file.name
                    + "! Please upload an image or audio file."
                )

        progress_bar.update(1)

    progress_bar.close()

    return redirect(url_for("dashboard"))


@app.route("/signout")
def signout():
    response = redirect(url_for("home"))
    response.set_cookie("token", expires=0)
    return response


@app.route("/error/<error>")
def error(error):
    return render_template("error.html", error=error)


if __name__ == "__main__":
    app.run()
