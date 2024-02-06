from flask import Flask, redirect, url_for, render_template, request
# import mysql.connector

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signin", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        return redirect(url_for("profile", usr=user))
    else:
        return render_template("sign-in.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        return redirect(url_for("profile", usr=user))
    else:
        return render_template("sign-up.html")


# Create a new route for admin
@app.route("/admin")
def admin():
    return render_template("tables.html")


@app.route("/profile/<usr>")
def profile(usr):
    return render_template("profile.html", user=usr)


@app.route("/project-editor")
def create():
    return render_template("project.html")


if __name__ == "__main__":
    app.run()
