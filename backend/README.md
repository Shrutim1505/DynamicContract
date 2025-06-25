# DynamicContractOps Backend

A production-grade FastAPI backend for the Smart Legal Contract Collaboration Platform.

## Features

- **RESTful API** with comprehensive endpoints for contract management
- **Real-time collaboration** using WebSockets
- **AI-powered contract analysis** with OpenAI/Anthropic integration
- **Version control** for contracts with diff tracking
- **Comment system** with threading and position tracking
- **User management** with JWT authentication
- **Analytics dashboard** with comprehensive insights
- **Document analysis** for risk assessment and compliance checking
- **Scalable architecture** with async/await patterns

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM with async support
- **PostgreSQL** - Robust relational database
- **Redis** - Caching and session storage
- **Alembic** - Database migration tool
- **WebSockets** - Real-time communication
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server implementation

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis 6+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment variables:
```bash
cp .env.example .env
```

5. Update `.env` with your configuration:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/dynamiccontractops
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key
OPENAI_API_KEY=your-openai-api-key  # Optional
ANTHROPIC_API_KEY=your-anthropic-api-key  # Optional
```

6. Initialize the database:
```bash
alembic upgrade head
```

7. Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/          # API endpoint definitions
│   │       └── router.py           # Main API router
│   ├── core/
│   │   ├── config.py              # Configuration settings
│   │   ├── database.py            # Database setup
│   │   └── security.py            # Authentication utilities
│   ├── models/                    # SQLAlchemy models
│   ├── schemas/                   # Pydantic schemas
│   ├── services/                  # Business logic layer
│   ├── websocket/                 # WebSocket management
│   └── main.py                    # FastAPI application
├── alembic/                       # Database migrations
├── scripts/                       # Utility scripts
├── requirements.txt               # Python dependencies
└── docker-compose.yml            # Docker configuration
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/me` - Update current user

### Projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/` - List projects
- `GET /api/v1/projects/{project_id}` - Get project details
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project

### Contracts
- `POST /api/v1/contracts/` - Create contract
- `GET /api/v1/contracts/` - List contracts
- `GET /api/v1/contracts/{contract_id}` - Get contract details
- `PUT /api/v1/contracts/{contract_id}` - Update contract
- `DELETE /api/v1/contracts/{contract_id}` - Delete contract
- `POST /api/v1/contracts/{contract_id}/lock` - Lock/unlock contract

### Comments
- `POST /api/v1/comments/` - Create comment
- `GET /api/v1/comments/contract/{contract_id}` - Get contract comments
- `PUT /api/v1/comments/{comment_id}` - Update comment
- `DELETE /api/v1/comments/{comment_id}` - Delete comment
- `POST /api/v1/comments/{comment_id}/resolve` - Resolve comment

### AI Suggestions
- `POST /api/v1/ai-suggestions/generate` - Generate AI suggestions
- `GET /api/v1/ai-suggestions/contract/{contract_id}` - Get contract suggestions
- `PUT /api/v1/ai-suggestions/{suggestion_id}` - Update suggestion status
- `POST /api/v1/ai-suggestions/feedback` - Submit feedback

### Versions
- `POST /api/v1/versions/` - Create new version
- `GET /api/v1/versions/contract/{contract_id}` - Get contract versions
- `POST /api/v1/versions/compare` - Compare versions
- `POST /api/v1/versions/{version_id}/approve` - Approve version

### Presence
- `POST /api/v1/presence/` - Update presence
- `GET /api/v1/presence/contract/{contract_id}` - Get contract presence
- `DELETE /api/v1/presence/{contract_id}` - Remove presence

### Analytics
- `GET /api/v1/analytics/contract/{contract_id}` - Contract analytics
- `GET /api/v1/analytics/project/{project_id}` - Project analytics
- `GET /api/v1/analytics/platform` - Platform analytics (admin only)
- `GET /api/v1/analytics/dashboard` - User dashboard

### WebSocket
- `WS /ws/{contract_id}` - Real-time collaboration

## Development

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

## Docker Deployment

### Development with Docker Compose

```bash
docker-compose up -d
```

This will start:
- FastAPI application on port 8000
- PostgreSQL database on port 5432
- Redis on port 6379
- Celery worker for background tasks

### Production Deployment

1. Build the image:
```bash
docker build -t dynamiccontractops-backend .
```

2. Run with production environment variables:
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379 \
  -e SECRET_KEY=production-secret-key \
  dynamiccontractops-backend
```

## AI Integration

The platform supports multiple AI providers:

### OpenAI Integration
Set `OPENAI_API_KEY` in your environment to enable:
- Contract analysis using GPT-4
- Intelligent suggestions for contract improvements
- Risk assessment and compliance checking

### Anthropic Integration
Set `ANTHROPIC_API_KEY` in your environment to enable:
- Contract analysis using Claude
- Alternative AI suggestions
- Enhanced document understanding

## Real-time Features

The WebSocket implementation supports:
- **Live cursor tracking** - See where other users are editing
- **Real-time text synchronization** - Collaborative editing
- **Presence awareness** - Know who's online
- **Live comments** - Instant comment notifications
- **Suggestion updates** - Real-time AI suggestion notifications

## Security Features

- **JWT Authentication** with access and refresh tokens
- **Password hashing** using bcrypt
- **API key management** for external integrations
- **Rate limiting** to prevent abuse
- **CORS protection** for cross-origin requests
- **Input validation** using Pydantic schemas

## Monitoring & Analytics

Built-in analytics provide insights into:
- Contract completion rates
- User collaboration patterns
- AI suggestion effectiveness
- Platform usage statistics
- Risk assessment metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the code examples in the `/examples` directory