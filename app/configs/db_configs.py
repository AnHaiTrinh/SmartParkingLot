import os
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_URI = f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_DATABASE")}'
print(DATABASE_URI)
Base = declarative_base()
