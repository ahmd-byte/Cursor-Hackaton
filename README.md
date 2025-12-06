# Financial AI App - Early Wage Access Backend

A comprehensive Python backend system for an early wage access app with AI-driven financial goal management using money jars/buckets.

## Features

### Core Features
- **Early Wage Access**: Daily wage calculation, advance requests, and automatic repayment
- **Money Jars (Buckets)**: Create, manage, and track financial goals with progress monitoring
- **AI Smart Allocation**: AI-powered recommendations for distributing funds across savings goals
- **Document Processing**: Extract financial data from PDFs, images, and emails

### AI Capabilities
- **Groq Integration**: Ultra-fast inference for real-time financial analysis
- **Gemini Integration**: Multimodal document understanding and vision capabilities
- **LangChain Orchestration**: Agent-based workflows for complex financial operations
- **MCP (Model Context Protocol)**: Standardized data extraction from various sources

## Tech Stack

- **Framework**: FastAPI with async support (Python 3.10+)
- **Database**: TiDB Serverless (MySQL-compatible) with SQLAlchemy async
- **AI/ML**: Groq + Gemini + LangChain
- **Authentication**: JWT-based with bcrypt password hashing
- **Migrations**: Alembic

## Project Structure

```
project-root/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Configuration management
│   ├── api/v1/              # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── buckets.py       # Money jars
│   │   ├── wages.py         # Early wage access
│   │   ├── ai_agent.py      # AI features
│   │   └── documents.py     # Document processing
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── ai/                  # AI integrations
│   │   ├── groq_client.py   # Groq API client
│   │   ├── gemini_client.py # Gemini API client
│   │   └── allocation_model.py
│   ├── mcp/                 # MCP integration
│   └── database/            # Database configuration
├── tests/                   # Test suite
├── alembic/                 # Database migrations
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.10+
- TiDB Serverless account or MySQL database
- Groq API key
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd financial-ai-app
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn app.main:app --reload
```

### Environment Variables

Key environment variables to configure:

```env
# Database
TIDB_HOST=your-tidb-host
TIDB_USER=your-username
TIDB_PASSWORD=your-password
TIDB_DATABASE=finapp

# AI APIs
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key

# Security
JWT_SECRET_KEY=your-jwt-secret-min-32-chars
SECRET_KEY=your-app-secret-key
```

## API Documentation

Once running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Main Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

#### Money Jars (Buckets)
- `POST /api/v1/buckets` - Create bucket
- `GET /api/v1/buckets` - List buckets
- `POST /api/v1/buckets/{id}/deposit` - Deposit funds
- `POST /api/v1/buckets/transfer` - Transfer between buckets

#### Early Wage Access
- `GET /api/v1/wages/available` - Check available balance
- `POST /api/v1/wages/advance` - Request advance
- `GET /api/v1/wages/history` - Transaction history

#### AI Features
- `POST /api/v1/ai/analyze` - Financial health analysis
- `POST /api/v1/ai/recommend` - Get allocation recommendations
- `POST /api/v1/ai/auto-allocate` - Execute AI allocation
- `POST /api/v1/ai/chat` - Chat with AI assistant

#### Document Processing
- `POST /api/v1/documents/upload` - Upload document
- `POST /api/v1/documents/extract` - Extract data
- `POST /api/v1/documents/email/sync` - Sync financial emails

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api/test_auth.py
```

## Development

### Adding New Migrations

```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Code Style

The project follows PEP 8 guidelines. Format code with:

```bash
black app/
isort app/
```

## Architecture

### Database Models

- **User**: Authentication and profile data
- **Bucket**: Financial goal containers
- **Transaction**: All financial movements
- **FinancialData**: Extracted financial information

### Service Layer

Business logic is separated into services:
- `BucketService`: Money jar operations
- `WageService`: Wage calculations and advances
- `AIAgentService`: AI orchestration
- `DocumentProcessor`: Document extraction

### AI Integration

The app uses multiple AI providers:
1. **Groq**: Fast text-based analysis and recommendations
2. **Gemini**: Document/image understanding
3. **LangChain**: Agent orchestration and workflows

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a Pull Request
