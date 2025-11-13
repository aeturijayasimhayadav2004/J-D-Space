# Our World Private Couple App

This project is a fully private couple space featuring a password-protected login, curated pages, and an interactive fun zone. A lightweight Python backend powers authentication plus persistence for notes, bucket list progress, polls, and other shared memories using SQLite.

## Getting started

1. **Install dependencies** – the app uses only the Python standard library, so no extra packages are required.
2. **Run the server**
   ```bash
   python server.py
   ```
3. Open your browser to [http://localhost:8000](http://localhost:8000) and log in with the shared password `starlight`.

## Features

- Secure login backed by salted hashing and HTTP-only session cookies.
- Home, memories, blog, date planner, special days, notes, and fun zone pages served from the backend.
- SQLite database seeded with starter content for posts, events, countdowns, and games.
- Persistent notes, poll tallies, and bucket list completion that survive refreshes and restarts.

## Project structure

```
public/          # Front-end assets served by the backend
  assets/
  css/
  js/
  *.html
server.py        # Python HTTP server + API + SQLite migrations and seeding
db/              # Stores the SQLite database file (created on first run)
```

Enjoy your private shared universe!
