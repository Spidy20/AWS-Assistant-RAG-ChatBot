import psycopg2

# Database connection parameters
host = '13.233.136.178'
dbname = 'postgres'
user = 'postgres'
password = 'spidy20'

try:
    # Establish a connection to the database
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=5432
    )

    # Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Execute a SQL query
    cursor.execute("SELECT version();")

    # Fetch result
    db_version = cursor.fetchone()
    print("PostgreSQL database version:", db_version)

    cursor.close()
    conn.close()

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)
