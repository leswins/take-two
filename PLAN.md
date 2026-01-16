# Sports Commentary Sentiment Analysis Dashboard

## Project Overview

A web-based dashboard that analyzes sports commentary transcripts to identify how commentators speak about specific players. The system leverages natural language processing (NLP) and AI to detect sentiment, track adjective usage patterns, and visualize potential commentator bias.

---

## Problem Statement

Sports commentary can contain subtle (or overt) bias toward certain players. This bias may manifest through:
- Tone and sentiment when discussing player actions
- Choice of adjectives and descriptive language
- Frequency and context of player mentions
- Attribution of success vs. failure

This tool provides data-driven insights into these patterns, enabling broadcasters, analysts, and fans to identify and understand commentator tendencies.

---

## Core Features

### 1. Transcript Ingestion
- **File Upload**: Support for common transcript formats (TXT, SRT, VTT, JSON)
- **Text Paste**: Direct paste of commentary text
- **Batch Processing**: Upload multiple transcripts for aggregate analysis
- **Metadata Tagging**: Associate transcripts with game, date, commentator(s), teams

### 2. Player Identification (Named Entity Recognition)
- Automatic detection of player names in transcripts
- Handling of nicknames, abbreviations, and informal references
- Player disambiguation (e.g., "Smith" when multiple Smiths exist)
- Manual player roster import for improved accuracy
- Player-team association tracking

### 3. Sentiment Analysis
- **Per-Player Sentiment Scoring**: Positive/negative/neutral classification
- **Contextual Sentiment**: Sentiment specific to game situations (goals, mistakes, etc.)
- **Comparative Sentiment**: Side-by-side sentiment comparison between players
- **Temporal Sentiment**: How sentiment changes throughout a game/season
- **Confidence Scores**: Reliability indicator for each analysis

### 4. Language Pattern Analysis
- **Adjective Frequency**: Most common adjectives used per player
- **Word Clouds**: Visual representation of language patterns
- **Phrase Detection**: Common phrases associated with each player
- **Language Tone**: Formal vs. casual, enthusiastic vs. neutral
- **Superlative Tracking**: "Best," "worst," "greatest" attribution patterns

### 5. Bias Detection & Metrics
- **Bias Score**: Aggregate measure of commentator tendency toward players
- **Comparative Analysis**: Same play described differently for different players
- **Statistical Significance**: Confidence levels for detected patterns
- **Historical Trends**: Bias patterns over time

### 6. Dashboard & Visualization
- **Player Cards**: Summary view of analysis for each player
- **Sentiment Timeline**: Graph of sentiment over game/season
- **Comparison Charts**: Multi-player sentiment comparison
- **Word Frequency Charts**: Bar charts of adjective usage
- **Heat Maps**: Sentiment intensity visualization
- **Export Options**: PDF reports, CSV data export

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│  │ Upload   │  │ Dashboard│  │ Player   │  │ Reports/Export   ││
│  │ Interface│  │ Views    │  │ Profiles │  │                  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend API (Python/FastAPI)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│  │ Transcript│  │ Analysis │  │ Player   │  │ Report           ││
│  │ Service  │  │ Service  │  │ Service  │  │ Generator        ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NLP/AI Processing Layer                    │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐ │
│  │ Named Entity │  │ Sentiment     │  │ Language Pattern     │ │
│  │ Recognition  │  │ Analysis      │  │ Analysis             │ │
│  │ (spaCy)      │  │ (Transformers)│  │ (Custom + spaCy)     │ │
│  └──────────────┘  └───────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Storage                             │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐│
│  │ PostgreSQL           │  │ Redis (Caching)                  ││
│  │ - Transcripts        │  │ - Analysis results               ││
│  │ - Players            │  │ - Session data                   ││
│  │ - Analysis Results   │  │                                  ││
│  └──────────────────────┘  └──────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | React 18+ with TypeScript | Type safety, component reusability |
| State Management | Zustand or Redux Toolkit | Lightweight, predictable state |
| UI Components | Tailwind CSS + shadcn/ui | Rapid development, consistent design |
| Charts | Recharts or Chart.js | Rich visualization options |
| Word Clouds | react-wordcloud | Player language visualization |

#### Backend
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | FastAPI (Python) | Async support, auto-documentation, Python ML ecosystem |
| Task Queue | Celery + Redis | Background processing for long analyses |
| Database | PostgreSQL | Relational data, JSON support for flexible schemas |
| Cache | Redis | Fast caching of analysis results |
| File Storage | Local/S3 | Transcript file storage |

#### NLP/AI
| Component | Technology | Rationale |
|-----------|------------|-----------|
| NER | spaCy | Fast, accurate entity recognition |
| Sentiment | HuggingFace Transformers (BERT/RoBERTa) | State-of-the-art sentiment analysis |
| Text Processing | NLTK + spaCy | Tokenization, POS tagging, lemmatization |
| Custom Models | Fine-tuned models (optional) | Sports-specific language understanding |

---

## Data Models

### Transcript
```python
{
    "id": "uuid",
    "filename": "string",
    "content": "string",
    "game_date": "date",
    "sport": "string",
    "teams": ["team_a", "team_b"],
    "commentators": ["name1", "name2"],
    "source": "string",
    "uploaded_at": "timestamp",
    "processed": "boolean"
}
```

### Player
```python
{
    "id": "uuid",
    "name": "string",
    "aliases": ["nickname1", "nickname2"],
    "team": "string",
    "sport": "string",
    "position": "string",
    "created_at": "timestamp"
}
```

### AnalysisResult
```python
{
    "id": "uuid",
    "transcript_id": "uuid",
    "player_id": "uuid",
    "sentiment_score": "float (-1 to 1)",
    "sentiment_label": "positive|negative|neutral",
    "confidence": "float (0 to 1)",
    "mention_count": "integer",
    "adjectives": [
        {"word": "string", "count": "integer", "sentiment": "float"}
    ],
    "phrases": [
        {"phrase": "string", "count": "integer", "context": "string"}
    ],
    "excerpts": [
        {"text": "string", "sentiment": "float", "timestamp": "string"}
    ],
    "analyzed_at": "timestamp"
}
```

---

## API Endpoints

### Transcripts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/transcripts/upload` | Upload new transcript |
| GET | `/api/transcripts` | List all transcripts |
| GET | `/api/transcripts/{id}` | Get transcript details |
| DELETE | `/api/transcripts/{id}` | Delete transcript |
| POST | `/api/transcripts/{id}/analyze` | Trigger analysis |

### Players
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/players` | List all detected players |
| GET | `/api/players/{id}` | Get player details |
| PUT | `/api/players/{id}` | Update player info/aliases |
| POST | `/api/players/import` | Import player roster |

### Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analysis/player/{id}` | Get analysis for player |
| GET | `/api/analysis/transcript/{id}` | Get all analysis for transcript |
| GET | `/api/analysis/compare` | Compare multiple players |
| GET | `/api/analysis/trends/{player_id}` | Get historical trends |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/generate` | Generate PDF report |
| GET | `/api/reports/export/csv` | Export data as CSV |

---

## Implementation Phases

### Phase 1: Foundation ✅
- [x] Project setup (monorepo structure, CI/CD)
- [x] Database schema and migrations
- [x] Basic FastAPI backend with transcript upload
- [x] React frontend scaffolding with routing
- [x] Basic file upload UI

### Phase 2: NLP Pipeline ✅
- [x] Text preprocessing pipeline
- [x] Named Entity Recognition for player detection
- [x] Basic sentiment analysis integration
- [x] Adjective extraction and counting
- [x] Analysis results storage

### Phase 3: Dashboard MVP ✅
- [x] Transcript list view
- [x] Player list with basic stats
- [x] Single player detail view
- [x] Basic sentiment visualization (bar chart)
- [x] Word frequency display

### Phase 4: Advanced Analysis
- [ ] Contextual sentiment (per-mention analysis)
- [ ] Phrase detection and tracking
- [ ] Comparative player analysis
- [ ] Bias scoring algorithm
- [ ] Confidence scoring

### Phase 5: Enhanced Visualization
- [ ] Interactive sentiment timeline
- [ ] Word clouds per player
- [ ] Heat maps for sentiment intensity
- [ ] Multi-player comparison charts
- [ ] Commentator-specific views

### Phase 6: Polish & Export
- [ ] PDF report generation
- [ ] CSV data export
- [ ] Performance optimization
- [ ] Batch processing improvements
- [ ] User preferences and settings

---

## Non-Functional Requirements

### Performance
- Transcript analysis: < 30 seconds for 10,000 words
- Dashboard load time: < 2 seconds
- Support for transcripts up to 100,000 words
- Concurrent analysis of multiple transcripts

### Scalability
- Handle 100+ transcripts per user
- Support 1,000+ unique players across all transcripts
- Efficient storage and retrieval of analysis results

### Usability
- Intuitive upload flow
- Clear visualization of complex data
- Mobile-responsive dashboard
- Accessible (WCAG 2.1 AA compliance)

### Security
- Secure file upload validation
- Input sanitization
- Rate limiting on API endpoints

---

## Success Metrics

1. **Accuracy**: Sentiment classification accuracy > 85% on test set
2. **Player Detection**: > 95% of player mentions correctly identified
3. **User Engagement**: Users can complete full analysis workflow in < 5 minutes
4. **Insight Quality**: Detected bias patterns validated by manual review

---

## Future Enhancements (Out of Scope for MVP)

- Real-time audio/video transcription integration
- Multi-language support
- Custom model fine-tuning interface
- Team collaboration features
- API access for third-party integrations
- Automated report scheduling
- Browser extension for live commentary analysis

---

## Glossary

| Term | Definition |
|------|------------|
| NER | Named Entity Recognition - identifying proper nouns like player names |
| Sentiment | The emotional tone (positive/negative/neutral) of text |
| Bias Score | Aggregate metric indicating systematic favoritism toward a player |
| Transcript | Text record of spoken commentary |
| Adjective Frequency | Count of descriptive words associated with each player |

---

## Getting Started

See [README.md](./README.md) for setup instructions once implementation begins.
