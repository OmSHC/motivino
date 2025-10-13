# Interactive Student Motivation News Website

A Django-based web application providing daily motivational content for students in grades 1-12. Features Google OAuth2 authentication, AI-powered content generation, and a modern React frontend.

## 🚀 Features

- **Google OAuth2 Authentication** - Secure login with Google accounts
- **Grade-based Content Filtering** - Personalized content for different grade levels
- **AI-powered Content Generation** - Daily motivational content using OpenAI
- **User Visit Tracking** - Track student engagement and progress
- **Bookmark System** - Save favorite content for later reading
- **Admin Content Management** - Manual content creation and management
- **Modern React Frontend** - Beautiful, responsive user interface
- **RESTful API** - Complete API for integration and development

## 🏗️ Architecture

### Backend (Django)
- **Django 4.2+** with Django REST Framework
- **SQLite** database (easily configurable for PostgreSQL)
- **Celery** for asynchronous task processing
- **Redis** as message broker for Celery
- **OAuth2** authentication with Google
- **OpenAI API** integration for content generation

### Frontend (React)
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API communication
- **Heroicons** for beautiful icons

## 📋 Prerequisites

- Python 3.10+
- Node.js 16+
- Redis server
- Google Cloud Console project (for OAuth2)
- OpenAI API key

## 🛠️ Installation

### Option 1: Docker Deployment (Recommended)

For easy deployment and production use:

```bash
# Clone the repository
git clone <repository-url>
cd motivation-news

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env

# Deploy with Docker
./deploy.sh
```

**Environment Variables:**
- `SECRET_KEY`: Django secret key (generate a secure one)
- `DATABASE_PASSWORD`: PostgreSQL database password
- `DOMAIN`: Your domain name (e.g., example.com)
- `OPENAI_API_KEY`: Your OpenAI API key (optional)

### Option 2: Manual Setup

```bash
# Clone the repository
git clone <repository-url>
cd Interactive-Student-Motivation-News

# Run the complete setup script
chmod +x setup_complete.sh
./setup_complete.sh
```

## 🐳 Docker Deployment

### Production Deployment

For production deployment with Docker:

1. **Copy environment file:**
```bash
cp .env.example .env
```

2. **Configure environment variables:**
```bash
# Edit .env with your production settings
nano .env
```

3. **Deploy with Docker:**
```bash
./deploy.sh
```

### Docker Services

- **Database**: PostgreSQL 15 with persistent data
- **Cache**: Redis 7 for session storage and Celery
- **Backend**: Django with Gunicorn WSGI server
- **Frontend**: React with Nginx reverse proxy
- **Web Server**: Nginx for static files and load balancing

### Production URLs

- **Frontend**: http://your-domain.com
- **API**: http://your-domain.com/api
- **Admin**: http://your-domain.com/admin

### Manual Setup

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup database:**
```bash
python manage.py migrate
python manage.py seed_data
```

4. **Setup React frontend:**
```bash
cd frontend
npm install
```

5. **Configure environment variables:**
```bash
cp env.example .env
# Edit .env with your configuration
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

### Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API and OAuth2 API
4. Configure OAuth consent screen
5. Create OAuth2 credentials
6. Add redirect URIs:
   - `http://127.0.0.1:8000/api/auth/oauth2/google/callback/`
   - `http://localhost:3000/auth/callback`

See [docs/GOOGLE_OAUTH_SETUP.md](docs/GOOGLE_OAUTH_SETUP.md) for detailed instructions.

## 🚀 Running the Application

### Development Mode

1. **Start Redis server:**
```bash
redis-server
```

2. **Start Django server:**
```bash
python manage.py runserver
```

3. **Start Celery worker:**
```bash
celery -A motivation_news worker --loglevel=info
```

4. **Start Celery beat (for scheduled tasks):**
```bash
celery -A motivation_news beat --loglevel=info
```

5. **Start React frontend:**
```bash
cd frontend
npm start
```

### Production Mode

1. **Build React frontend:**
```bash
cd frontend
npm run build
```

2. **Collect static files:**
```bash
python manage.py collectstatic
```

3. **Run with Gunicorn:**
```bash
gunicorn motivation_news.wsgi:application
```

## 🌐 Access Points

- **Django Admin**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/
- **React Frontend**: http://localhost:3000/
- **Homepage**: http://localhost:8000/

## 📚 API Documentation

### Authentication
- `POST /api/users/oauth/google/callback/` - Google OAuth2 callback
- `GET /api/users/oauth/google/url/` - Get OAuth2 authorization URL

### Users
- `GET /api/users/me/` - Get current user profile
- `PUT /api/users/me/update/` - Update user profile
- `POST /api/users/track-visit/` - Track user visit

### Content
- `GET /api/content/` - List content with filtering
- `GET /api/content/{id}/` - Get specific content
- `GET /api/content/quote/` - Get daily quote
- `POST /api/content/{id}/bookmark/` - Toggle bookmark
- `GET /api/content/bookmarks/` - Get user bookmarks

### Admin
- `GET /api/content/admin/` - List all content (admin)
- `POST /api/content/admin/create/` - Create content (admin)
- `PUT /api/content/admin/{id}/update/` - Update content (admin)
- `DELETE /api/content/admin/{id}/delete/` - Delete content (admin)

### Core
- `POST /api/core/generate-content/` - Trigger content generation (admin)
- `POST /api/core/generate-grade-content/` - Generate grade-specific content (admin)
- `POST /api/core/generate-quote/` - Generate daily quote (admin)

## 🧪 Testing

### Run All Tests
```bash
python run_tests.py
```

### Run Tests with Coverage
```bash
python run_tests.py --coverage
```

### Run Specific Test Modules
```bash
python manage.py test apps.users.tests
python manage.py test apps.content.tests
python manage.py test apps.core.tests
```

## 📁 Project Structure

```
Interactive-Student-Motivation-News/
├── apps/
│   ├── users/           # User management and authentication
│   ├── content/         # Content models and API
│   └── core/           # Core services and utilities
├── frontend/           # React frontend application
├── motivation_news/    # Django project settings
├── templates/          # Django HTML templates
├── static/            # Static files
├── media/             # Media files
├── logs/              # Application logs
├── docs/              # Documentation
├── requirements.txt   # Python dependencies
├── setup_complete.sh  # Complete setup script
└── run_tests.py      # Test runner
```

## 🔧 Management Commands

```bash
# Create admin user
python manage.py create_admin

# Seed sample data
python manage.py seed_data

# Generate content manually
python manage.py generate_content
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment

1. Set up production environment variables
2. Configure production database (PostgreSQL recommended)
3. Set up Redis server
4. Configure web server (Nginx + Gunicorn)
5. Set up SSL certificates
6. Configure domain and DNS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation in the `docs/` directory
- Review the API documentation at `/api/`
- Open an issue on GitHub

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Content recommendation engine
- [ ] Social sharing features
- [ ] Parent/teacher portal
- [ ] Gamification elements

---

**Built with ❤️ for student motivation and learning**