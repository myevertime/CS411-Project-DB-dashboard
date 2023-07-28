import mysql.connector
from mysql.connector import pooling


def mysql_connector():
    db_connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='test_root',
        database='academicworld'
    )
    return db_connection

def mysql_connector_pool():
# Connect to the MySQL database (Make sure to update the credentials)
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=4,  # Set the maximum number of connections based on your system's capabilities
        host='localhost',
        user='root',
        password='test_root',
        database='academicworld'
    )
    return connection_pool

def execute_sql_statement(connection_pool, statement):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    cursor.execute(statement)
    connection.commit()
    cursor.close()
    connection.close()
