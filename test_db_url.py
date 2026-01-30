
import os
import django
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL')
# Try without the %20 at the end of the db name
clean_url = db_url.replace('Projecthub%20', 'Projecthub')

print(f"Original: {db_url}")
print(f"Cleaned:  {clean_url}")

try:
    conn = psycopg2.connect(clean_url)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM projects_department")
    count = cur.fetchone()[0]
    print(f"Cleaned URL Dept Count: {count}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error connecting to cleaned URL: {e}")
