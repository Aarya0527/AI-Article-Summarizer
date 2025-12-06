# 📰 NewsInsight: AI-Powered News Summarizer

## Overview

*NewsInsight* is a modern, interactive web application built with *Streamlit* that utilizes the power of *Generative AI* and established news APIs to provide users with quick, concise summaries of global news.

In today's fast-paced world, staying informed is critical, but time is scarce. NewsInsight solves this by offering two core functionalities: summarizing news articles fetched from a *global news API* based on user queries, and summarizing any article from the web using its *URL. Furthermore, it enhances accessibility by providing **AI-powered translation* of the summaries into multiple languages.

This application is designed for professionals, researchers, and anyone looking to quickly grasp the core facts and implications of a news story without reading the full, often lengthy, article.

## Key Features

* *Comprehensive News Search:* Search through a vast database of global news articles by keyword, country, and date range, powered by the *NewsAPI*.
* *Trending Topics:* Displays top-headlines and trending articles for a selected country for immediate insight into current events.
* *URL Summarization:* Paste any news article URL directly into the app to generate a summary instantly.
* *AI Summarization:* Utilizes the *Google Gemini API* to generate structured, insightful summaries that include:
    * A concise *Headline Summary*.
    * *Key Highlights* (3-5 major points).
    * *Insights & Implications* (the "so what" factor).
* *Multi-Language Translation:* Translate the generated summaries into several languages (Hindi, Spanish, French, German, Chinese, Japanese, Arabic, Russian, Portuguese) with a single click.

## Technology Stack

NewsInsight is built upon a reliable and efficient set of modern tools, combining data extraction, API integration, and cutting-edge Generative AI.

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| *Frontend/UI* | *Streamlit* | Rapidly create the interactive, responsive web interface and handle user inputs. |
| *Generative AI* | *Google Gemini API* (gemini-2.5-flash) | The core engine for sophisticated news summarization and multi-lingual translation. |
| *News Data* | *NewsAPI* | Source for fetching real-time, structured global news data and top headlines. |
| *Web Scraping* | newspaper / BeautifulSoup (bs4) | Robustly extract the main article text from a given URL for summarization. |
| *Python Libraries* | requests, dotenv | Handling HTTP requests to external APIs and securely managing API keys. |

## How It Works: The AI & Technical Flow

The application seamlessly integrates several components to deliver the final result:

1.  *News Retrieval:* User search queries (keyword, date, country) are sent to the *NewsAPI* endpoint. The API returns a list of matching articles with metadata (title, source, URL, image).
2.  *Article Content Extraction:*
    * For search results, the newspaper library attempts a clean download and parse of the full article content from the given URL.
    * For arbitrary URLs, a custom BeautifulSoup function is used for robust scraping, cleaning out navigation, headers, and footers to isolate the main text.
3.  *Core Summarization (Gemini):* The extracted text is passed to the gemini-2.5-flash model with a highly structured, system-level prompt instructing it to act as an "expert news summarizer." This ensures the output is not just a bland summary, but an analysis delivered in the required three-part format.
4.  *Translation (Gemini):* The generated English summary is passed back to the Gemini model with a prompt to perform a direct translation while *strictly preserving the original Markdown formatting and structure.*
5.  *User Experience:* *Streamlit* handles the state management (ensuring summaries persist when a new button is clicked) and renders the results, providing an intuitive, columnar layout for a professional reading experience.

## Getting Started

To run this application locally, you will need *Python (3.8+)* and the following API keys:

### 1. Prerequisites

* A *NewsAPI* key (Free tier is sufficient).
* A *Google AI Studio* API key (for the Gemini API).

### 2. Setup

1.  *Clone the repository:*
    bash
    git clone [YOUR_REPO_URL]
    cd NewsInsight
    

2.  *Create a virtual environment and install dependencies:*
    bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    
    (Note: You'll need to create a requirements.txt file listing all the libraries used in the code, such as streamlit, requests, beautifulsoup4, newspaper3k, python-dotenv, google-genai)

3.  *Configure API Keys:*
    Create a file named .env in the root directory and add your keys:
    ini
    # .env file
    NEWSAPI_KEY="YOUR_NEWS_API_KEY_HERE"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    

### 3. Run the Application

Execute the Streamlit command:

```bash
streamlit run app.py
