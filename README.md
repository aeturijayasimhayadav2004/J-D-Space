# Our World Private Couple App

This project is a fully private couple space featuring a password-protected login, curated pages, and an interactive fun zone. A lightweight Python backend powers authentication plus persistence for notes, bucket list progress, polls, and other shared memories using SQLite.

## Getting started

1. **Install dependencies** – the app uses only the Python standard library, so no extra packages are required.
2. **Run the server**
   ```bash
   python server.py
   ```
3. Open your browser to [http://localhost:8000](http://localhost:8000) and log in with the shared password `starlight`.
   - If you see a “Unable to reach the server” message on the login page, confirm that the command above is still running and that you are visiting the same machine/port where it is serving.

## Sharing the site securely

Because the experience depends on the Python backend and SQLite database, the pages will only work when the server is running. You have two common options to make it reachable beyond your computer:

### 1. Temporary private links

Use a tunneling tool (for example [ngrok](https://ngrok.com/) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)) while the server is running locally. These tools generate a unique HTTPS URL that you can share with your partner and revoke at any time.

1. Start the backend locally: `python server.py`.
2. Run your tunnel client and point it at `http://localhost:8000`.
3. Share the generated HTTPS link. Anyone visiting it will hit your local server, so stop the tunnel or the Python process to close access.

### 2. Always-on hosting (recommended)

Deploy the repository to a platform that can run a persistent Python service, such as Render, Railway, Fly.io, or a small VPS.

For Render (example):

1. Push your latest changes to GitHub.
2. Create a new **Web Service** on Render and connect your repository.
3. Choose the **Python** environment, set the build command to `pip install -r requirements.txt || true` (no external deps, so installs succeed even though the file is empty), and the start command to `python server.py`.
4. Render provisions a public HTTPS URL. Log in with `starlight`, and share that link exclusively with the people you trust.

> If you prefer another host, the only requirement is that it runs `python server.py` and exposes port 8000 (or any port you configure in `run_server`).

### Customizing the password

You can change the shared secret by editing `password = 'starlight'` in `server.py` inside the `seed_database` function and deleting `db/ourworld.db` so the new value seeds on the next startup. Everyone must then use the new password to log in.

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
