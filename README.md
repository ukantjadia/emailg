# Email Generator

A powerful web application that leverages multiple AI providers (Deepseek, Claude, Groq) to generate personalized outreach emails. The application supports various email styles, purposes, and tones while providing a user-friendly interface for feedback and continuous improvement.

## ✨ Features

- **Multi-AI Provider Support**: Integrates with Deepseek, Claude, and Groq APIs
- **Flexible Email Styles**: Direct, Friendly, and Professional tones
- **Multiple Use Cases**: Sales, Networking, Partnership, and Collaboration emails
- **User Feedback System**: Collect and store user feedback for continuous improvement
- **Web Interface**: Clean, responsive HTML forms for easy email generation
- **RESTful API**: Well-structured endpoints for programmatic access
- **Database Integration**: PostgreSQL backend for feedback storage
- **Comprehensive Logging**: Built-in logging system for debugging and monitoring

## 🏗️ Architecture

```
emailg-sandbox_emailgen/
├── app.py                          # Flask application entry point
├── logging_setup.py                # Centralized logging configuration
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore patterns
│
├── config/
│   └── config.py                   # Application configuration
│
├── Routes/                         # Blueprint route definitions
│   ├── email_routes.py             # Email generation endpoints
│   ├── feedback_routes.py          # Feedback submission endpoints
│   ├── input_form_routes.py        # Form rendering endpoints
│   └── main_routes.py              # Main application routes
│
├── controllers/                    # Business logic layer
│   ├── feedback_controller.py      # Feedback processing logic
│   ├── generate_controller.py      # Email generation logic
│   └── prompt_controller.py        # Prompt template management
│
├── models/                         # Data models
│   ├── __init__.py                 # Models package initialization
│   ├── feedback_model.py           # SQLAlchemy feedback model
│   └── feedback_model_old.py       # Legacy model (deprecated)
│
├── prompt_bank/                    # Email prompt templates
│   ├── direct_collaboration_v1.txt
│   ├── direct_networking_v1.txt
│   ├── direct_partnership_v1.txt
│   ├── direct_sales_v1.txt
│   ├── friendly_collaboration_v1.txt
│   ├── friendly_networking_v1.txt
│   ├── friendly_partnership_v1.txt
│   ├── friendly_sales_v1.txt
│   ├── professional_collaboration_v1.txt
│   ├── professional_networking_v1.txt
│   ├── professional_partnership_v1.txt
│   └── professional_sales_v1.txt
│
├── templates/                      # Jinja2 HTML templates
│   ├── email_generator.html        # Main email generation form
│   ├── endpoints.html              # API documentation page
│   └── index.html                  # Landing page
│
├── static/                         # Static web assets
│   ├── style.css                   # Application styling
│   └── js/
│       └── email_generator.js      # Frontend JavaScript
│
└── utils/                          # Utility functions
    └── get_routes.py               # Route introspection utility
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- API keys for at least one AI provider (OpenAI, Anthropic, or Groq)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/ukantjadia/emailg.git
   cd emailg-sandbox_emailgen
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Create environment file**

   ```bash
   cp .env.example .env  # Create from example or create new file
   ```

2. **Configure environment variables**

   ```env
   # AI Provider API Keys (at least one required)
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   CLAUDE_API_KEY=your_claude_api_key_here
   GROQ_API_KEY=your_groq_api_key_here

   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/email_generator

   # Flask Configuration
   SECRET_KEY=your_super_secret_key_here
   FLASK_ENV=development  # Change to 'production' for production

   # Optional: Logging Configuration
   LOG_LEVEL=INFO
   ```

3. **Set up PostgreSQL database**

   ```sql
   CREATE DATABASE email_generator;
   CREATE USER your_username WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE email_generator TO your_username;
   ```

4. **Initialize database tables**
   ```bash
   python -c "
   from models.feedback_model import db
   from app import app
   with app.app_context():
       db.create_all()
       print('Database tables created successfully!')
   "
   ```

### Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:8001/`

## 📚 API Documentation

### Email Generation

**Endpoint**: `POST /api/generate-email`

Generate a personalized outreach email based on company, industry, tone, and focus parameters.

**Request Body**:

```json
{
  "tone": "friendly",
  "focus": "sales",
  "company_name": "OpenAI",
  "industry": "Artificial Intelligence",
  "model_choice": "groq",
  "user_id": "user123",
  "parent_message_id": null,
  "additional_context": [
    "OpenAI’s rollout of advanced models like o3, o4-mini, and Deep Research demonstrates an impressive commitment to pushing the boundaries of reasoning, multimodal capabilities, and practical tool integration, empowering professionals and everyday users alike with more intelligent and versatile AI assistants.",
    "By introducing business-focused offerings with custom connectors, memory features, and flexible deployment options, OpenAI is thoughtfully addressing enterprise needs while ensuring companies can securely integrate cutting-edge AI into their own unique workflows and data ecosystems.",
    "The expansion of voice capabilities, seamless multilingual translation, and image generation in GPT-4o shows OpenAI’s dedication to building an engaging, interactive AI experience that transcends traditional text-based interactions and unlocks creative possibilities for users worldwide."
  ]
}
```

**Parameters**:

- `tone`: Email tone (`friendly`, `professional`, `direct`)
- `focus`: Email purpose (`sales`, `networking`, `partnership`, `collaboration`)
- `company_name`: Target company name
- `industry`: Target company's industry
- `model_choice`: AI provider (`openai`, `anthropic`, `groq`)
- `user_id`: User identifier (optional, defaults to "test_test")
- `parent_message_id`: For regenerations (optional)
- `additional_context`: Array of context strings (each must be ≥20 words)

**Response**:

```json
{
  "message": "Subject: What OpenAI’s o4-mini & Deep Research Mean for the Next AI Winners\n\nHi there,\n\nHi team at OpenAI, I saw your recent work in the Artificial Intelligence space, especially...",
  "prompt_version": "friendly_sales_v1",
  "model_used": "groq",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "parent_message_id": null,
  "prompt_text": "You are a friendly sales professional..."
}
```

**Error Responses**:

- `400`: Invalid input (e.g., context points too short)
- `404`: Prompt template not found
- `402`: Insufficient API credits
- `500`: Server error
- `502`: Invalid or missing API key

### Feedback Submission

**Endpoint**: `POST /api/feedback`

Submit upvote/downvote feedback on generated emails.

**Request Body**:

```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "feedback_type": "upvote",
  "user_id": "user123",
  "company_name": "OpenAI",
  "industry": "artificial intelligence",
  "tone": "friendly",
  "focus": "sales",
  "context": "OpenAI’s rollout of advanced models...",
  "model_used": "groq",
  "prompt_template": "friendly_sales_v1",
  "prompt_text": "You are a friendly sales professional...",
  "generated_message": "What OpenAI’s o4-mini & Deep Research Mean..."
}
```

**Response**:

```json
{
  "success": true,
  "message": "Feedback captured successfully"
}
```

### Advanced Feedback Endpoints

**Endpoint**: `POST /feedback`

General feedback capture endpoint.

**Endpoint**: `POST /regenerate`

Handle content regeneration requests.

**Endpoint**: `GET /analytics`

Get feedback analytics with optional filters.

**Query Parameters**:

- `user_id`: Filter by user
- `model_used`: Filter by AI model
- `tone`: Filter by email tone
- `focus`: Filter by email focus
- `date_from`: Start date filter
- `date_to`: End date filter

**Response**:

```json
{
  "total_generations": 1250,
  "upvotes": 892,
  "downvotes": 358,
  "satisfaction_rate": 71.36,
  "top_models": [
    { "model": "deepseek", "count": 650 },
    { "model": "claude", "count": 400 },
    { "model": "groq", "count": 200 }
  ],
  "popular_combinations": [
    { "tone": "friendly", "focus": "sales", "count": 450 },
    { "tone": "professional", "focus": "partnership", "count": 320 }
  ]
}
```

**Endpoint**: `GET /history`

Get user's feedback history.

**Query Parameters**:

- `user_id`: Required user identifier

**Response**:

```json
{
  "success": true,
  "data": [
    {
      "message_id": "550e8400-e29b-41d4-a716-446655440000",
      "feedback_type": "upvote",
      "company_name": "OpenAI",
      "generated_at": "2024-01-15T10:30:00Z",
      "model_used": "deepseek"
    }
  ]
}
```

## 🎨 Available Prompt Templates

The application includes 12 pre-built prompt templates covering different combinations of:

### Tones

- **Direct**: Straightforward, no-nonsense approach
- **Friendly**: Warm, approachable, conversational
- **Professional**: Formal, business-appropriate tone

### Use Cases

- **Sales**: Product/service sales outreach
- **Networking**: Professional relationship building
- **Partnership**: Business collaboration proposals
- **Collaboration**: Project-based cooperation

### Template Naming Convention

`{tone}_{use_case}_v{version}.txt`

Examples:

- `friendly_sales_v1.txt`
- `professional_partnership_v1.txt`
- `direct_networking_v1.txt`

## 🌐 Web Interface

### Main Pages

1. **Landing Page** (`/`): Redirects to email generator
2. **Email Generator** (`/email-generator`): Interactive form for email generation
3. **API Documentation** (`/endpoints`): Complete API reference
4. **User Documentation** (`/docs`): Coming soon page

### Using the Web Interface

1. Navigate to `/email-generator` (or just `/` for auto-redirect)
2. Fill out the form with:
   - **Company Name**: Target company
   - **Industry**: Target company's industry sector
   - **Tone**: Choose from Friendly, Professional, or Direct
   - **Focus**: Select Sales, Networking, Partnership, or Collaboration
   - **AI Model**: Choose OpenAI, Anthropic, or Groq
   - **Context Points**: Add 3+ context points (minimum 20 words each)
3. Click "Generate Email"
4. Review the generated email with subject line and body
5. Use upvote/downvote buttons to provide feedback
6. Click "Regenerate" for alternative versions

## 🔧 Development

### Adding New Prompt Templates

1. Create a new `.txt` file in the `prompt_bank/` directory
2. Follow the naming convention: `{tone}_{use_case}_v{version}.txt`
3. Write your prompt template with clear instructions for the AI
4. Test the prompt using the API or web interface

### Extending API Functionality

1. Create new route files in the `Routes/` directory
2. Implement corresponding controller logic in `controllers/`
3. Register new blueprints in `app.py`
4. Update the API documentation

### Database Schema

The application uses a normalized feedback tracking system with the MessageFeedback model:
MessageFeedback Table (message_feedback):

- `entry_id`: Primary key (UUID) - unique for every feedback action
- `message_id`: Links to the generated message (not unique, allows multiple feedback entries per message)
- `parent_message_id`: Links to parent message ID for regenerations (nullable)
- `user_id`: User identifier for tracking (nullable)
- `company_name`: Target company name (nullable)
- `industry`: Target industry sector (nullable)
- `tone`: Email tone used (friendly, professional, direct) (nullable)
- `focus`: Email focus (sales, networking, partnership, collaboration) (nullable)
- `context`: Full context provided by user (nullable)
- `model_used`: AI provider used (openai, anthropic, groq) (nullable)
- `prompt_template`: Template identifier (e.g., friendly_sales_v1) (nullable)
- `prompt_text`: Full prompt sent to AI (nullable)
- `generated_message`: JSONB containing generated email and metadata (nullable)
- `feedback_type`: Type of interaction (generation, regeneration, upvote, downvote) (required)
- `timestamp`: Timestamp of record creation (defaults to UTC now)

#### Key Design Features:

- **One row per feedback action**: Each generation, upvote, downvote, or regeneration creates a new entry
- **Message lineage tracking**: parent_message_id links regenerated content to original messages
- **Flexible schema**: Most fields are nullable to accommodate different feedback types
- **JSONB storage**: generated_message uses PostgreSQL JSONB for efficient JSON storage and querying
- **UUID primary keys**: Uses UUID4 for globally unique identifiers

### Logging

Logs are configured in `logging_setup.py` and include:

- Request/response logging
- Error tracking
- Performance metrics
- AI provider usage statistics

## 🧪 Testing

### Manual Testing

1. **Web Interface Testing**:

   ```bash
   # Start the application
   python app.py

   # Navigate to http://localhost:8001/email-generator
   # Test various combinations of tones and use cases
   ```

2. **API Testing**:

   ```bash
   # Test email generation
   curl -X POST http://127.0.0.1:8001/api/generate-email \
     -H "Content-Type: application/json" \
     -d '{
       "tone": "friendly",
       "focus": "sales",
       "company_name": "OpenAI",
       "industry": "Artificial Intelligence",
       "model_choice": "groq",
       "additional_context": [
         "OpenAI’s rollout of advanced models like o3, o4-mini, and Deep Research demonstrates an impressive commitment to pushing the boundaries of reasoning, multimodal capabilities, and practical tool integration, empowering professionals and everyday users alike with more intelligent and versatile AI assistants.",
         "By introducing business-focused offerings with custom connectors, memory features, and flexible deployment options, OpenAI is thoughtfully addressing enterprise needs while ensuring companies can securely integrate cutting-edge AI into their own unique workflows and data ecosystems.",
         "The expansion of voice capabilities, seamless multilingual translation, and image generation in GPT-4o shows OpenAI’s dedication to building an engaging, interactive AI experience that transcends traditional text-based interactions and unlocks creative possibilities for users worldwide."
       ]
     }'

   # Test feedback submission
   curl -X POST http://127.0.0.1:8001/api/feedback \
     -H "Content-Type: application/json" \
     -d '{
       "message_id": "test-message-id",
       "feedback_type": "upvote",
       "user_id": "test-user",
       "company_name": "OpenAI",
       "industry": "Artificial Intelligence",
       "tone": "friendly",
       "focus": "sales",
       "context": "OpenAI’s rollout of advanced models...",
       "model_used": "groq"
     }'

   # Get user feedback history
   curl -X GET "http://127.0.0.1:8001/history?user_id=test-user"

   # Get analytics
   curl -X GET "http://127.0.0.1:8001/analytics?model_used=groq&tone=friendly"
   ```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**:

   - Set `FLASK_ENV=production`
   - Use strong `SECRET_KEY`
   - Configure production database URL

2. **Database**:

   - Use connection pooling
   - Set up database backups
   - Configure SSL connections

3. **Security**:

   - Implement rate limiting
   - Add input validation and sanitization
   - Use HTTPS in production
   - Secure API key storage

4. **Performance**:
   - Configure caching
   - Set up load balancing
   - Monitor AI provider rate limits

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "app.py"]
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write tests** (when test framework is added)
5. **Commit your changes**
   ```bash
   git commit -m "Add your descriptive commit message"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose
- Comment complex logic

## 📝 License

This project is proprietary. Please contact the repository owner for licensing information and usage permissions.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**:

   - Verify PostgreSQL is running
   - Check DATABASE_URL format
   - Ensure database and user exist

2. **AI Provider Errors**:

   - Verify API keys are correct
   - Check rate limits
   - Ensure sufficient account credits

3. **Import Errors**:

   - Activate virtual environment
   - Reinstall requirements: `pip install -r requirements.txt`

4. **Template Not Found**:
   - Check prompt file exists in `prompt_bank/`
   - Verify naming convention
   - Check file permissions

### Getting Help

- Check the application logs for detailed error messages
- Review the `/endpoints` page for API documentation
- Verify environment variable configuration
- Test with minimal examples first

## 📞 Support

For support, questions, or contributions, please contact the repository maintainer or open an issue in the project repository.

---
