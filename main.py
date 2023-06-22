# first, go to Secrets and add an environmental variable called OPENAI_KEY with your OpenAI API key
from flask import Flask, render_template, url_for
import os
import time
import openai
import threading
import json
import random
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_KEY')

# Load the list of pages from a file at startup
try:
    with open('pages.json', 'r') as f:
        pages = json.load(f)
except FileNotFoundError:
    pages = []

def generate_content():
    # Select a topic
    topic = "traveling in Asia"

    # Generate a title
    title_response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Write a creative fun title for a blog article about a specific instance of " + topic,
        max_tokens=40,
        temperature=0.9
    )
    
    title = title_response.choices[0].text.strip()

    # Given the title, generate the text.
    content_response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a very creative and prolific blogger."},
        {"role": "user", "content": f"Print out a creative blog article based on the title: '{title}'."}
      ],
        max_tokens=600,
        temperature=0.7
    )

    content = content_response.choices[0].message.content.strip()
    
    return title, content

def create_html():
    with app.app_context():
        title, content = generate_content()
        description = content[:150]

        # Hardcode in keywords or use a GPT prompt to auto-generate keywords for your article!
        keywords = f"travel, asia, traveling, tourism"  # Example keywords from the page content
        
        timestamp = int(time.time())
        filename = f'generated_{timestamp}.html'
        with open(f'static/{filename}', 'w') as f:
            f.write(f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>{title}</title>
                <link rel="stylesheet" href="/static/styles.css">
                <meta name="viewport" content="width=device-width, initial-scale=1"> 
                <meta name="description" content="{description}">
                <meta name="keywords" content="{keywords}">
            </head>
            <body>
                <h1>{title}</h1>
                <pre>{content}</pre>
                <p><a href="/">Back to home</a></p>
            </body>
            </html>
            ''')
        pages.append({'filename': filename, 'title': title})
        # keeps the number of pages at 100. if you want more than 100, remove this if statement.
        if len(pages) > 100:
            oldest_page = pages.pop(0)  # Remove from list
            os.remove(f'static/{oldest_page["filename"]}')  # Delete file
        # Save the list of pages to a file every time it's updated
        with open('pages.json', 'w') as f:
            json.dump(pages, f)

@app.route('/')
def home():
    return render_template('index.html', pages=pages[::-1])

def run():
    while True:
        create_html()
        time.sleep(50)

if __name__ == '__main__':
    threading.Thread(target=run).start()
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))
