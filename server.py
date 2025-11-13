from __future__ import annotations

import json
import secrets
import sqlite3
import time
import hashlib
import hmac
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any, Dict
from urllib.parse import urlparse

DB_PATH = Path(__file__).resolve().parent / 'db' / 'ourworld.db'
PUBLIC_DIR = Path(__file__).resolve().parent / 'public'
SESSION_COOKIE = 'ourworld_session'
SESSIONS: Dict[str, Dict[str, Any]] = {}

PROTECTED_PATHS = {
    '/home.html',
    '/memories.html',
    '/blog.html',
    '/dates.html',
    '/special.html',
    '/notes.html',
    '/fun.html'
}


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                date TEXT NOT NULL,
                author TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS date_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bucket_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS countdowns (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                date TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS wheel_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                label TEXT NOT NULL,
                is_answer INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES quiz_questions(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS poll_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                votes INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS upcoming_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                label TEXT NOT NULL
            )
            """
        )
    seed_database(conn)
    return conn


def seed_database(conn: sqlite3.Connection) -> None:
    def table_empty(table: str) -> bool:
        row = conn.execute(f'SELECT COUNT(*) AS count FROM {table}').fetchone()
        return bool(row and row['count'] == 0)

    if table_empty('users'):
        salt = secrets.token_hex(16)
        password = 'starlight'
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 120_000)
        conn.execute(
            'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
            ('couple', digest.hex(), salt)
        )

    if table_empty('blog_posts'):
        posts = [
            ('The Day We Met', 'I still remember the way you smiled. It felt like the world paused just for us.', 'Feb 14, 2021', 'Him'),
            ('Our Rainy Adventure', 'Dancing in the rain and getting completely soaked was the best idea ever.', 'Jul 03, 2022', 'Her'),
            ('Weekend Getaway', 'We found our cozy cabin escape and made it our own little universe for a weekend.', 'Nov 19, 2023', 'Him')
        ]
        conn.executemany('INSERT INTO blog_posts (title, body, date, author) VALUES (?, ?, ?, ?)', posts)

    if table_empty('date_ideas'):
        ideas = [
            ('Sunset Picnic by the Lake', 'Planned'),
            ('Pottery Class Together', 'Completed'),
            ('DIY Pizza Night', 'Want to Try'),
            ('Stargazing Road Trip', 'Planned'),
            ('Bookstore Treasure Hunt', 'Completed')
        ]
        conn.executemany('INSERT INTO date_ideas (title, status) VALUES (?, ?)', ideas)

    if table_empty('bucket_items'):
        items = [
            ('Visit a foreign country together', 0),
            ('Adopt a tiny plant family', 1),
            ('Write and record a song', 0),
            ('Wake up for a 5am sunrise date', 0),
            ('Learn a new language phrase each week', 1)
        ]
        conn.executemany('INSERT INTO bucket_items (title, completed) VALUES (?, ?)', items)

    if table_empty('milestones'):
        milestones = [
            ('Feb 14, 2021', 'We met 💫', 'The start of everything amazing.'),
            ('Mar 01, 2021', 'First Official Date', 'Coffee, laughs, and sparks.'),
            ('Dec 25, 2021', 'First Holiday Together', 'Matching pajamas and cozy cuddles.'),
            ('Apr 12, 2023', 'Moved In Together', 'Our shared safe place was born.')
        ]
        conn.executemany('INSERT INTO milestones (date, title, description) VALUES (?, ?, ?)', milestones)

    if table_empty('countdowns'):
        countdowns = [
            ('anniversary', 'Next Anniversary', '2025-02-14T00:00:00'),
            ('herBirthday', 'Her Birthday', '2024-11-05T00:00:00'),
            ('hisBirthday', 'His Birthday', '2025-04-22T00:00:00')
        ]
        conn.executemany('INSERT INTO countdowns (id, title, date) VALUES (?, ?, ?)', countdowns)

    if table_empty('wheel_ideas'):
        ideas = [
            'Cook a new recipe together',
            'Watch the stars with a cozy blanket',
            'Karaoke night at home',
            'Write each other love letters',
            'Explore a new coffee shop',
            'Go for a midnight walk'
        ]
        conn.executemany('INSERT INTO wheel_ideas (idea) VALUES (?)', [(idea,) for idea in ideas])

    if table_empty('quiz_questions'):
        questions = [
            ('Where did we first meet?', [
                ('At a bookstore', 0),
                ('At a coffee shop', 1),
                ('At a concert', 0)
            ]),
            ('Our go-to comfort movie is…', [
                ('The Notebook', 0),
                ('Your Name', 0),
                ('La La Land', 1)
            ]),
            ('Who said “I love you” first?', [
                ('Him', 1),
                ('Her', 0),
                ('We said it at the same time', 0)
            ])
        ]
        for question, options in questions:
            cursor = conn.execute('INSERT INTO quiz_questions (question) VALUES (?)', (question,))
            q_id = cursor.lastrowid
            for label, is_answer in options:
                conn.execute(
                    'INSERT INTO quiz_options (question_id, label, is_answer) VALUES (?, ?, ?)',
                    (q_id, label, is_answer)
                )

    if table_empty('poll_options'):
        options = [
            ('Romantic picnic', 0),
            ('Art museum date', 0),
            ('Weekend road trip', 0)
        ]
        conn.executemany('INSERT INTO poll_options (label, votes) VALUES (?, ?)', options)

    if table_empty('config'):
        conn.execute('INSERT INTO config (key, value) VALUES (?, ?)', ('first_met_date', '2021-02-14T00:00:00'))

    if table_empty('upcoming_events'):
        events = [
            ('2024-11-05', 'Her birthday breakfast in bed'),
            ('2024-12-12', 'Winter wonderland photo walk'),
            ('2025-02-14', 'Our next anniversary escape'),
            ('2025-04-22', 'His birthday adventure day')
        ]
        conn.executemany('INSERT INTO upcoming_events (date, label) VALUES (?, ?)', events)


def verify_password(conn: sqlite3.Connection, password: str) -> bool:
    row = conn.execute('SELECT password_hash, salt FROM users WHERE username = ?', ('couple',)).fetchone()
    if not row:
        return False
    salt = bytes.fromhex(row['salt'])
    expected = row['password_hash']
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 120_000).hex()
    return hmac.compare_digest(digest, expected)


def create_session() -> str:
    session_id = secrets.token_hex(32)
    SESSIONS[session_id] = {'created': time.time()}
    return session_id


def get_session(session_id: str | None) -> Dict[str, Any] | None:
    if not session_id:
        return None
    return SESSIONS.get(session_id)


def destroy_session(session_id: str | None) -> None:
    if session_id and session_id in SESSIONS:
        SESSIONS.pop(session_id, None)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class OurWorldHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    @property
    def db(self) -> sqlite3.Connection:
        if not hasattr(self.server, 'db_conn'):
            self.server.db_conn = ensure_database()
        return self.server.db_conn

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # Reduce console noise when running the server.
        return

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin', ''))
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith('/api/'):
            self.handle_api_get(path)
            return

        if path in PROTECTED_PATHS and not self.is_authenticated():
            self.send_response(HTTPStatus.FOUND)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return

        self.path = path
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith('/api/'):
            self.handle_api_post(path)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith('/api/'):
            self.handle_api_delete(path)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def handle_api_get(self, path: str) -> None:
        if path == '/api/session':
            self.send_json({'authenticated': self.is_authenticated()})
            return

        if not self.require_auth():
            return

        if path == '/api/home':
            config = self.db.execute('SELECT value FROM config WHERE key = ?', ('first_met_date',)).fetchone()
            events = [dict(row) for row in self.db.execute('SELECT date, label FROM upcoming_events ORDER BY date ASC')]
            self.send_json({
                'startDate': config['value'] if config else None,
                'upcomingEvents': events
            })
        elif path == '/api/blog':
            posts = [dict(row) for row in self.db.execute('SELECT title, body, date, author FROM blog_posts ORDER BY id DESC')]
            self.send_json({'posts': posts})
        elif path == '/api/dates':
            date_ideas = [dict(row) for row in self.db.execute('SELECT id, title, status FROM date_ideas ORDER BY id ASC')]
            bucket_items = [
                {'id': row['id'], 'title': row['title'], 'completed': bool(row['completed'])}
                for row in self.db.execute('SELECT id, title, completed FROM bucket_items ORDER BY id ASC')
            ]
            self.send_json({'dateIdeas': date_ideas, 'bucketItems': bucket_items})
        elif path == '/api/special':
            milestones = [dict(row) for row in self.db.execute('SELECT date, title, description FROM milestones ORDER BY id ASC')]
            countdowns = [dict(row) for row in self.db.execute('SELECT id, title, date FROM countdowns ORDER BY id ASC')]
            self.send_json({'milestones': milestones, 'countdowns': countdowns})
        elif path == '/api/notes':
            notes = [
                {'id': row['id'], 'author': row['author'], 'message': row['message'], 'date': row['created_at']}
                for row in self.db.execute('SELECT id, author, message, created_at FROM notes ORDER BY id DESC')
            ]
            self.send_json({'notes': notes})
        elif path == '/api/fun':
            wheel = [dict(row) for row in self.db.execute('SELECT id, idea FROM wheel_ideas ORDER BY id ASC')]
            quiz_data = []
            for question in self.db.execute('SELECT id, question FROM quiz_questions ORDER BY id ASC'):
                options = [
                    {'id': option['id'], 'label': option['label']}
                    for option in self.db.execute('SELECT id, label FROM quiz_options WHERE question_id = ? ORDER BY id ASC', (question['id'],))
                ]
                answer = self.db.execute(
                    'SELECT id FROM quiz_options WHERE question_id = ? AND is_answer = 1 LIMIT 1',
                    (question['id'],)
                ).fetchone()
                quiz_data.append({
                    'id': question['id'],
                    'question': question['question'],
                    'options': options,
                    'answerId': answer['id'] if answer else None
                })
            poll = [dict(row) for row in self.db.execute('SELECT id, label, votes FROM poll_options ORDER BY id ASC')]
            self.send_json({'wheelIdeas': wheel, 'quizQuestions': quiz_data, 'pollOptions': poll})
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def handle_api_post(self, path: str) -> None:
        if path == '/api/login':
            data = self.read_json()
            password = (data or {}).get('password', '')
            if not password:
                self.send_json({'message': 'Password is required.'}, status=HTTPStatus.BAD_REQUEST)
                return
            if verify_password(self.db, password):
                session_id = create_session()
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Set-Cookie', f'{SESSION_COOKIE}={session_id}; HttpOnly; Path=/; SameSite=Lax')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
            else:
                self.send_json({'message': 'Incorrect password.'}, status=HTTPStatus.UNAUTHORIZED)
            return

        if not self.require_auth():
            return

        if path == '/api/logout':
            session_id = self.get_session_id()
            destroy_session(session_id)
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Set-Cookie', f'{SESSION_COOKIE}=; HttpOnly; Path=/; Max-Age=0; SameSite=Lax')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
        elif path.startswith('/api/bucket/') and path.endswith('/toggle'):
            try:
                item_id = int(path.split('/')[3])
            except (IndexError, ValueError):
                self.send_json({'message': 'Invalid bucket item.'}, status=HTTPStatus.BAD_REQUEST)
                return
            row = self.db.execute('SELECT completed FROM bucket_items WHERE id = ?', (item_id,)).fetchone()
            if not row:
                self.send_json({'message': 'Bucket item not found.'}, status=HTTPStatus.NOT_FOUND)
                return
            new_value = 0 if row['completed'] else 1
            with self.db:
                self.db.execute('UPDATE bucket_items SET completed = ? WHERE id = ?', (new_value, item_id))
            self.send_json({'id': item_id, 'completed': bool(new_value)})
        elif path == '/api/notes':
            data = self.read_json() or {}
            message = (data.get('message') or '').strip()
            author = (data.get('author') or 'Someone in love').strip()
            if not message:
                self.send_json({'message': 'Note message is required.'}, status=HTTPStatus.BAD_REQUEST)
                return
            created_at = time.strftime('%b %d, %Y')
            with self.db:
                cursor = self.db.execute(
                    'INSERT INTO notes (author, message, created_at) VALUES (?, ?, ?)',
                    (author, message, created_at)
                )
            note_id = cursor.lastrowid
            self.send_json({'id': note_id, 'author': author, 'message': message, 'date': created_at})
        elif path == '/api/poll/vote':
            data = self.read_json() or {}
            option_id = data.get('optionId')
            if not isinstance(option_id, int):
                self.send_json({'message': 'Option id is required.'}, status=HTTPStatus.BAD_REQUEST)
                return
            row = self.db.execute('SELECT votes FROM poll_options WHERE id = ?', (option_id,)).fetchone()
            if not row:
                self.send_json({'message': 'Poll option not found.'}, status=HTTPStatus.NOT_FOUND)
                return
            with self.db:
                self.db.execute('UPDATE poll_options SET votes = votes + 1 WHERE id = ?', (option_id,))
            options = [dict(option) for option in self.db.execute('SELECT id, label, votes FROM poll_options ORDER BY id ASC')]
            self.send_json({'options': options})
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def handle_api_delete(self, path: str) -> None:
        if not self.require_auth():
            return

        if path.startswith('/api/notes/'):
            try:
                note_id = int(path.split('/')[3])
            except (IndexError, ValueError):
                self.send_json({'message': 'Invalid note.'}, status=HTTPStatus.BAD_REQUEST)
                return
            with self.db:
                deleted = self.db.execute('DELETE FROM notes WHERE id = ?', (note_id,)).rowcount
            if deleted:
                self.send_json({'success': True})
            else:
                self.send_json({'message': 'Note not found.'}, status=HTTPStatus.NOT_FOUND)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def is_authenticated(self) -> bool:
        session_id = self.get_session_id()
        return bool(get_session(session_id))

    def get_session_id(self) -> str | None:
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None
        cookies = SimpleCookie()
        cookies.load(cookie_header)
        morsel = cookies.get(SESSION_COOKIE)
        if morsel:
            return morsel.value
        return None

    def require_auth(self) -> bool:
        if not self.is_authenticated():
            self.send_json({'message': 'Authentication required.'}, status=HTTPStatus.UNAUTHORIZED)
            return False
        return True

    def read_json(self) -> Dict[str, Any] | None:
        length = int(self.headers.get('Content-Length', 0))
        if length <= 0:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode('utf-8'))
        except json.JSONDecodeError:
            return None

    def send_json(self, payload: Dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server(host: str = '0.0.0.0', port: int = 8000) -> None:
    db_conn = ensure_database()
    server = ThreadedHTTPServer((host, port), OurWorldHandler)
    server.db_conn = db_conn
    print(f'Server running on http://{host}:{port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
    finally:
        server.server_close()
        try:
            server.db_conn.close()
        except Exception:  # pragma: no cover - defensive cleanup
            pass


if __name__ == '__main__':
    run_server()
