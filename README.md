# CodeWizard 🚀

> Empowering the next generation of coders through AI-powered learning

![Bolt AI Hackathon](https://img.shields.io/badge/Bolt%20AI-Hackathon-blue)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Built with AI](https://img.shields.io/badge/Built%20with-AI-orange)

## 🌟 About

CodeWizard is an innovative learning platform built for the [World's Largest Hackathon](https://worldslargesthackathon.devpost.com/) by Bolt AI. We're on a mission to make coding education more accessible, interactive, and engaging through the power of AI.

### 🎯 Key Features

- 🤖 **AI-Powered Learning**: Get instant feedback and explanations for your code
- 📚 **Interactive Lessons**: Step-by-step learning paths with hands-on exercises
- 💡 **Smart Hints**: AI-generated hints to help you solve coding challenges
- 🔍 **Code Analysis**: Get detailed explanations and optimizations for your code
- 🎮 **Gamified Progress**: Track your learning journey with achievements and progress tracking
- 👨‍🏫 **Admin Dashboard**: Comprehensive tools for educators to manage content and track student progress

## 🛠️ Tech Stack

- **Backend**: Python with Catzilla 
- **Database**: SQLite with SQLAlchemy
- **AI Integration**: OpenAI API
- **Authentication**: JWT-based secure authentication
- **API Documentation**: OpenAPI/Swagger

## 👥 Team

### Developers
- [Farhan Ali](https://github.com/farhaanaliii) - Backend Developer & System Architecture
- [MINHAJUL ISLAM](https://github.com/xspoilt-dev) - Backend Developer & System Architecture

### AI Integration
Our platform leverages advanced AI capabilities to provide:
- Real-time code analysis and feedback
- Personalized learning paths
- Smart code optimization suggestions
- Intelligent error detection and debugging
- Natural language code explanations

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/xspoilt-dev/codewizard_backend.git
   cd codewizard_backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with:
   ```
   HOST=0.0.0.0
   PORT=8000
   DEBUG=False
   RELOAD=False
   DATABASE_FILE=hackathon.db
   USER_TOKEN_LENGTH=32
   USER_TOKEN_LIFETIME_HOURS=24
   SECRET_KEY=your-secret-key-here
   LOG_LEVEL=INFO
   LOG_FILE=app.log
   ```

4. Run the server:
   ```bash
   python run.py
   ```

5. Access the API:
   - API Documentation: http://localhost:8000/api/v1/
   - Admin Panel: http://localhost:8000/api/v1/admin/

## 📚 API Endpoints

### Public Endpoints
- `POST /api/v1/register` - Register a new user
- `POST /api/v1/login` - User login
- `GET /api/v1/` - API information

### User Endpoints
- `GET /api/v1/profile` - Get user profile
- `GET /api/v1/lessons` - List available lessons
- `POST /api/v1/chat` - AI-powered coding assistance
- `POST /api/v1/code/evaluate` - Get code evaluation
- And many more...

### Admin Endpoints
- `GET /api/v1/admin/` - Admin dashboard
- `POST /api/v1/admin/lessons` - Create new lessons
- `GET /api/v1/admin/stats` - View platform statistics

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [World's Largest Hackathon](https://worldslargesthackathon.devpost.com/) by Bolt AI
- Special thanks to all contributors and the open-source community
- Powered by OpenAI's advanced AI capabilities

## 📞 Contact

- Project Link: [https://github.com/xspoilt-dev/codewizard_backend](https://github.com/xspoilt-dev/codewizard_backend)
- Hackathon Submission: [Devpost Link](#)

---

Made with ❤️ for the Bolt AI Hackathon by [Farhan Ali](https://github.com/farhaanaliii) and [MINHAJUL ISLAM](https://github.com/xspoilt-dev) 
