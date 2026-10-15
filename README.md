# Task API (SQLite Backend) - BE-02

Part 2 of the FlyRank Backend AI Engineering track. Upgrading the in-memory CRUD API to use a persistent SQLite database.

## Stage 4: Explored SQLite

The database was interacted with directly via DB Browser for SQLite to verify that the FastAPI application and the SQLite database share a single source of truth (`tasks.db`) with zero server restarts.

### Example Query

**Mark every task completed:**

```sql
UPDATE tasks SET done = 1;
```

**Response:**

```text
Execution finished without errors.
Result: query executed successfully. Took 6ms, 5 rows affected
At line 1:
UPDATE tasks SET done = 1;
```

- **Result:** Executed successfully and returned `query executed successfully. Took 6ms, 5 rows affected`, marking all tasks as completed (`done = 1`).
- **Note:** Clicking the **"Write Changes"** button in DB Browser was required to flush the pending transaction to the physical `tasks.db` disk file, allowing the running FastAPI server to reflect the updates instantly via `GET /tasks` with no server restarts.