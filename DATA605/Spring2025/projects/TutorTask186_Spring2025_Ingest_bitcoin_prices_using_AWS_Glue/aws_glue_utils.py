import sqlite3
import os

def init_filebrowser_db(db_path="docker_data605_style/anaconda_projects/db/project_filebrowser.db"):
    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Create the database and a basic table
    conn = sqlite3.connect(db_path)
    conn.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL
        );
    \"\"\")
    conn.commit()
    conn.close()
