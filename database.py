from dotenv import dotenv_values
import mysql.connector

env = dotenv_values(".env")


def createDatabase():
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
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
    mycursor.close()
    mydb.close()


def createUser(username, name, email, password):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "INSERT INTO users (username, name, email, password, noOfProjects) VALUES (%(username)s, %(name)s, %(email)s, %(password)s, 0)",
        {"username": username, "name": name, "email": email, "password": password},
    )
    mydb.commit()
    mycursor.close()
    mydb.close()


def createProject(name, username):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
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
    mycursor.close()
    mydb.close()

    return project_id


def userExists(username):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM users WHERE username = %(username)s", {
            "username": username}
    )
    user = mycursor.fetchone()
    mycursor.close()
    mydb.close()

    return user is not None


def getAdminView():
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT username, name, email, noOfProjects FROM users WHERE username != 'admin'"
    )
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return result


def getUser(username):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM users WHERE username = %(username)s", {
            "username": username}
    )
    result = mycursor.fetchone()
    mycursor.close()
    mydb.close()

    return result


def getProjects(username):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM projects WHERE user_username = %(username)s ORDER BY id DESC",
        {"username": username},
    )
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return result


def getTasks(project_id):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM tasks WHERE project_id = %(project_id)s",
        {"project_id": project_id},
    )
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return result


def getProject(project_id):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM projects WHERE id = %(project_id)s", {
            "project_id": project_id}
    )
    result = mycursor.fetchone()
    mycursor.close()
    mydb.close()

    return result


def getTask(task_id):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM tasks WHERE id = %(task_id)s", {"task_id": task_id})
    result = mycursor.fetchone()
    mycursor.close()
    mydb.close()

    return result


def getTaskByProjectID(project_id):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM tasks WHERE project_id = %(project_id)s", {
            "project_id": project_id}
    )
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()

    return result


def authenticate(username, password):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM users WHERE username = %(username)s AND password = %(password)s",
        {"username": username, "password": password},
    )
    result = mycursor.fetchone() is not None
    mycursor.close()
    mydb.close()

    return result


def getLastProject(username):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute(
        "SELECT * FROM projects WHERE user_username = %(username)s ORDER BY id DESC LIMIT 1",
        {"username": username},
    )
    result = mycursor.fetchone()
    mycursor.close()
    mydb.close()

    return result


def removeTask(project_id):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute("DELETE FROM tasks WHERE project_id = %(project_id)s", {
                     "project_id": project_id})
    mydb.commit()
    mycursor.close()
    mydb.close()


def deleteProject(project_id):
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    removeTask(project_id)
    mycursor.execute("DELETE FROM projects WHERE id = %(project_id)s", {
                     "project_id": project_id})
    mydb.commit()
    mycursor.close()
    mydb.close()


def getStats():
    mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
    mycursor = mydb.cursor()
    mycursor.execute("USE fuse")
    mycursor.execute("SELECT COUNT(*) FROM users")
    n_users = mycursor.fetchone()[0]
    mycursor.execute("SELECT COUNT(*) FROM projects")
    n_projects = mycursor.fetchone()[0]
    mycursor.close()
    mydb.close()

    return n_users, n_projects


createDatabase()
