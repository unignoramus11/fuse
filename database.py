from dotenv import dotenv_values
env = dotenv_values(".env")

if env["SERVER_BAD"] == "YES":
    import json
    import psycopg2
    import psycopg2.pool

    global db_pool
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1,  # minconn: start with 1 connection
        10000,  # maxconn: max 10000 connections
        env["DB_URL"],
        connect_timeout=10  # timeout in seconds
    )

    def get_conn():
        # Get a connection from the pool
        return db_pool.getconn()

    def return_conn(conn):
        # Return a connection to the pool
        db_pool.putconn(conn)

    def createDatabase():
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("CREATE DATABASE IF NOT EXISTS fuse")
            mycursor.execute("USE fuse")
            mycursor.execute(
                "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(255) UNIQUE, name VARCHAR(255), email VARCHAR(255), password VARCHAR(1024), noOfProjects INT)"
            )
            mycursor.execute(
                "CREATE TABLE IF NOT EXISTS projects (id SERIAL PRIMARY KEY, name VARCHAR(255), user_username VARCHAR(255), FOREIGN KEY (user_username) REFERENCES users(username))"
            )
            mycursor.execute(
                "CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, name VARCHAR(255), project_id INT, FOREIGN KEY (project_id) REFERENCES projects(id))"
            )
            # add admin user
            mycursor.execute(
                "INSERT INTO users (username, password) VALUES ('admin', 'admin') ON CONFLICT DO NOTHING"
            )
            mycursor.execute(
                "CREATE TABLE IF NOT EXISTS files (id SERIAL PRIMARY KEY, username VARCHAR(255), filename VARCHAR(255), file BYTEA, FOREIGN KEY (username) REFERENCES users(username))"
            )

            mycursor.execute(
                "CREATE TABLE IF NOT EXISTS videos (id SERIAL PRIMARY KEY, project_id INT, video BYTEA, json_data TEXT, FOREIGN KEY (project_id) REFERENCES projects(id))"
            )

            mydb.commit()
            mycursor.close()
        finally:
            return_conn(mydb)

    def createUser(username, name, email, password):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "INSERT INTO users (username, name, email, password, noOfProjects) VALUES (%(username)s, %(name)s, %(email)s, %(password)s, 0)",
                {"username": username, "name": name,
                    "email": email, "password": password},
            )
            mydb.commit()
            mycursor.close()
        finally:
            return_conn(mydb)

    def createProject(name, username):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "INSERT INTO projects (name, user_username) VALUES (%(name)s, %(username)s) RETURNING id",
                {"username": username, "name": name},
            )

            project_id = mycursor.fetchone()[0]

            mycursor.execute(
                "UPDATE users SET noOfProjects = noOfProjects + 1 WHERE username = %(username)s",
                {"username": username},
            )

            mycursor.execute(
                "INSERT INTO tasks (name, project_id) VALUES (%(name)s, %(project_id)s)",
                {"name": name, "project_id": project_id},
            )
            mydb.commit()
            mycursor.close()
        finally:
            return_conn(mydb)

        return project_id

    def userExists(username):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM users WHERE username = %(username)s", {
                    "username": username}
            )
            user = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        return user is not None

    def getAdminView():
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT username, name, email, noOfProjects FROM users WHERE username != 'admin'"
            )
            result = mycursor.fetchall()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getFile(username, filename):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM files WHERE username = %(username)s AND filename = %(filename)s",
                {"username": username, "filename": filename},
            )
            result = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getFiles(username):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM files WHERE username = %(username)s",
                {"username": username},
            )
            result = mycursor.fetchall()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def saveFile(username, filename, file):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")

            # if file with the same name exists, add a number to the end of the filename and try again
            i = 1
            while getFile(username, filename):
                filename = f"{filename.split('.')[0]}_{i}.{filename.split('.')[1]}"
                i += 1

            mycursor.execute(
                "INSERT INTO files (username, filename, file) VALUES (%(username)s, %(filename)s, %(file)s)",
                {"username": username, "filename": filename, "file": file},
            )
            mydb.commit()
            mycursor.close()
        finally:
            return_conn(mydb)

    def getUser(username):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM users WHERE username = %(username)s", {
                    "username": username}
            )
            result = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getProjects(username):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM projects WHERE user_username = %(username)s ORDER BY id DESC",
                {"username": username},
            )
            result = mycursor.fetchall()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getTasks(project_id):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM tasks WHERE project_id = %(project_id)s",
                {"project_id": project_id},
            )
            result = mycursor.fetchall()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getProject(project_id):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM projects WHERE id = %(project_id)s", {
                    "project_id": project_id}
            )
            result = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getTask(task_id):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM tasks WHERE id = %(task_id)s", {"task_id": task_id})
            result = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getTaskByProjectID(project_id):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM tasks WHERE project_id = %(project_id)s", {
                    "project_id": project_id}
            )
            result = mycursor.fetchall()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def authenticate(username, password):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM users WHERE username = %(username)s AND password = %(password)s",
                {"username": username, "password": password},
            )
            result = mycursor.fetchone() is not None
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getLastProject(username):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM projects WHERE user_username = %(username)s ORDER BY id DESC LIMIT 1",
                {"username": username},
            )
            result = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def removeTask(project_id):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute("DELETE FROM tasks WHERE project_id = %(project_id)s", {
                "project_id": project_id})
            mydb.commit()
            mycursor.close()
        finally:
            return_conn(mydb)

    def removeVideo(project_id):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute("DELETE FROM videos WHERE project_id = %(project_id)s", {
                "project_id": project_id})
            mydb.commit()
            mycursor.close()
        finally:
            return_conn(mydb)

    def deleteProject(project_id):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            removeTask(project_id)
            removeVideo(project_id)
            mycursor.execute("DELETE FROM projects WHERE id = %(project_id)s", {
                "project_id": project_id})
            mydb.commit()
            mycursor.close()
        finally:
            return_conn(mydb)

    def getStats():
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            # get number of projects as sum of the values in the column noOfProjects
            mycursor.execute("SELECT SUM(noOfProjects) FROM users")
            n_projects = mycursor.fetchone()[0]
            mycursor.execute(
                "SELECT COUNT(*) FROM users WHERE username != 'admin'")
            n_users = mycursor.fetchone()[0]
            mycursor.close()
        finally:
            return_conn(mydb)

        return n_users, n_projects

    def saveVideo(project_id, video, json_data):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "INSERT INTO videos (project_id, video, json_data) VALUES (%(project_id)s, %(video)s, %(json_data)s)",
                {"project_id": project_id, "video": video, "json_data": json_data},
            )
            mydb.commit()
            mycursor.close()
        finally:
            return_conn(mydb)

    def getVideo(project_id):
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM videos WHERE project_id = %(project_id)s",
                {"project_id": project_id},
            )
            result = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    def getThumbnail(project_id):
        # get the first image present int the json file of the project in video table
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT json_data FROM videos WHERE project_id = %(project_id)s",
                {"project_id": project_id},
            )
            result = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        if result is None:
            return None

        result = result[0]

        result = json.loads(result)
        thumbnail_file_name = result["images"][0]["file"]

        # get the username of the project
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT user_username FROM projects WHERE id = %(project_id)s",
                {"project_id": project_id},
            )
            username = mycursor.fetchone()[0]
            mycursor.close()
        finally:
            return_conn(mydb)

        # get the file from the files table
        mydb = get_conn()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("USE fuse")
            mycursor.execute(
                "SELECT * FROM files WHERE username = %(username)s AND filename = %(filename)s",
                {"username": username, "filename": thumbnail_file_name},
            )
            result = mycursor.fetchone()
            mycursor.close()
        finally:
            return_conn(mydb)

        return result

    createDatabase()

else:
    import mysql.connector
    import json

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
        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS files (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), filename VARCHAR(255), file LONGBLOB, FOREIGN KEY (username) REFERENCES users(username))"
        )

        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS videos (id INT AUTO_INCREMENT PRIMARY KEY, project_id INT, video LONGBLOB, json_data TEXT, FOREIGN KEY (project_id) REFERENCES projects(id))"
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
            {"username": username, "name": name,
                "email": email, "password": password},
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

    def getFile(username, filename):
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        mycursor.execute(
            "SELECT * FROM files WHERE username = %(username)s AND filename = %(filename)s",
            {"username": username, "filename": filename},
        )
        result = mycursor.fetchone()
        mycursor.close()
        mydb.close()

        return result

    def getFiles(username):
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        mycursor.execute(
            "SELECT * FROM files WHERE username = %(username)s",
            {"username": username},
        )
        result = mycursor.fetchall()
        mycursor.close()
        mydb.close()

        return result

    def saveFile(username, filename, file):
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")

        # if file with the same name exists, add a number to the end of the filename and try again
        i = 1
        while getFile(username, filename):
            filename = f"{filename.split('.')[0]}_{i}.{filename.split('.')[1]}"
            i += 1

        mycursor.execute(
            "INSERT INTO files (username, filename, file) VALUES (%(username)s, %(filename)s, %(file)s)",
            {"username": username, "filename": filename, "file": file},
        )
        mydb.commit()
        mycursor.close()
        mydb.close()

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

    def removeVideo(project_id):
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        mycursor.execute("DELETE FROM videos WHERE project_id = %(project_id)s", {
            "project_id": project_id})
        mydb.commit()
        mycursor.close()
        mydb.close()

    def deleteProject(project_id):
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        removeTask(project_id)
        removeVideo(project_id)
        mycursor.execute("DELETE FROM projects WHERE id = %(project_id)s", {
            "project_id": project_id})
        mydb.commit()
        mycursor.close()
        mydb.close()

    def getStats():
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        # get number of projects as sum of the values in the column noOfProjects
        mycursor.execute("SELECT SUM(noOfProjects) FROM users")
        n_projects = mycursor.fetchone()[0]
        mycursor.execute(
            "SELECT COUNT(*) FROM users WHERE username != 'admin'")
        n_users = mycursor.fetchone()[0]
        mycursor.close()
        mydb.close()

        return n_users, n_projects

    def saveVideo(project_id, video, json_data):
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        mycursor.execute(
            "INSERT INTO videos (project_id, video, json_data) VALUES (%(project_id)s, %(video)s, %(json_data)s)",
            {"project_id": project_id, "video": video, "json_data": json_data},
        )
        mydb.commit()
        mycursor.close()
        mydb.close()

    def getVideo(project_id):
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        mycursor.execute(
            "SELECT * FROM videos WHERE project_id = %(project_id)s",
            {"project_id": project_id},
        )
        result = mycursor.fetchone()
        mycursor.close()
        mydb.close()

        return result

    def getThumbnail(project_id):
        # get the first image present int the json file of the project in video table
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        mycursor.execute(
            "SELECT json_data FROM videos WHERE project_id = %(project_id)s",
            {"project_id": project_id},
        )
        result = mycursor.fetchone()
        mycursor.close()
        mydb.close()

        if result is None:
            return None

        result = result[0]

        result = json.loads(result)
        thumbnail_file_name = result["images"][0]["file"]

        # get the username of the project
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        mycursor.execute(
            "SELECT user_username FROM projects WHERE id = %(project_id)s",
            {"project_id": project_id},
        )
        username = mycursor.fetchone()[0]
        mycursor.close()
        mydb.close()

        # get the file from the files table
        mydb = mysql.connector.connect(user="root", password=env["PASSWORD"])
        mycursor = mydb.cursor()
        mycursor.execute("USE fuse")
        mycursor.execute(
            "SELECT * FROM files WHERE username = %(username)s AND filename = %(filename)s",
            {"username": username, "filename": thumbnail_file_name},
        )
        result = mycursor.fetchone()
        mycursor.close()
        mydb.close()

        return result

    createDatabase()
