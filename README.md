# 💰 Smart Budgeting

**Smart Budgeting** is a Django web application for personal finance management. It helps users track income, expenses, savings goals, and debts in one place, with AI-powered recommendations, automatic invoice scanning (OCR), multi-currency support, and a notification system to keep users on top of their finances.

## 🎥 Demo

[![Watch the demo](https://img.shields.io/badge/▶-Watch%20Demo%20Video-blue?style=for-the-badge)](https://drive.google.com/file/d/1mgQrWwj1uzi9-ReGSGTrKS4nuuf44ybN/view?usp=sharing)

> Click the badge above to watch the full demo (hosted on Google Drive).

## ✨ Features

### Core Functionality
- ✅ **User Management**: Registration, authentication, password reset, email confirmation
- 💵 **Revenue Tracking**: Multi-currency support with automatic conversion
- 💸 **Expense Management**: OCR invoice scanning, budget alerts, category-based tracking
- 🎯 **Savings Goals**: Progress tracking with visual indicators and deadline notifications
- 💳 **Debt Management**: Payment tracking, automatic balance calculation, due date reminders
- 👥 **Collaborative Groups**: Shared savings objectives with email notifications
- 📊 **Budget Analytics**: Monthly spending vs income visualization with progress bars
- 🔔 **Smart Notifications**: In-app and email alerts for deadlines and budget overruns
- 🤖 **AI Assistant**: Intelligent chatbot (Groq/Llama 3.1) for personalized financial advice
- 📈 **AI Recommendations**: Automated spending analysis and optimization suggestions

### Advanced Features
- **OCR Invoice Scanning**: Automatic data extraction from receipt images using Tesseract
- **Multi-Currency Support**: Real-time exchange rate conversion
- **Category Management**: Global and personal expense categories
- **Admin Dashboard**: User and category management interface

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Django templates, Bootstrap
- **Database:** SQLite (development)
- **OCR:** Tesseract
- **AI:** Groq API (Llama 3.1) / GitHub Models API
- **Email:** SMTP (Gmail / Mailtrap / SendGrid)
- **Deployment:** Gunicorn + Nginx

## 📁 Project Structure

```
smart-budgeting/
├── apps/              # Django apps (users, revenus, depenses, objectifs, dettes, groups, categories, notifications, aiApp)
├── config/             # Project settings, root urls.py
├── media/              # User-uploaded files (gitignored)
├── nginx/              # Nginx configuration for deployment
├── scripts/            # Utility / deployment scripts
├── src/                # Additional source files
├── templates/           # Shared HTML templates
├── web_project/         # Project-level package
├── .env.example         # Environment variable template
├── manage.py
└── pyproject.toml
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip
- Tesseract OCR installed locally ([installation guide](https://github.com/tesseract-ocr/tesseract))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/smart-budgeting.git
cd smart-budgeting

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# then edit .env with your own values

# Apply migrations
python manage.py migrate

# Create a superuser (admin account)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`.

## 🧪 Running Tests

```bash
python manage.py test
```

## 👥 Team

| Name | Module |
|------|--------|
| Safa | Authentication & User Management |
| Wajd | UI Template, Savings Goals, Notifications |
| Asma | Groups & Group Notifications |
| Baraa | Expenses, Budget Tracking, OCR |
| Roudayna | Income & Currency Conversion |
| Ghofrane | Categories & Budget Alerts |
| Belkis | Debt Management |

## 📌 Project Management

This project follows Scrum methodology with 3 sprints:
Sprint Breakdown
Sprint 1: Core CRUD operations (Users, Revenues, Expenses, Goals, Debts, Groups, Categories)
Sprint 2: Advanced features (Password reset, Budget tracking, OCR, Currency conversion, Email notifications)
Sprint 3: AI features (Chatbot with Groq, Recommendations with GitHub Models)

### Documentation
📄 Product Backlog
📄 Sprint 1 Backlog
📄 Sprint 2 Backlog
📄 Sprint 3 Backlog - AI
📄 Story Tests

