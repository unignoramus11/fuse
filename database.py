from dotenv import dotenv_values
import mysql.connector

env = dotenv_values(".env")

mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
mycursor = mydb.cursor()


def createDatabase():
    mycursor.execute("CREATE DATABASE IF NOT EXISTS fuse")
    mycursor.execute("USE fuse")
    mycursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE, name VARCHAR(255), email VARCHAR(255), password VARCHAR(1024), noOfProjects INT)"
    )
    mycursor.execute(
        "CREATE TABLE IF NOT EXISTS projects (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), user_username VARCHAR(255), FOREIGN KEY (user_username) REFERENCES users(username))"
    )
    mycursor.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), project_id INT, FOREIGN KEY (project_id) REFERENCES projects(id))"
    )
    # add admin user
    mycursor.execute(
        "INSERT IGNORE INTO users (username, password) VALUES ('admin', 'admin')"
    )
    mydb.commit()


def createUser(username, name, email, password):
    mycursor.execute(
        "INSERT INTO users (username, name, email, password, noOfProjects) VALUES (%(username)s, %(name)s, %(email)s, %(password)s, 0)",
        {"username": username, "name": name, "email": email, "password": password},
    )
    mydb.commit()


def createProject(name, username):
    mycursor.execute(
        "INSERT INTO projects (name, user_username) VALUES (%(name)s, %(username)s)",
        {"username": username, "name": name},
    )
    mycursor.execute(
        "UPDATE users SET noOfProjects = noOfProjects + 1 WHERE username = %(username)s",
        {"username": username},
    )

    mycursor.execute("SELECT LAST_INSERT_ID()")

    project_id = mycursor.fetchone()[0]
    mycursor.execute(
        "INSERT INTO tasks (name, project_id) VALUES (%(name)s, %(project_id)s)",
        {"name": name, "project_id": project_id},
    )
    mydb.commit()

    return project_id


def userExists(username):
    mycursor.execute(
        "SELECT * FROM users WHERE username = %(username)s", {"username": username}
    )
    user = mycursor.fetchone()
    return user != None


def getAdminView():
    mycursor.execute("SELECT username, noOfProjects FROM users WHERE username != 'admin'")
    return mycursor.fetchall()


def getUser(username):
    mycursor.execute(
        "SELECT * FROM users WHERE username = %(username)s", {"username": username}
    )
    return mycursor.fetchone()


def getProjects(username):
    mycursor.execute(
        "SELECT * FROM projects WHERE user_username = %(username)s ORDER BY id DESC",
        {"username": username},
    )
    return mycursor.fetchall()


def getTasks(project_id):
    mycursor.execute(
        "SELECT * FROM tasks WHERE project_id = %(project_id)s",
        {"project_id": project_id},
    )
    return mycursor.fetchall()


def getProject(project_id):
    mycursor.execute(
        "SELECT * FROM projects WHERE id = %(project_id)s", {"project_id": project_id}
    )
    return mycursor.fetchone()


def getTask(task_id):
    mycursor.execute("SELECT * FROM tasks WHERE id = %(task_id)s", {"task_id": task_id})
    return mycursor.fetchone()


def authenticate(username, password):
    mycursor.execute(
        "SELECT * FROM users WHERE username = %(username)s AND password = %(password)s",
        {"username": username, "password": password},
    )
    return mycursor.fetchone() != None


def getLastProject(username):
    mycursor.execute(
        "SELECT * FROM projects WHERE user_username = %(username)s ORDER BY id DESC LIMIT 1",
        {"username": username},
    )
    return mycursor.fetchone()


createDatabase()
