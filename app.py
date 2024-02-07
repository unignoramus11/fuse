from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signin", methods=["POST", "GET"])
def signin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Fetch user from database
        # TODO: make it so that it send the name instead of username
        name = username

        if name == "admin" and password == "admin":
            return redirect(url_for("admin"))

        return redirect(url_for("profile", name=name))
    else:
        return render_template("sign-in.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Create a user
        user = {
            "username": username,
            "name": name,
            "email": email,
            "password": password,
        }

        # Add user to database

        return redirect(url_for("profile", name=username))
    else:
        return render_template("sign-up.html")


# Create a new route for admin
@app.route("/admin")
def admin():
    return render_template("admin-dashboard.html")


@app.route("/profile/<name>")
def profile(name):
    return render_template("profile.html", name=name)


@app.route("/project-editor")
def create():
    return render_template("project.html")


if __name__ == "__main__":
    app.run()
