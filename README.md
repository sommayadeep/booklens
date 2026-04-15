# BookLens - Document Intelligence Platform

BookLens is a full-stack AI-powered web app for scraping books, generating insights, and running RAG-based question answering with source citations.

## Features

- Automated book scraping using Selenium (with requests + BeautifulSoup fallback)
- Django REST API for book listing, detail retrieval, recommendations, scraping, upload, and RAG Q&A
- AI insight generation:
  - Summary generation
  - Genre classification
  - Sentiment analysis
  - Embedding-based recommendations
- RAG pipeline with:
  - Smart overlapping chunking
  - Embedding generation (Sentence Transformers with deterministic fallback)
  - Similarity retrieval from ChromaDB (with DB fallback)
  - Contextual answer generation with source citations
- Caching for repeated insights and Q&A queries
- Modern Next.js + Tailwind glassmorphism frontend (light, neutral, warm tone)

## Tech Stack

- Backend: Django, Django REST Framework
- Database: MySQL (optional) / SQLite fallback
- Vector DB: ChromaDB
- Frontend: Next.js (React), Tailwind CSS
- AI Provider Options: OpenAI / LM Studio / local fallback
- Automation: Selenium

## Project Structure

- `backend/` - Django backend
- `frontend/` - Next.js frontend
- `samples/` - sample upload payload and question set
- `docs/screenshots/` - screenshot folder for submission assets

## Setup Instructions

## 1. Clone and prepare environment

```bash
git clone <your-repo-url>
cd BookLens
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Backend setup

```bash
cp backend/.env.example backend/.env
cd backend
python manage.py migrate
python manage.py runserver
```

Backend runs at: `http://127.0.0.1:8000`

### Optional MySQL config

In `backend/.env`, set:

```env
MYSQL_DATABASE=booklens
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

If MySQL values are empty, SQLite is used automatically.

## 3. Frontend setup

```bash
cd ../frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Frontend runs at: `http://localhost:3000`

Set backend URL in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api
```

## 4. AI/LLM configuration (Optional)

Set in `backend/.env`:

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
LLM_MODEL=gpt-4o-mini
```

### LM Studio (Local)

```env
LLM_PROVIDER=lmstudio
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=your-loaded-model
OPENAI_API_KEY=lm-studio
```

Without provider keys, BookLens still runs using local heuristic fallbacks.

## API Documentation

Base URL: `http://127.0.0.1:8000/api`

### GET APIs

1. `GET /books/`
- List all books (paginated)

2. `GET /books/{id}/`
- Get complete details for a specific book

3. `GET /books/{id}/recommendations/`
- Get embedding-based related books

4. `GET /books/stats/`
- Dashboard stats: total books, processed books, chunks, genres, Q&A sessions

5. `GET /rag/history/`
- Recent Q&A logs

### POST APIs

1. `POST /books/scrape/`
- Scrape and process books automatically

Request body:

```json
{
  "pages": 2,
  "max_books": 40
}
```

2. `POST /books/upload/`
- Bulk upload books and process AI insights

Request body example: see [`samples/upload_books.json`](samples/upload_books.json)

3. `POST /rag/ask/`
- Ask questions over all books or a single book

Request body:

```json
{
  "question": "What are the central themes of Dune?",
  "book_id": 1
}
```

## Frontend Pages

1. Dashboard (`/`)
- Hero, scrape CTA, stats cards, searchable + filterable book listing

2. Book Detail (`/books/[id]`)
- Book metadata, summary, genre classification, sentiment, and recommendations

3. Ask AI (`/ask`)
- Chat UI with citation badges and typing/loading indicator

4. Login (`/login`)
- Light glassmorphism authentication-style page

## Sample Questions and Answers

See: [`samples/questions.md`](samples/questions.md)

Example:

- Q: "Summarize Atomic Habits with sources."
- A: "Atomic Habits emphasizes identity-based habit change and small, repeated improvements [S1][S2]."

## Screenshots (Add Before Submission)

Add these files in `docs/screenshots/` and keep paths in README:

- `dashboard.png`
- `book-detail.png`
- `ask-ai.png`
- `login.png`

Example markdown:

```md
![Dashboard](docs/screenshots/dashboard.png)
![Book Detail](docs/screenshots/book-detail.png)
![Ask AI](docs/screenshots/ask-ai.png)
![Login](docs/screenshots/login.png)
```

## Notes on Optimization

- Caches summaries, genres, sentiment, recommendations, and RAG answers
- Uses overlapping chunk strategy (`CHUNK_SIZE` + `CHUNK_OVERLAP`)
- Uses batched embedding generation when indexing chunks
- ChromaDB persistence for fast similarity search

## Submission Checklist

- Code pushed to GitHub
- `README.md` includes setup + API docs + sample Q&A + screenshot links
- `requirements.txt` included
- Samples included in `samples/`
- Submit repository URL in form: https://forms.gle/Fby8pMSmBJqjuVf56
