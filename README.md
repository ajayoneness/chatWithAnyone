# Chatbot System with Django & Next.js

## Overview
This is a chatbot system where users can upload WhatsApp chat histories with their exes. The system processes the chat data using machine learning and generates a chatbot that mimics the ex's conversation style. The backend is built with Django, and the frontend is developed using Next.js.

## Features
- Upload WhatsApp chat history.
- Train a chatbot on chat data.
- Interact with the trained chatbot.
- Store and retrieve past conversations.

## Tech Stack
- **Backend**: Django, Django REST Framework (DRF), SQLite/PostgreSQL
- **Frontend**: Next.js, React
- **Machine Learning**: Transformers, Hugging Face, Coqui TTS
- **Server**: Nginx, Gunicorn (for deployment)
- **OS**: Ubuntu/CentOS

---

## Installation & Setup
### **1. Clone the Repository**
```bash
git clone https://github.com/your-repo/chatbot-system.git
cd chatbot-system
```

### **2. Backend (Django)**
#### **Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

#### **Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **Apply Migrations**
```bash
python manage.py migrate
```

#### **Run the Development Server**
```bash
python manage.py runserver
```

#### **API Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/upload-chat/` | Upload WhatsApp chat history |
| GET | `/train-model/` | Train chatbot on user data |
| POST | `/chat/` | Interact with chatbot |

### **3. Frontend (Next.js)**
#### **Install Dependencies**
```bash
cd frontend
npm install
```

#### **Run Next.js Server**
```bash
npm run dev
```

---

## Troubleshooting
### **1. Integrity Error: NOT NULL constraint failed (persona_id)**
**Solution:** Ensure `persona_id` is included when saving conversation data.
```python
ConversationMemory.objects.create(
    session=session,
    user_input=user_input,
    bot_response=response,
    persona=persona  # Ensure persona is retrieved correctly
)
```

### **2. Token Length Exceeding Model Limits**
**Error:** `Token indices sequence length is longer than the specified maximum sequence length (1062 > 1024).`

**Solution:** Truncate input text before sending it to the model:
```python
MAX_LENGTH = 1024
if len(tokenizer.encode(user_input)) > MAX_LENGTH:
    user_input = tokenizer.decode(tokenizer.encode(user_input)[:MAX_LENGTH])
```

---

## Deployment
### **1. Deploy Django Backend with Gunicorn & Nginx**
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### **2. Deploy Next.js Frontend**
```bash
npm run build
npm start
```

---

## License
MIT License

---

## Author
**Your Name** - [Your GitHub](https://github.com/your-github)

