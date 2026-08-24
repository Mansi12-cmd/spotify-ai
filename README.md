# 🎵 Spotify AI — Personalized Music Assistant

> **An AI-powered Spotify assistant that understands user intent, remembers preferences, and provides personalized music recommendations.**

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://www.docker.com/)
[![Spotify](https://img.shields.io/badge/Spotify-API-black?logo=spotify)](https://developer.spotify.com/)

---

## ✨ Overview

**Spotify AI** is a personalized AI music assistant that combines an LLM with Spotify and user memory.

Instead of searching Spotify for every message, the system first understands **what the user actually wants** and decides whether it needs:

* 🧠 Stored user context
* 💬 Conversation history
* 🎵 Spotify search
* 🤖 AI-generated response

This makes the assistant more personalized and efficient.

---

## 🚀 Key Features

* 🎧 **Personalized Music Recommendations**
* 🧠 **User Preference Memory**
* 💬 **Conversation Context**
* 🎯 **Intent-Based Decision Making**
* 🔎 **Spotify API Integration**
* ⚡ **Asynchronous Processing**
* 🧩 **Embedding-Based Memory**
* 🐳 **Docker & Docker Compose Setup**

---

## 💡 How It Works

```text
                    👤 User
                       │
                       ▼
                 💬 Chat Request
                       │
                       ▼
                🤖 AI / LLM Layer
                       │
              ┌────────┴────────┐
              ▼                 ▼
        🧠 User Context     🎵 Spotify
        / Database            Search
              │                 │
              └────────┬────────┘
                       ▼
                🎯 AI Decision
                       │
                       ▼
                💬 Final Response
```

### Example

**User:**

> Who is my favorite artist?

The system can use stored memory instead of unnecessarily searching Spotify.

**User:**

> I'm feeling sad. Give me some songs.

The system can use the user's stored preference/context and then search Spotify for suitable songs.

---

## 🧠 AI Memory

The application maintains useful information from conversations.

For example:

```text
User:
"When I'm sad, I like listening to Arijit Singh."

        ↓

Memory Extraction

        ↓

Stored User Context

        ↓

Future Conversation

User:
"I'm feeling sad."

        ↓

AI understands the preference

        ↓

Spotify search for relevant music
```

This allows the assistant to provide more personalized responses over time.

---

## ⚡ Asynchronous Processing

The application uses asynchronous programming for operations that may involve waiting, such as:

* AI/LLM requests
* Database operations
* Spotify API calls

Instead of unnecessarily blocking the entire request flow, independent operations can progress while another operation is waiting.

This helps keep the application **responsive and efficient**.

---

## 🛠️ Tech Stack

| Category         | Technologies                      |
| ---------------- | --------------------------------- |
| Language         | Python                            |
| AI / LLM         | Groq API / LLM                    |
| Backend          | FastAPI                           |
| Validation       | Pydantic                          |
| Database         | SQLite                            |
| Music API        | Spotify Web API                   |
| Memory           | Embeddings + Conversation Context |
| Containerization | Docker, Docker Compose            |
| Version Control  | Git, GitHub                       |

---

## 📁 Project Structure

```text
Spotify AI/
│
├── app/
│   ├── models/
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── context_service.py
│   │   ├── conversation_service.py
│   │   ├── embedding_service.py
│   │   ├── memory_service.py
│   │   ├── memory_retrieval_service.py
│   │   ├── spotify_service.py
│   │   └── groq_service.py
│   │
│   ├── database.py
│   ├── init_db.py
│   ├── schema.sql
│   ├── schemas.py
│   └── main.py
│
├── frontend/
├── docker/
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.frontend
├── main.py
├── pyproject.toml
├── uv.lock
└── .gitignore
```

---

## 🐳 Run with Docker

### 1. Clone the repository

```bash
git clone https://github.com/Mansi12-cmd/spotify-ai.git
cd spotify-ai
```

### 2. Configure environment variables

Create a `.env` file and add your required API credentials.

> **Never commit `.env` or API keys to GitHub.**

### 3. Build and start

```bash
docker compose up -d --build
```

### 4. Stop the application

```bash
docker compose down
```

---

## 🔐 Environment Variables

Example:

```env
GROQ_API_KEY=your_api_key
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Do not use real credentials in the repository.**

---

## 🎯 What I Learned

Through this project, I worked with:

* LLM integration
* API-based application development
* User context and memory
* Embeddings
* Database initialization and schema design
* Asynchronous programming
* FastAPI backend development
* Spotify API integration
* Docker and Docker Compose
* Git and GitHub

---

## 🔮 Future Improvements

* 🎤 Voice-based music assistant
* 🎼 More advanced recommendation logic
* 📊 User listening analytics
* 💾 Improved long-term memory
* 🌐 Cloud deployment
* 🔐 Improved authentication

---

## 👩‍💻 Author

**Mansi Srivastava**

📧 [Email](mailto:srivastavamansi077@gmail.com)
💼 [LinkedIn](https://www.linkedin.com/in/mansi-srivastava-4aa65431a/)
💻 [GitHub](https://github.com/Mansi12-cmd/)

---
## 📸 Preview
<img width="1920" height="1080" alt="Screenshot (117)" src="https://github.com/user-attachments/assets/9288d7f6-da16-435f-bff8-66d9063e6e68" />
<img width="1920" height="1080" alt="Screenshot (119)" src="https://github.com/user-attachments/assets/ce965c12-3f6b-467e-a736-c04099270e30" />
<img width="1920" height="1080" alt="Screenshot (118)" src="https://github.com/user-attachments/assets/5b225318-8343-476a-a0e9-159ba49e1df1" />



### ⭐ If you like this project

Give the repository a ⭐ and feel free to explore the implementation!
