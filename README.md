# 🤖 AI Chatbot using Angular, FastAPI & Ollama (Mistral)

A full-stack AI chatbot that enables users to interact with a locally hosted Large Language Model (LLM). The application features a modern Angular frontend, a FastAPI backend, and uses the Mistral model through Ollama for AI-powered responses.

---

## 🚀 Demo

> Running locally using Ollama and Mistral.

---

# ✨ Features

- 💬 Modern responsive chat interface
- 🤖 AI-powered conversations using Mistral
- ⚡ FastAPI REST API backend
- 🌐 Angular 22 frontend
- 🔄 Real-time communication between frontend and backend
- ⌨️ Typing indicator
- 🛡️ Error handling
- 🧠 Prompt engineering for improved responses
- 🏠 100% Local AI (No OpenAI API required)

---

# 🏗️ System Architecture

```
+----------------------+
|      Angular UI      |
+----------+-----------+
           |
           | HTTP POST
           |
+----------v-----------+
|       FastAPI        |
+----------+-----------+
           |
           | REST API
           |
+----------v-----------+
|        Ollama        |
+----------+-----------+
           |
           |
+----------v-----------+
|    Mistral LLM       |
+----------------------+
```

---

# 🛠️ Tech Stack

### Frontend
- Angular 22
- TypeScript
- HTML5
- CSS3

### Backend
- Python
- FastAPI
- Requests

### AI
- Ollama
- Mistral LLM

### Tools
- Git
- GitHub
- VS Code

---

# 📂 Project Structure

```
AI-CHATBOT
│
├── chatbot-ui
│   ├── src
│   ├── angular.json
│   ├── package.json
│   └── ...
│
├── ai-chatbot-backend
│   ├── app
│   │   ├── main.py
│   │   ├── services
│   │   │    └── ollama_service.py
│   │   └── __init__.py
│   ├── requirements.txt
│   └── venv
│
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/ArinTholia/AI-Chatbot.git
```

---

## Frontend

```bash
cd chatbot-ui
npm install
ng serve
```

Frontend:

```
http://localhost:4200
```

---

## Backend

```bash
cd ai-chatbot-backend

python -m venv venv

venv\Scripts\activate

pip install fastapi uvicorn requests

python -m uvicorn app.main:app --reload
```

Backend:

```
http://127.0.0.1:8000
```

---

## Install Ollama

Download:

https://ollama.com

Install Mistral:

```bash
ollama pull mistral
```

Run:

```bash
ollama serve
```

---

# 📡 API

## POST /chat

Request

```json
{
  "message": "What is Angular?"
}
```

Response

```json
{
  "response": "Angular is a TypeScript-based frontend framework developed by Google..."
}
```

---

# 📸 Screenshots

## Chat Interface

_Add screenshot here_

---

## FastAPI Swagger

_Add screenshot here_

---

# 🔮 Future Enhancements

- Streaming responses (ChatGPT-style)
- Chat history
- Markdown rendering
- Code syntax highlighting
- Multiple AI models
- Authentication
- Dark mode
- Docker support
- Cloud deployment

---

# 🎓 Learning Outcomes

This project helped me understand:

- Angular Standalone Components
- Angular Forms
- Angular HttpClient
- REST API development with FastAPI
- Prompt Engineering
- Ollama Integration
- Local LLM deployment
- Frontend–Backend communication
- API error handling
- Full-stack AI application architecture

---

# 👨‍💻 Author

**Arin Tholia**

GitHub: https://github.com/ArinTholia

---

# ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.