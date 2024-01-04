import os
from sqlalchemy.orm import declarative_base

DATABASE_URI = os.getenv("DATABASE_URI")

Base = declarative_base()
