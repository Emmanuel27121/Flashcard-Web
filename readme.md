# Flashcard Web

A web app that turns PDF documents into flashcards to help you study.

## Features

- Upload a PDF and generate flashcards from its content.
- Study generated cards in the browser.
- Export flashcards as CSV.

## Tech Stack

- **Frontend:** React, Vite, JavaScript
- **Backend:** Python, FastAPI
- **PDF processing:** pdfplumber
- **Flashcard generation:** OpenAI API

## Requirements

- Node.js and npm
- Python 3.10 or newer
- An OpenAI API key

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Emmanuel27121/Flashcard-Web.git
cd Flashcard-web
```

### 2. Set up the backend
```
cd backend
python -m venv venv
```

#### Activate the virtual environment
- On Windows:
  ```
  venv\Scripts\activate
  ```
- On macOS and Linux:
  ```
  source venv/bin/activate
  ```
##### Install dependencies
```
pip install -r requirements.txt
```

#### Create a `.env` file in the `backend` directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

#### Start the backend server
```bash
uvicorn main:app --reload
```

### 3. Set up the frontend

Open a second Terminal

```
cd frontend
npm install
npm run dev
```
Open your browser and navigate to `http://localhost:5173` to access the app.


## Project Structure

```
Flashcard-web/
├── backend/     # FastAPI API and PDF/flashcard processing
└── frontend/    # React application
```


## NOTE: 
1. The backend and frontend are separate applications. Make sure to run both servers to use the app.
2. The OpenAI API key is required for generating flashcards. Make sure to keep it secure and do not expose it in the frontend code.
