#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Try to load .env from the project root
    import dotenv
    from pathlib import Path
    
    BASE_DIR = Path(__file__).resolve().parent
    env_path = BASE_DIR / '.env'
    
    if env_path.exists():
        dotenv.load_dotenv(env_path)
    else:
        # Fallback to standard search if path is not found directly
        dotenv.load_dotenv()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
