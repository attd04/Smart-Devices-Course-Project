import requests
import json
from flask import Flask, render_template_string, request
from bs4 import BeautifulSoup
import paho.mqtt.publish as publish
import urllib.parse

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Swear Words Censorship - Smart Devices Project</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        pre {
            background: #eee;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 300px;
            overflow-y: auto;
        }
        .section {
            margin-bottom: 30px;
        }
        .bad-word {
            color: #d90429;
            font-weight: bold;
        }
        .censored {
            color: #2b9348;
            font-weight: bold;
        }
        details {
            margin-top: 20px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Swear Words Censored from Wiktionary</h1>

        <div class="section">
            <h2>🔹 Censored Text:</h2>
            <pre class="censored">{{ censored_text }}</pre>
        </div>

        <div class="section">
            <h2>🔹 Original Scraped Text:</h2>
            <pre>{{ original_text }}</pre>
        </div>

        <div class="section">
            <h2>🔹 Bad Words Detected ({{ bad_words | length }})</h2>
            {% if bad_words %}
                <ul>
                    {% for word in bad_words %}
                        <li><span class="bad-word">{{ word.word }}</span> → <span class="censored">{{ '*' * word.replacedLen }}</span></li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>No bad words found 🎉</p>
            {% endif %}
        </div>

        {% if full_json %}
        <details>
            <summary>Show full API JSON response</summary>
            <pre>{{ full_json }}</pre>
        </details>
        {% endif %}
    </div>
</body>
</html>
'''

def scrape_swear_words(limit=20):
    url = "https://en.wiktionary.org/wiki/Category:English_swear_words"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    word_links = soup.select("div#mw-pages li a")
    swear_words = [link.text for link in word_links]
    return swear_words[:limit]  # Limit to 'limit' for readability


def censor_text_with_api(text):
    headers = {
        "apikey": "hjS94lyrrURYhuHA5iCY6xeqPoyssh3U",
        "Content-Type": "application/json"
    }
    payload = {"content": text}

    response = requests.post(
        "https://api.apilayer.com/bad_words",
        headers=headers,
        json=payload  # MUST use `json=payload` instead of `data=payload`
    )

    if response.status_code == 200:
        return response.json()
    else:
        print("API Error:", response.status_code, response.text)
        return {}



@app.route("/")
def index():
    words = scrape_swear_words(20)
    text = " ".join(words)
    censored_result = censor_text_with_api(text)

    with open("output.json", "w") as f:
        json.dump(censored_result, f, indent=4)

    publish.single(
        topic="smartdevices/jsondata",
        payload=json.dumps(censored_result),
        hostname="172.20.10.11",
        port=1883
    )

    censored_text = urllib.parse.unquote(censored_result.get("censored_content", ""))
    original_text = urllib.parse.unquote(censored_result.get("content", text))
    bad_words = censored_result.get("bad_words_list", [])

    return render_template_string(
        HTML_TEMPLATE,
        censored_text=censored_text,
        original_text=original_text,
        bad_words=bad_words,
        full_json=None
    )

@app.route("/detailed")
def detailed():
    words = scrape_swear_words(50)  # scrape more words here for a richer example
    text = " ".join(words)
    censored_result = censor_text_with_api(text)

    with open("output_detailed.json", "w") as f:
        json.dump(censored_result, f, indent=4)

    publish.single(
        topic="smartdevices/jsondata_detailed",
        payload=json.dumps(censored_result),
        hostname="172.20.10.11",
        port=1883
    )

    censored_text = urllib.parse.unquote(censored_result.get("censored_content", ""))
    original_text = urllib.parse.unquote(censored_result.get("content", text))
    bad_words = censored_result.get("bad_words_list", [])

    # Pass full json prettified for debug viewing
    full_json_pretty = json.dumps(censored_result, indent=4)

    return render_template_string(
        HTML_TEMPLATE,
        censored_text=censored_text,
        original_text=original_text,
        bad_words=bad_words,
        full_json=full_json_pretty
    )


@app.route("/custom", methods=["GET", "POST"])
def custom_input():
    censored_text = ""
    original_text = ""
    bad_words = []
    full_json_pretty = ""

    if request.method == "POST":
        input_text = request.form.get("input_text", "")
        result = censor_text_with_api(input_text)

        censored_text = urllib.parse.unquote(result.get("censored_content", ""))
        original_text = urllib.parse.unquote(result.get("content", input_text))
        bad_words = result.get("bad_words_list", [])
        full_json_pretty = json.dumps(result, indent=4)

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom Censorship</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0,0,0,0.1);
            }
            h1 {
                text-align: center;
            }
            textarea {
                width: 100%;
                height: 100px;
                padding: 10px;
                margin-bottom: 20px;
                font-size: 16px;
            }
            pre {
                background: #eee;
                padding: 15px;
                border-radius: 5px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .bad-word {
                color: #d90429;
                font-weight: bold;
            }
            .censored {
                color: #2b9348;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Custom Text Censorship</h1>
            <form method="POST">
                <textarea name="input_text" placeholder="Type your text here...">{{ request.form.get('input_text', '') }}</textarea>
                <br>
                <button type="submit">Censor Text</button>
            </form>

            {% if censored_text %}
                <h2>🔹 Censored Output:</h2>
                <pre class="censored">{{ censored_text }}</pre>
                <h2>🔹 Original Input:</h2>
                <pre>{{ original_text }}</pre>
                <h2>🔹 Bad Words Detected ({{ bad_words | length }})</h2>
                {% if bad_words %}
                    <ul>
                        {% for word in bad_words %}
                            <li><span class="bad-word">{{ word.word }}</span> → <span class="censored">{{ '*' * word.replacedLen }}</span></li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p>No bad words found 🎉</p>
                {% endif %}
                <details>
                    <summary>Full JSON Response</summary>
                    <pre>{{ full_json_pretty }}</pre>
                </details>
            {% endif %}
        </div>
    </body>
    </html>
    ''',
                                  censored_text=censored_text,
                                  original_text=original_text,
                                  bad_words=bad_words,
                                  full_json_pretty=full_json_pretty
                                  )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
