from django.core.management.base import BaseCommand
from django.db import connections
import os

class Command(BaseCommand):
    help = 'Rebuilds the entire database structure and data by executing SQL scripts in the defined order.'

    def handle(self, *args, **options):
        # Order of execution is critical
        scripts = [
            'create.sql',          # 1. Structure (Tables)
            'funcoes.sql',         # 2. Functions (Logic base)
            'procedimentos.sql',   # 3. Stored Procedures
            'vistas.sql',          # 4. Views
            'triggers.sql',        # 5. Triggers
            'exportações.sql',     # 6. Export Functions
            'indices.sql',         # 7. Optimizations
            'users_roles.sql',     # 8. Permissions/Roles
            'fill.sql'             # 9. Mock Data
        ]

        # Use the 'admin' connection to ensure we have permissions to Drop/Create tables and roles
        # Make sure 'admin' is defined in your DATABASES setting
        db_conn = 'admin' if 'admin' in connections else 'default'
        
        self.stdout.write(f"Using database connection: {db_conn}")
        
        base_dir = os.path.join(os.getcwd(), 'Scripts')
        
        try:
            with connections[db_conn].cursor() as cursor:
                for script_name in scripts:
                    file_path = os.path.join(base_dir, script_name)
                    
                    if not os.path.exists(file_path):
                        self.stdout.write(self.style.WARNING(f"Skipping missing file: {script_name}"))
                        continue

                    self.stdout.write(f"Executing {script_name}...")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            sql_content = f.read()
                            # Execute the script
                            cursor.execute(sql_content)
                            
                        self.stdout.write(self.style.SUCCESS(f"OK: {script_name}"))
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"FAILED: {script_name}"))
                        self.stdout.write(self.style.ERROR(f"Error details: {e}"))
                        # Stop execution on error to prevent cascading failures
                        return

            self.stdout.write(self.style.SUCCESS("\nDatabase rebuild completed successfully!"))
            
        except Exception as conn_err:
             self.stdout.write(self.style.ERROR(f"Database connection blocked or failed: {conn_err}"))
