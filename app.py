from flask import Flask, request, render_template
import os
import time
import urllib.parse
from dotenv import load_dotenv
import openai
from GoogleNews import GoogleNews
from newspaper import Article

# Load environment variables and set the OpenAI API key.
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

def clean_url(url):
    """
    Remove extraneous query parameters (like 'ved', 'usg', 'amp', etc.)
    that might interfere with downloading the article.
    """
    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed.query)
    # Remove unwanted parameters
    for key in ['ved', 'usg', 'amp']:
        query_params.pop(key, None)
    new_query = urllib.parse.urlencode(query_params, doseq=True)
    cleaned_url = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    return cleaned_url

def fetch_articles(topic, num_articles=10):
    """
    Uses GoogleNews to search for articles on the given topic from the past year.
    Returns a list of up to num_articles URLs.
    """
    googlenews = GoogleNews(period='1y')
    googlenews.search(topic)
    results = googlenews.results()
    
    seen = set()
    article_urls = []
    for result in results:
        url = result.get('link')
        if url and url not in seen:
            seen.add(url)
            article_urls.append(url)
        if len(article_urls) >= num_articles:
            break
    return article_urls

def extract_article_text(url):
    """
    Attempts to download and parse an article using newspaper3k.
    Returns the article text if successful, otherwise returns None.
    """
    try:
        cleaned_url = clean_url(url)
        article = Article(cleaned_url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error extracting article from {url}: {e}")
        return None

def generate_post_text(topic, audience, style):
    """
    Fetches articles and calls the OpenAI API to generate a post.
    Returns a dictionary containing the generated post and metadata.
    """
    style_mapping = {
        "1": "easy to read",
        "2": "exciting read",
        "3": "technical read",
        "4": "marketing purpose",
        "5": "upskilling"
    }
    style_text = style_mapping.get(str(style), "easy to read")
    
    print("Fetching articles...")
    article_urls = fetch_articles(topic, num_articles=10)
    articles_text_list = []
    for url in article_urls:
        print(f"Processing article: {url}")
        text = extract_article_text(url)
        if text and text.strip():
            articles_text_list.append(text)
        else:
            print(f"Skipping article {url} due to no extractable text.")

    if articles_text_list:
        aggregated_articles_text = "\n\n".join(articles_text_list)
        prompt = f"""
You are an expert content creator. Based on the following aggregated article texts:

{aggregated_articles_text}

Generate an HTML formatted post on the topic "{topic}" tailored for the audience "{audience}" in a style that is "{style_text}". Follow these guidelines:
- For "easy to read": Ensure the post can be read in about 10 minutes.
- For "exciting read": Highlight the opportunities and potential the articles present.
- For "technical read": Use precise technical language and include mathematical descriptions where applicable.
- For "marketing purpose": Write in a persuasive tone that positions the author as the first point of contact.
- For "upskilling": Adopt an educational tone that informs and teaches.

Please produce the final post as HTML formatted text.
"""
    else:
        print("No article text could be extracted. Using fallback prompt.")
        prompt = f"""
You are an expert content creator. Using your expertise, generate an HTML formatted post on the topic "{topic}" tailored for the audience "{audience}" in a style that is "{style_text}". Please include background, insights, and recommendations based solely on the topic.
"""

    print("Generating post via OpenAI...")
    start_time = time.time()
    response = openai.ChatCompletion.create(
        model="o1-2024-12-17",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    end_time = time.time()
    inference_time = end_time - start_time

    post_content = response['choices'][0]['message']['content']
    usage = response.get('usage', {})
    input_tokens = usage.get('prompt_tokens', 0)
    output_tokens = usage.get('completion_tokens', 0)

    output_data = {
        "topic": topic,
        "audience": audience,
        "style": style_text,
        "post": post_content,
        "output token used": output_tokens,
        "input token used": input_tokens,
        "inference time": inference_time
    }
    
    # Print the output details to the terminal.
    print("\nFinal Output:")
    print(output_data)
    
    return output_data

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Read form data.
        topic = request.form.get("topic")
        audience = request.form.get("audience")
        style = request.form.get("style")
        
        # Generate the post.
        output_data = generate_post_text(topic, audience, style)
        # Pass the generated post and metadata to the template.
        return render_template("index.html", output=output_data, topic=topic, audience=audience, style=style)
    
    # GET request: render the form.
    return render_template("index.html", output=None)

if __name__ == '__main__':
    # Change port to 8000
    app.run(debug=True, port=8000)
