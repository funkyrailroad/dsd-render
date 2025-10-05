import os

import dj_database_url

from .settings import *

# SECURITY
DEBUG = False

ALLOWED_HOSTS = [".onrender.com"]

# Use the Render Postgres database.
db_url = os.environ.get("DATABASE_URL")
DATABASES["default"] = dj_database_url.parse(db_url)
