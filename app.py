from flask import Flask, request, jsonify, render_template
import requests
import os
import json
from googlesearch import search

app = Flask(__name__)

# API KEY from Render Environment
API_KEY = os.getenv("OPENROUTER_API_KEY")

MEMORY_FILE = "memory.json"


# -------- MEMORY --------

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)


# -------- HOME --------

@app.route("/")
def home():
    return render_template("index.html")


# -------- CHAT API --------

@app.route("/chat", methods=["POST"])
def chat():

    user = request.json.get("message")

    memory = load_memory()

    messages = []

    for m in memory[-6:]:
        messages.append(m)

    messages.append({
        "role": "user",
        "content": user
    })

    # -------- GOOGLE SEARCH --------

    sources = []

    try:
        for url in search(user, num_results=3):
            sources.append(url)
    except:
        pass


    # -------- AI REQUEST --------

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ai-agent-xgf4.onrender.com",
        "X-Title": "AI Agent"
    }

    data = {
        "model": "google/gemma-7b-it",
        "messages": messages,
        "max_tokens": 1000
    }

    try:

        res = requests.post(url, headers=headers, json=data)

        response = res.json()

        print(response)  # debug log

        if "choices" in response:
            reply = response["choices"][0]["message"]["content"]
        else:
            reply = str(response)

    except Exception as e:

        reply = "Server error: " + str(e)


    # -------- SAVE MEMORY --------

    memory.append({
        "role": "user",
        "content": user
    })

    memory.append({
        "role": "assistant",
        "content": reply
    })

    save_memory(memory)

    return jsonify({
        "reply": reply,
        "sources": sources
    })


# -------- RUN --------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
