from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sqlite3

DB_FILE = "tasks.db"

def get_db_connection():
  """Helper function to connect to SQLite and return rows as dictionaries."""
  conn = sqlite3.connect(DB_FILE)
  conn.row_factory = sqlite3.Row
  return conn

def init_db():
  """Stage 0: Create tasks table if missing, and seed 3 examples only if empty."""
  conn = get_db_connection()
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL CHECK (done IN (0, 1))
        )
    """)

  cursor.execute("SELECT COUNT(*) FROM tasks")
  count = cursor.fetchone()[0]

  if count == 0:
    initial_tasks = [
        ("Learn FastAPI", 0),
        ("Build CRUD API", 0),
        ("Test the API", 0),
    ]
    cursor.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks
    )
    conn.commit()

  conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
  init_db()
  yield

app = FastAPI(title="Task API", version="2.0", lifespan=lifespan)

@app.get("/", description="Get API information and available endpoints.")
def root():
    return {
        "name": "Task API",
        "version": "2.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", description="Check whether the API is running.")
def health():
    return {"status": "ok"}

@app.get("/tasks", description="Get all tasks.")
def get_tasks():
    """Stage 1: Read all tasks from SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return [dict(task) for task in tasks]

@app.get("/tasks/{task_id}", description="Get a single task by ID.")
def get_task(task_id: int):
    """Stage 1: Read a single task by ID from SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()

    if task is None:
        return JSONResponse(
            status_code=404, content={"error": f"Task {task_id} not found"}
        )

    return dict(task)

@app.post("/tasks", status_code=201, description="Create a new task.")
def create_task(task_data: dict):
    """Stage 2: Create a new task in the SQLite database with validation."""
    title = task_data.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert task into SQLite database (done defaults to 0 / False)
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)", (title.strip(), 0)
    )
    conn.commit()

    new_id = cursor.lastrowid

    # Fetch the newly created record to return it
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    new_task = cursor.fetchone()
    conn.close()

    return dict(new_task)

@app.put("/tasks/{task_id}", description="Update a task by ID.")
def update_task(task_id: int, task_data: dict):
    task = next((task for task in tasks if task["id"] == task_id), None)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    if not task_data:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )

    if "title" in task_data:
        title = task_data["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"}
            )

        task["title"] = title.strip()

    if "done" in task_data:
        done = task_data["done"]

        if not isinstance(done, bool):
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be a boolean"}
            )

        task["done"] = done

    if "title" not in task_data and "done" not in task_data:
        return JSONResponse(
            status_code=400,
            content={"error": "At least one of title or done is required"}
        )

    return task

@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task by ID.")
def delete_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"}
        )

    tasks.remove(task)