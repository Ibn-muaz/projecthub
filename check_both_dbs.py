
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL')

def check_url(url, label):
    print(f"\nChecking {label}...")
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [t[0] for t in cur.fetchall()]
        print(f"Tables: {len(tables)}")
        
        if 'projects_projectmaterial' in tables:
            cur.execute("SELECT count(*) FROM projects_projectmaterial")
            count = cur.fetchone()[0]
            print(f"Projects count: {count}")
        else:
            print("projects_projectmaterial table NOT found")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

check_url(db_url, "Original URL")
clean_url = db_url.replace('Projecthub%20', 'Projecthub')
check_url(clean_url, "Cleaned URL")
