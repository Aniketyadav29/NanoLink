# NanoLink - URL Shortener

https://drive.google.com/file/d/1Xyn-TlS9jdxTj25TvEZmLdmi5C8sx6Ad/view?usp=drivesdk

NanoLink is a FastAPI URL shortener with a simple web interface. It lets users paste a long URL, generate a short link, copy it, and redirect back to the original URL from the generated short code.

The app uses SQLite for local development and supports Postgres in production through `DATABASE_URL` or `POSTGRES_URL`, which makes it suitable for Vercel deployment.

[![Open NanoLink](https://img.shields.io/badge/Open%20NanoLink-Visit%20Website-f97316?style=for-the-badge&logo=vercel&logoColor=white)](https://nano-link-dun.vercel.app/)

## Features

- Shorten long URLs from the browser
- Reuse the same short code for an already saved original URL
- Redirect short links to the original URL
- Responsive frontend with static CSS and JavaScript
- SQLite support for local development
- Postgres support for Vercel or other production hosting

## Project Structure

```text
.
├── links.db
├── requirements.txt
├── vercel.json
└── url-shortener/
    ├── main.py
    ├── static/
    │   ├── css/
    │   │   └── style.css
    │   └── js/
    │       └── app.js
    └── templates/
        └── index.html
```

## Requirements

- Python 3.10 or newer
- pip
- Git
- A Vercel account for deployment
- A Postgres database for persistent production storage

## Local Setup

Clone the repository:

```bash
git clone https://github.com/Aniketyadav29/NanoLink.git
cd NanoLink
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app locally:

```bash
cd url-shortener
uvicorn main:app --reload
```

Or run this from the project root:

```bash
python url-shortener/main.py
```

Open the app:

```text
http://127.0.0.1:8000
```

Local development uses `links.db` automatically.

## Environment Variables

For local SQLite usage, no environment variable is required.

For production Postgres usage, set one of these variables:

```text
DATABASE_URL=postgresql://...
```

or:

```text
POSTGRES_URL=postgresql://...
```

The app checks `DATABASE_URL` first, then `POSTGRES_URL`.

## Vercel Deployment

### 1. Push Code To GitHub

Make sure the latest project code is pushed to GitHub:

```bash
git add .
git commit -m "Prepare NanoLink for deployment"
git push origin main
```

### 2. Import Project In Vercel

1. Go to Vercel.
2. Click `Add New Project`.
3. Import `Aniketyadav29/NanoLink`.
4. Keep the project connected to the `main` branch.

The repository already includes `vercel.json`, so Vercel knows to serve the FastAPI app from:

```text
url-shortener/main.py
```

### 3. Add A Production Database

Vercel serverless functions do not provide a normal persistent writable disk. SQLite files may work temporarily, but saved links can disappear between deployments or function restarts.

Use a hosted Postgres database for production. You can use Vercel Storage Postgres, Neon, Supabase, Railway, or any Postgres provider.

After creating the database, copy the connection string and add it to Vercel as an environment variable:

```text
DATABASE_URL
```

or:

```text
POSTGRES_URL
```

### 4. Configure Vercel Environment Variables

In Vercel:

1. Open your NanoLink project.
2. Go to `Settings`.
3. Open `Environment Variables`.
4. Add `DATABASE_URL` or `POSTGRES_URL`.
5. Paste your Postgres connection string as the value.
6. Select Production, Preview, and Development if you want the same database available everywhere.
7. Save the variable.

### 5. Redeploy

After adding environment variables, redeploy the project:

1. Open the `Deployments` tab.
2. Select the latest deployment.
3. Click `Redeploy`.

The app will create the required `urls` table automatically when it starts.

## Database Table

The app creates this table automatically:

```sql
CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    original_url TEXT UNIQUE NOT NULL,
    short_code TEXT UNIQUE NOT NULL
);
```

For local SQLite development, the same table is created with SQLite-compatible syntax.

## API Endpoints

### Home Page

```http
GET /
```

Returns the web interface.

### Shorten URL

```http
POST /shorten
```

Request body:

```json
{
  "original_url": "https://example.com/very/long/url"
}
```

Response:

```json
{
  "original_url": "https://example.com/very/long/url",
  "short_code": "abc123",
  "short_url": "https://your-domain.vercel.app/abc123"
}
```

### Redirect

```http
GET /{short_code}
```

Redirects to the original saved URL.

## Troubleshooting

### Short links do not persist on Vercel

Make sure a Postgres connection string is set in Vercel as `DATABASE_URL` or `POSTGRES_URL`. SQLite is not reliable for persistent storage on Vercel serverless deployments.

### Deployment succeeds but shortening fails

Check the Vercel function logs. Common causes are:

- Missing `DATABASE_URL` or `POSTGRES_URL`
- Invalid Postgres connection string
- Database provider blocking external connections
- Required dependency installation failed

### Static files do not load

Confirm `vercel.json` is present at the project root and includes the `/static/(.*)` route.

### Local server does not start

Check that dependencies are installed:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python url-shortener/main.py
```

## Notes For Production

- Do not rely on `links.db` for Vercel production storage.
- Keep database credentials in Vercel environment variables, not in source code.
- Do not commit real database files or secrets.
- Use a custom domain in Vercel if you want cleaner short URLs.

## Author

Built by Aniket Yadav.
