import streamlit as st
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import date

# Load API keys
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Language Map
lang_map = {
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Arabic": "ar",
    "Russian": "ru",
    "Portuguese": "pt",
}

# --------------------------- Extractors ---------------------------
def extract_article_text_newspaper(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        return f"⚠️ Failed to extract article text: {e}"

def extract_text_with_bs4(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'form']):
            tag.decompose()
        text = ' '.join(chunk.strip() for chunk in soup.stripped_strings if len(chunk.strip()) > 30)
        return text[:12000] if text else "⚠️ No readable text found on page."
    except Exception as e:
        return f"⚠️ Failed to scrape text from the webpage: {e}"

# --------------------------- Summarizer & Translator ---------------------------
def summarize_text(text):
    prompt = f"""
You are an expert news summarizer.

Please summarize the following news article in a structured, informative, and human-friendly format:

1. **Headline Summary** – What is the article mainly about?
2. **Key Highlights** – 3 to 5 major points with context.
3. **Insights & Implications** – Why does this matter? Who is affected?

Here is the article content:
{text}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Failed to summarize: {e}"

def translate_summary(text, target_language):
    lang_code = lang_map.get(target_language)
    if not lang_code:
        return "⚠️ Unsupported language."
    prompt = f"""
Translate the following summary into {target_language} ({lang_code}) while keeping the structure and formatting intact.

{text}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Failed to translate: {e}"

# --------------------------- NewsAPI ---------------------------
def fetch_articles(query, country, from_date, to_date, sort_by="publishedAt"):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "to": to_date,
        "sortBy": sort_by,
        "pageSize": 10,
        "language": "en",
        "apiKey": NEWSAPI_KEY,
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("articles", []) if data.get("status") == "ok" else []

def fetch_trending_articles(country="us"):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": country,
        "pageSize": 10,
        "language": "en",
        "apiKey": NEWSAPI_KEY,
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("articles", []) if data.get("status") == "ok" else []

def display_image_safe(url):
    if url and isinstance(url, str) and url.startswith("http"):
        st.image(url, width=180)
    else:
        st.image("https://via.placeholder.com/180x100?text=No+Image", width=180)

# --------------------------- Streamlit UI ---------------------------
st.set_page_config(page_title="AI News Summarizer", layout="wide")
st.title("🗞️NewsInsight")

# --- Filters in a single row ---
col1, col2, col3 = st.columns([3, 1, 2])
with col1:
    query_input = st.text_input("Search", placeholder="Search for topics like 'AI regulation', 'tech layoffs'...")
with col2:
    country = st.selectbox("Country", ["us", "in", "gb", "au", "ca"], index=0)
with col3:
    from_date, to_date = st.date_input("Date Range", [date.today(), date.today()])

# --- Search Button ---
if st.button("Apply Filters"):
    with st.spinner("Fetching articles..."):
        st.session_state.articles = fetch_articles(query_input, country, from_date, to_date)
        st.session_state.searched = True

# --- URL Summarizer (Enter to trigger) ---
url_input = st.text_input(
    "Paste article URL to summarize",
    placeholder="https://www.example.com/news/article"
)
if url_input.strip():
    with st.spinner("Summarizing the article..."):
        scraped_text = extract_text_with_bs4(url_input)
        summary = summarize_text(scraped_text)
        st.session_state.url_summary = summary

# --- Display URL Summary ---
if "url_summary" in st.session_state:
    st.subheader("📝 Summary:")
    st.markdown(st.session_state.url_summary)

    with st.expander("🌍 Translate Summary"):
        selected_lang = st.selectbox("Choose Language", list(lang_map.keys()), key="lang_url")
        if st.button("Translate Summary", key="translate_url"):
            with st.spinner(f"Translating to {selected_lang}..."):
                translated = translate_summary(st.session_state.url_summary, selected_lang)
            st.subheader(f"🗣️ Summary in {selected_lang}:")
            st.markdown(translated)

# --- Trending News ---
if not st.session_state.get("searched"):
    st.markdown("### 📈 Trending News")
    trending_articles = fetch_trending_articles(country)
    for i, article in enumerate(trending_articles):
        st.markdown("---")
        with st.container():
            col_img, col_text = st.columns([1, 3])
            with col_img:
                display_image_safe(article.get("urlToImage"))
            with col_text:
                st.subheader(article["title"])
                st.caption(f"📰 {article['source']['name']} | Date: {article['publishedAt'][:10]}")
                st.markdown(f"[Read Full Article]({article['url']})")

                if st.button("Summarize this Article", key=f"trend_btn_{i}"):
                    with st.spinner("Extracting article..."):
                        content = extract_article_text_newspaper(article['url'])
                    with st.spinner("Generating summary..."):
                        summary = summarize_text(content)
                        st.session_state[f"trend_summary_{i}"] = summary

                if f"trend_summary_{i}" in st.session_state:
                    st.subheader("📝 Summary:")
                    st.markdown(st.session_state[f"trend_summary_{i}"])

                    with st.expander("🌍 Translate Summary"):
                        selected_lang = st.selectbox("Choose Language", list(lang_map.keys()), key=f"trend_lang_{i}")
                        if st.button("Translate Summary", key=f"translate_trend_{i}"):
                            with st.spinner(f"Translating to {selected_lang}..."):
                                translated = translate_summary(st.session_state[f"trend_summary_{i}"], selected_lang)
                            st.subheader(f"🗣️ Summary in {selected_lang}:")
                            st.markdown(translated)

# --- Search Results ---
if st.session_state.get("searched"):
    st.markdown("### 🔍 Search Results")
    articles = st.session_state.get("articles", [])
    if not articles:
        st.warning("No articles found. Try a different keyword or date range.")
    else:
        for i, article in enumerate(articles):
            st.markdown("---")
            with st.container():
                col_img, col_text = st.columns([1, 3])
                with col_img:
                    display_image_safe(article.get("urlToImage"))
                with col_text:
                    st.subheader(article["title"])
                    st.caption(f"📰 {article['source']['name']} | Date: {article['publishedAt'][:10]}")
                    st.markdown(f"[Read Full Article]({article['url']})")

                    if st.button("Summarize this Article", key=f"search_btn_{i}"):
                        with st.spinner("Extracting article..."):
                            content = extract_article_text_newspaper(article['url'])
                        with st.spinner("Generating summary..."):
                            summary = summarize_text(content)
                            st.session_state[f"search_summary_{i}"] = summary

                    if f"search_summary_{i}" in st.session_state:
                        st.subheader("📝 Summary:")
                        st.markdown(st.session_state[f"search_summary_{i}"])

                        with st.expander("🌍 Translate Summary"):
                            selected_lang = st.selectbox("Choose Language", list(lang_map.keys()), key=f"search_lang_{i}")
                            if st.button("Translate Summary", key=f"translate_search_{i}"):
                                with st.spinner(f"Translating to {selected_lang}..."):
                                    translated = translate_summary(st.session_state[f"search_summary_{i}"], selected_lang)
                                st.subheader(f"🗣️ Summary in {selected_lang}:")
                                st.markdown(translated)
