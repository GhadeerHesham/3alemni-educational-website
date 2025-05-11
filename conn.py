import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('3alemni.db')  # Make sure the path is correct

# Create a cursor object to interact with the database
cur = conn.cursor()

# Example: fetch all centers
cur.execute("SELECT * FROM centers")
rows = cur.fetchall()

# Print the results
for row in rows:
    print(row)

# Always close the connection when done
conn.close()
