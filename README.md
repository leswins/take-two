# Take Two - Sports Commentary Bias Analyzer

A dashboard application that analyzes sports commentary transcripts to identify how commentators speak about specific players, detecting sentiment patterns, language bias, and descriptive tendencies.

## Overview

Sports commentary can contain subtle bias toward certain players. This tool uses NLP and AI to provide data-driven insights into:

- **Sentiment Analysis**: How positively or negatively commentators speak about each player
- **Language Patterns**: Most frequently used adjectives and phrases per player
- **Bias Detection**: Systematic patterns in how different players are described
- **Comparative Analysis**: Side-by-side comparison of commentary treatment

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for background tasks)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:5173 and will proxy API requests to the backend.

### Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE sports_commentary;
```

Update the `DATABASE_URL` in `backend/.env` with your credentials.

## Project Structure

```
take-two/
├── backend/
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── core/         # Config and database setup
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic (Phase 2)
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   └── types/        # TypeScript types
│   └── package.json
├── PLAN.md               # Project plan and requirements
└── README.md
```

## API Documentation

Once the backend is running, access the interactive API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Documentation

- [Project Plan & Requirements](./PLAN.md) - Detailed technical plan, architecture, and implementation phases

## Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, React Router, Recharts
- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **NLP/AI**: spaCy, HuggingFace Transformers (Phase 2)
- **Database**: PostgreSQL, Redis

## Project Status

**Current Phase**: Phase 2 - NLP Pipeline (Complete)

### Phase 1: Foundation ✅
- [x] Project structure setup
- [x] Database schema and models
- [x] FastAPI backend with transcript upload
- [x] React frontend with routing
- [x] Basic file upload UI

### Phase 2: NLP Pipeline ✅
- [x] Text preprocessing pipeline
- [x] Named Entity Recognition (spaCy) for player detection
- [x] Sentiment analysis (HuggingFace Transformers)
- [x] Adjective extraction and counting
- [x] Analysis orchestration service

See [PLAN.md](./PLAN.md) for the full implementation roadmap.

## License

MIT
