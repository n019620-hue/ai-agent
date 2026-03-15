from flask import Flask, request, jsonify, render_template
import requests
import os
import datetime
import json
from googlesearch import search

app = Flask(__name__)

API_KEY = "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"   # put your OpenRouter API key here

MEMORY_FILE = "memory.json"


# ---------------- MEMORY ----------------

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE,"r") as f:
            return json.load(f)
    return []

def save_memory(user,reply):

    memory = load_memory()

    memory.append({
        "user":user,
        "ai":reply
    })

    memory = memory[-10:]

    with open(MEMORY_FILE,"w") as f:
        json.dump(memory,f)


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- CHAT ----------------

@app.route("/chat",methods=["POST"])
def chat():

    user = request.json.get("message").lower()

    # TIME
    if "time" in user:
        now = datetime.datetime.now().strftime("%H:%M")
        return jsonify({"reply":"Current time is "+now})


    # CREATE FILE
    if "create file" in user:
        name=user.replace("create file","").strip()
        open(name,"w").close()
        return jsonify({"reply":"File created: "+name})


    # DELETE FILE
    if "delete file" in user:

        name=user.replace("delete file","").strip()

        if os.path.exists(name):
            os.remove(name)
            return jsonify({"reply":"File deleted"})
        else:
            return jsonify({"reply":"File not found"})


    # WIFI
    if "wifi on" in user:
        os.system("nmcli radio wifi on")
        return jsonify({"reply":"WiFi ON"})

    if "wifi off" in user:
        os.system("nmcli radio wifi off")
        return jsonify({"reply":"WiFi OFF"})


    # BLUETOOTH
    if "bluetooth on" in user:
        os.system("rfkill unblock bluetooth")
        return jsonify({"reply":"Bluetooth ON"})

    if "bluetooth off" in user:
        os.system("rfkill block bluetooth")
        return jsonify({"reply":"Bluetooth OFF"})


    # OPEN APP
    if "open firefox" in user:
        os.system("firefox &")
        return jsonify({"reply":"Opening Firefox"})


    # SYSTEM INFO
    if "system info" in user:
        info=os.popen("uname -a").read()
        return jsonify({"reply":info})


    # AUTO SEARCH
    links=""

    if "search" in user or "who is" in user or "what is" in user:

        try:
            results=list(search(user,num_results=3))

            for r in results:
                links += f'<a href="{r}" target="_blank">{r}</a><br>'
        except:
            pass


    # LOAD MEMORY
    memory = load_memory()

    messages=[{
        "role":"system",
        "content":"You are a helpful AI assistant running inside a personal AI agent."
    }]

    for m in memory:

        messages.append({
            "role":"user",
            "content":m["user"]
        })

        messages.append({
            "role":"assistant",
            "content":m["ai"]
        })


    messages.append({
        "role":"user",
        "content":user
    })


    url="https://openrouter.ai/api/v1/chat/completions"

    headers={
        "Authorization":f"Bearer {API_KEY}",
        "Content-Type":"application/json"
    }

    data={
        "model":"deepseek/deepseek-chat",
        "messages":messages
    }


    res=requests.post(url,headers=headers,json=data)

    reply=res.json()["choices"][0]["message"]["content"]

    save_memory(user,reply)

    reply = reply + "<br><br><b>Top sources:</b><br>" + links

    return jsonify({"reply":reply})


# ---------------- FILE UPLOAD ----------------

@app.route("/upload",methods=["POST"])
def upload():

    file=request.files["file"]

    content=file.read().decode("utf-8","ignore")

    text=content[:4000]

    url="https://openrouter.ai/api/v1/chat/completions"

    headers={
        "Authorization":f"Bearer {API_KEY}",
        "Content-Type":"application/json"
    }

    data={
        "model":"deepseek/deepseek-chat",
        "messages":[
            {"role":"system","content":"Summarize this file"},
            {"role":"user","content":text}
        ]
    }

    res=requests.post(url,headers=headers,json=data)

    reply=res.json()["choices"][0]["message"]["content"]

    return jsonify({"reply":reply})


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)
