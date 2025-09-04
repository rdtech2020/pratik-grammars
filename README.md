# 🚀 Pratik's Grammar Correction API

Advanced AI-powered grammar correction system with JWT authentication, user management, and analytics. Built with FastAPI, SQLAlchemy, and state-of-the-art transformer models.

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [Architecture](#architecture)
- [Authentication](#authentication)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [About the Developer](#about-the-developer)

## 🎯 About

This project provides a comprehensive grammar correction API that combines the power of AI transformer models with robust JWT-based authentication, user management, and analytics. The system is designed to be scalable, maintainable, and production-ready.

### Key Features:
- 🤖 **AI-Powered Grammar Correction**: Uses state-of-the-art T5 transformer models
- 🔐 **JWT Authentication**: Secure token-based authentication system
- 👤 **Complete User Management**: Registration, authentication, and profile management
- 📊 **User-Specific Analytics**: Each user sees only their own data
- 🔒 **Security & Validation**: Secure password hashing and input validation
- 📈 **Scalable Architecture**: Modular design with clear separation of concerns

## 🔐 Authentication System

### **JWT Token Flow:**

1. **User Registration** → Returns JWT token immediately
2. **User Login** → Returns JWT token for API access
3. **Protected Endpoints** → Require valid JWT token
4. **User Data Isolation** → Each user only sees their own data

### **Token Usage:**
```bash
# Include token in Authorization header
Authorization: Bearer <your_jwt_token>
```

### **Authentication Levels:**
- 🔓 **Public**: `/`, `/health`, `/correct/anonymous`
- 🔒 **Authenticated**: `/correct`, `/corrections/*`, `/analytics/*`, `/users/*`
- 👑 **Admin**: User management, system analytics, and global data access

### **Security Features:**
- 🔒 **Secure JWT Tokens**: Uses user IDs instead of email addresses
- 🛡️ **No Information Disclosure**: Tokens don't reveal user emails
- 🔐 **Role-Based Access**: Admin-only endpoints properly protected
- 🚫 **No Role Escalation**: Users cannot promote themselves to admin
- 📝 **Admin Script Only**: Admin users only created through secure script

## 🏗️ Architecture

The project follows a clean, modular architecture:

```
pratik-grammars/
├── src/                    # Source code
│   └── grammar_app/        # Main application
│       ├── routes/         # API route modules
│       │   ├── grammar.py  # Grammar correction endpoints
│       │   ├── users.py    # User management endpoints
│       │   ├── database.py # Database operations
│       │   ├── analytics.py # Analytics endpoints
│       │   └── system.py   # System endpoints
│       ├── models.py       # Database models
│       ├── schemas.py      # Pydantic schemas
│       ├── crud.py         # Database operations
│       ├── services.py     # Business logic
│       ├── auth.py         # JWT authentication
│       ├── database.py     # Database configuration
│       └── main.py         # FastAPI application
├── config/                 # Configuration
│   └── settings.py         # Application settings
├── tests/                  # Test files
│   ├── conftest.py         # Pytest configuration
│   ├── test_comprehensive.py # Comprehensive tests
│   └── test_authentication_flow.py # Authentication tests
├── scripts/                # Utility scripts
│   └── train_grammar_model.py # Model training
├── data/                   # Data files
│   ├── grammar.db          # SQLite database
│   └── sample_grammar_dataset.json # Sample data
├── models/                 # AI model storage
├── logs/                   # Application logs
├── docs/                   # Documentation
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── Makefile               # Development tasks
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Multi-service setup
└── README.md              # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pratik-grammars.git
   cd pratik-grammars
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup development environment**
   ```bash
   make setup-dev
   ```

5. **Start the server**
   ```bash
   make dev
   ```

The API will be available at `http://localhost:8000`

## 📖 Usage

### **1. User Registration (Get JWT Token)**
```bash
curl -X POST "http://localhost:8000/users/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "securepassword",
       "full_name": "John Doe"
     }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-08-23T14:00:00Z",
    "updated_at": "2025-08-23T14:00:00Z",
    "total_corrections": 0
  }
}
```

### **2. User Login (Get JWT Token)**
```bash
curl -X POST "http://localhost:8000/users/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "password": "securepassword"
     }'
```

### **3. Grammar Correction (Authenticated)**
```bash
curl -X POST "http://localhost:8000/correct" \
     -H "Authorization: Bearer <your_jwt_token>" \
     -H "Content-Type: application/json" \
     -d '{"text": "how is you?"}'
```

**Response:**
```json
{
  "original": "how is you?",
  "corrected": "How are you?"
}
```

**Note:** This correction is automatically saved to the database linked to your user account.

### **4. Grammar Correction (Anonymous)**
```bash
curl -X POST "http://localhost:8000/correct/anonymous" \
     -H "Content-Type: application/json" \
     -d '{"text": "how is you?"}'
```

**Note:** Anonymous corrections are NOT saved to the database.

### **5. View Your Corrections**
```bash
curl -H "Authorization: Bearer <your_jwt_token>" \
     "http://localhost:8000/corrections?page=1&per_page=10"
```

### **6. Get Your Statistics**
```bash
curl -H "Authorization: Bearer <your_jwt_token>" \
     "http://localhost:8000/analytics/my-stats"
```

### **7. Admin Access (Admin Users Only)**
```bash
# List all users
curl -H "Authorization: Bearer <admin_jwt_token>" \
     "http://localhost:8000/users?page=1&per_page=20"

# Get database statistics
curl -H "Authorization: Bearer <admin_jwt_token>" \
     "http://localhost:8000/analytics/stats"

# View all corrections across all users
curl -H "Authorization: Bearer <admin_jwt_token>" \
     "http://localhost:8000/corrections/admin/all"
```

## 📚 API Documentation

### **Core Endpoints**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/correct` | ✅ Yes | Correct grammar (saves to DB) |
| `POST` | `/correct/anonymous` | ❌ No | Correct grammar (no DB save) |
| `GET` | `/` | ❌ No | API information |
| `GET` | `/health` | ❌ No | Health check |

### **User Management**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/users/register` | ❌ No | Register new user (returns token) |
| `POST` | `/users/login` | ❌ No | User authentication (returns token) |
| `GET` | `/users/me` | ✅ Yes | Get current user profile |
| `GET` | `/users/{id}` | ✅ Yes | Get user by ID (admin only) |
| `PUT` | `/users/me` | ✅ Yes | Update current user profile |
| `PUT` | `/users/{id}` | ✅ Yes | Update user by ID (admin only) |
| `DELETE` | `/users/{id}` | ✅ Yes | Delete user (admin only) |
| `GET` | `/users` | ✅ Yes | List all users (admin only) |

### **Database Operations**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/corrections` | ✅ Yes | List user's corrections |
| `GET` | `/corrections/{id}` | ✅ Yes | Get correction by ID (own) |
| `GET` | `/corrections/recent` | ✅ Yes | Get user's recent corrections |
| `GET` | `/corrections/search` | ✅ Yes | Search user's corrections |
| `DELETE` | `/corrections/{id}` | ✅ Yes | Delete correction (own) |

### **Admin Database Operations**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/corrections/admin/all` | ✅ Yes | List all corrections (admin only) |
| `GET` | `/corrections/admin/{id}` | ✅ Yes | Get any correction (admin only) |
| `DELETE` | `/corrections/admin/{id}` | ✅ Yes | Delete any correction (admin only) |
| `GET` | `/corrections/admin/search` | ✅ Yes | Search all corrections (admin only) |

### **Analytics**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/analytics/my-stats` | ✅ Yes | Current user statistics |
| `GET` | `/analytics/my-corrections` | ✅ Yes | Current user corrections |
| `GET` | `/analytics/my-correction-count` | ✅ Yes | Current user correction count |
| `GET` | `/analytics/stats` | ✅ Yes | Database statistics (admin only) |

### **Admin Analytics**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/analytics/admin/users/{uuid}/corrections` | ✅ Yes | Any user corrections (admin only) |
| `GET` | `/analytics/admin/users/{uuid}/correction-count` | ✅ Yes | Any user correction count (admin only) |

### **Interactive Documentation**

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

**🔑 Testing with Swagger:**
1. Click the **"Authorize"** button (🔒)
2. Enter your JWT token: `Bearer <your_token>`
3. Test authenticated endpoints
4. Test unauthenticated endpoints

## 👑 Admin Setup

### **Creating Admin Users**

After setting up the database, create an admin user using the provided script:

```bash
# Run the admin creation script
python scripts/create_admin.py

# Or set environment variables for custom admin details
export ADMIN_EMAIL="your-admin@example.com"
export ADMIN_NAME="Your Admin Name"
export ADMIN_PASSWORD="secure-admin-password"
python scripts/create_admin.py
```

**Default Admin Credentials:**
- **Email**: admin@grammar-api.com
- **Password**: admin123
- **Name**: System Administrator

### **Admin Capabilities**
- 👥 **User Management**: View, update, and delete any user
- 📊 **System Analytics**: Access comprehensive database statistics
- 🔍 **Global Data Access**: View all corrections across all users
- 🛠️ **System Administration**: Manage the entire application
- 🔐 **Secure Identifiers**: Uses UUIDs instead of simple integer IDs for enhanced security
- 🔒 **Secure JWT Tokens**: Uses user IDs instead of email addresses to prevent information disclosure

## 🧪 Testing
```bash
python tests/test_authentication_flow.py
```

This test demonstrates:
- ✅ User registration and JWT token generation
- ✅ User login and token validation
- ✅ Authenticated endpoint access
- ✅ User-specific data isolation
- ✅ Anonymous endpoint access
- ✅ Proper error handling

### **Run All Tests**
```bash
make test
```

### **Test Coverage**
```bash
pytest tests/ -v --cov=src --cov-report=html
```

## 🛠️ Development

### **Available Commands**

```bash
# Install dependencies
make install

# Start development server
make dev

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Clean up files
make clean

# Generate documentation
make docs

# Setup development environment
make setup-dev

# Full test suite
make test-full
```

### **Code Structure**

The application follows a clean architecture pattern:

- **Routes**: Handle HTTP requests and responses
- **Services**: Contain business logic
- **Models**: Define database structure
- **Schemas**: Validate request/response data
- **CRUD**: Database operations
- **Auth**: JWT authentication and authorization
- **Config**: Application settings

### **Adding New Features**

1. **New Route**: Add to appropriate file in `src/grammar_app/routes/`
2. **New Model**: Add to `src/grammar_app/models.py`
3. **New Schema**: Add to `src/grammar_app/schemas.py`
4. **New Service**: Add to `src/grammar_app/services.py`
5. **New CRUD**: Add to `src/grammar_app/crud.py`
6. **New Auth**: Add to `src/grammar_app/auth.py`

## 🚀 Deployment

### **Docker Deployment**

1. **Build the image**
   ```bash
   make docker-build
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### **Production Deployment**

1. **Environment setup**
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost/db"
   export SECRET_KEY="your-secure-secret-key"
   export ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

2. **Run production server**
   ```bash
   make run
   ```

## 👨‍💻 About the Developer

**Ram Dayal** - Senior Software Engineer

### Professional Expertise
- **Backend Development**: Python, FastAPI, Django, Node.js, Express.js
- **Database Design**: PostgreSQL, MySQL, MongoDB, Redis, SQLAlchemy
- **API Development**: RESTful APIs, GraphQL, Microservices Architecture
- **DevOps & Cloud**: AWS, Docker, Kubernetes, CI/CD, GitLab, GitHub Actions
- **System Architecture**: Scalable Systems, Distributed Systems, Event-Driven Architecture

### Technical Skills
- **Languages**: Python, JavaScript, Rust, Shell-script
- **Frameworks**: FastAPI, Django, Flask, Express.js
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Cloud & DevOps**: AWS, Docker, Kubernetes
- **Testing**: Pytest, Jest, Selenium, Postman, API Testing

### Experience
- **Senior Software Engineer** with 5+ years of experience
- **Full-Stack Development** expertise
- **System Architecture** and **Scalable Solutions**
- **API Design** and **Microservices**
- **Database Optimization** and **Performance Tuning**

### Project Showcase
- **API Development**: Designed and implemented RESTful APIs
- **Microservices**: Developed distributed systems
- **Database Design**: Optimized database schemas and queries
- **DevOps Automation**: Implemented CI/CD pipelines

### Connect
- **LinkedIn**: [Ram Dayal](https://www.linkedin.com/in/i-am-ramaji/)
- **GitHub**: [@ramdayal](https://github.com/ramdayal)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact: [LinkedIn](https://www.linkedin.com/in/i-am-ramaji/)

---

**Built with ❤️ by Ram Dayal**

*Last Updated: August 2025*
