import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'b2da1.settings')
django.setup()

def fix_schema():
    print("Attempting to fix DB schema for 'sessoes' table...")
    with connection.cursor() as cursor:
        try:
            # Check current type (optional, but good for verify)
            # We just force the alter.
            # We use USING to handle the conversion from TIME to TIMESTAMP
            # We add the current date to the existing time to make a valid timestamp
            
            print("Altering 'inicio' column...")
            cursor.execute("""
                ALTER TABLE sessoes 
                ALTER COLUMN inicio TYPE TIMESTAMP WITHOUT TIME ZONE 
                USING (CURRENT_DATE + inicio);
            """)
            
            print("Altering 'fim' column...")
            cursor.execute("""
                ALTER TABLE sessoes 
                ALTER COLUMN fim TYPE TIMESTAMP WITHOUT TIME ZONE 
                USING (CURRENT_DATE + fim);
            """)
            
            print("Schema fix applied successfully.")
        except Exception as e:
            print(f"Error applying fix: {e}")

if __name__ == "__main__":
    fix_schema()
