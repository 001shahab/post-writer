# Post Generator Flask Application

This Flask application generates a post by fetching articles from Google News, extracting their content, and then using the OpenAI API to create an HTML-formatted post. The user can enter a topic, specify a target audience, and choose a style for the post. The generated post is displayed in a simple, minimalistic web UI.

## Features

- **User Interface:** A minimalistic web form to input the topic, audience, and select a style.
- **Article Fetching:** Searches for articles from the past year using Google News.
- **Content Extraction:** Uses `newspaper3k` to extract text from articles (skips articles if extraction fails).
- **Content Generation:** Constructs a prompt and calls the OpenAI Chat API with the model `o1-2024-12-17` to generate a post.
- **Formatted Output:** The generated post (in HTML format) is rendered on the web page along with metadata (token usage, inference time, etc.).

## Prerequisites

- Python 3.6 or higher
- [Flask](https://palletsprojects.com/p/flask/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [openai](https://github.com/openai/openai-python)
- [newspaper3k](https://github.com/codelucas/newspaper)
- [GoogleNews](https://pypi.org/project/GoogleNews/)

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <repository_folder>

2. **Create and activate a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt

4. **Set up environment variables:**

Create a .env file in the project root and add your OpenAI API key:
    OPENAI_API_KEY=your_openai_api_key_here

## Running the Application

1. Start the Flask server on port 8000:

    ```bash
    python app.py

2. Open your web browser:

Visit http://localhost:8000 to access the application.


## Usage
1. Fill Out the Form:
Topic: Enter the subject you want to generate a post about.
Audience: Specify the target audience.
Style: Choose one of the following styles:
    Easy to read
    Exciting read
    Technical read
    Marketing purpose
    Upskilling
2. Submit the Form:
Click the "Generate Post" button.
The application will fetch relevant articles, generate a prompt, and call the OpenAI API.
The generated post and metadata (token usage, inference time, etc.) are then displayed on the page.


## Folder Structure

my_app/
├── app.py
├── README.md
└── templates/
    └── index.html
