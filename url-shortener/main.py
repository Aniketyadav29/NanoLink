from pathlib import Path
from secrets import token_urlsafe
import os
import sqlite3

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
DB_PATH = Path("/tmp/links.db") if os.getenv("VERCEL") else BASE_DIR.parent / "links.db"
INDEX_PATH = BASE_DIR / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="URL Shortener API",
    description="A high-performance URL shortening service developed by Aniket Yadav (BBD).",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def using_postgres() -> bool:
    return bool(DATABASE_URL)


def get_psycopg():
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError(
            "psycopg is required when DATABASE_URL or POSTGRES_URL is configured"
        ) from exc

    return psycopg


def get_postgres_connection():
    return get_psycopg().connect(DATABASE_URL)


def init_db():
    """Create the database table if it does not already exist."""
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS urls (
                        id SERIAL PRIMARY KEY,
                        original_url TEXT UNIQUE NOT NULL,
                        short_code TEXT UNIQUE NOT NULL
                    )
                """)
        return

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT UNIQUE NOT NULL,
            short_code TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()


class URLRequest(BaseModel):
    original_url: HttpUrl


@app.get("/", response_class=HTMLResponse)
def read_root():
    if not INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="Homepage template is missing")

    return HTMLResponse(INDEX_PATH.read_text(encoding="utf-8"))


@app.post("/shorten")
def shorten_url(url_request: URLRequest, request: Request):
    original_url = str(url_request.original_url)

    if using_postgres():
        psycopg = get_psycopg()

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                existing_url = cursor.execute(
                    "SELECT short_code FROM urls WHERE original_url = %s",
                    (original_url,),
                ).fetchone()

                if existing_url:
                    short_code = existing_url[0]
                    return {
                        "original_url": original_url,
                        "short_code": short_code,
                        "short_url": str(request.base_url) + short_code,
                    }

                for _ in range(5):
                    short_code = token_urlsafe(4)
                    try:
                        cursor.execute(
                            """
                            INSERT INTO urls (original_url, short_code)
                            VALUES (%s, %s)
                            ON CONFLICT (original_url) DO UPDATE
                            SET original_url = EXCLUDED.original_url
                            RETURNING short_code
                            """,
                            (original_url, short_code),
                        )
                        saved_code = cursor.fetchone()[0]
                        conn.commit()
                        return {
                            "original_url": original_url,
                            "short_code": saved_code,
                            "short_url": str(request.base_url) + saved_code,
                        }
                    except psycopg.IntegrityError:
                        conn.rollback()
                        continue

        raise HTTPException(status_code=500, detail="Could not generate a unique short URL")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    existing_url = cursor.execute(
        "SELECT short_code FROM urls WHERE original_url = ?",
        (original_url,),
    ).fetchone()

    if existing_url:
        conn.close()
        short_code = existing_url["short_code"]
        return {
            "original_url": original_url,
            "short_code": short_code,
            "short_url": str(request.base_url) + short_code,
        }

    for _ in range(5):
        short_code = token_urlsafe(4)
        try:
            cursor.execute(
                "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
                (original_url, short_code),
            )
            conn.commit()
            conn.close()
            return {
                "original_url": original_url,
                "short_code": short_code,
                "short_url": str(request.base_url) + short_code,
            }
        except sqlite3.IntegrityError:
            continue

    conn.close()
    raise HTTPException(status_code=500, detail="Could not generate a unique short URL")


@app.get("/{short_code}")
def redirect_to_original_url(short_code: str):
    if using_postgres():
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                result = cursor.execute(
                    "SELECT original_url FROM urls WHERE short_code = %s",
                    (short_code,),
                ).fetchone()

        if result is None:
            raise HTTPException(status_code=404, detail="Short URL not found")

        return RedirectResponse(url=result[0])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    result = cursor.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,),
    ).fetchone()
    conn.close()

    if result is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=result[0])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
