from dotenv import dotenv_values
import mysql.connector
import os

env = dotenv_values(".env")
print(env)

mydb = mysql.connector.connect(user=env["USER"], password=env["PASSWORD"])
mycursor = mydb.cursor()


def getUser(user_id):
    mycursor.execute(f"SELECT * FROM users WHERE id")
    return mycursor.fetchall()
