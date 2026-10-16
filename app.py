from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "lab.db"
app = FastAPI(title="Test Login (Vulnerable)")

def connect():
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  return conn

def init_db():
  with connect() as conn:
    conn.execute(
      """
      CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        role TEXT
      )
      """
    )
    conn.execute("DELETE FROM users")

    conn.executemany(
      """
      INSERT INTO users (username, password, role)
      VALUES (?, ?, ?)
      """,
      [
        ("aman", "aman-demo", "user"),
        ("admin", "admin-demo", "admin")
      ],
    )
    
init_db()

class LoginRequest(BaseModel):
  username: str
  password: str

@app.post("/login")
def login(body: LoginRequest):
  # VULNERABLE CODE - User Input is directly inserted into the SQL query
  query = (
    "SELECT id, username, role FROM users "
    f"WHERE username = '{body.username}' "
    f"AND password = '{body.password}' "
  )

  with connect() as conn:
    row = conn.execute(query).fetchone()

  if row is None:
    raise HTTPException(status_code=401, detail="Invalid credentials")

  return{
    "user_id": row["id"],
    "username": row["username"],
    "role": row["role"],
  }
