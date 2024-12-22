from sqlmodel import create_engine, Session, SQLModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Membuat engine
engine = create_engine(DATABASE_URL, echo=True)

# Fungsi untuk membuat tabel
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency untuk mendapatkan session
def get_session():
    with Session(engine) as session:
        yield session
