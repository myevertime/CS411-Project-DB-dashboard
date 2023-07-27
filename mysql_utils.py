import mysql.connector

def mysql_connector():
# Connect to the MySQL database (Make sure to update the credentials)
    db_connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='test_root',
        database='academicworld'
    )
    return db_connection