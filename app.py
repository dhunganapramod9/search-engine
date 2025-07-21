from flask import Flask, render_template, request, redirect, url_for, session
from sentence_transformers import SentenceTransformer, util
from utils import load_documents, extract_keywords, extract_text_from_file
import os

app = Flask(__name__)

# I’ve set a secret key for Flask session management (for history/favorites)
app.secret_key = "your_secret_key"

# This loads the existing .txt files from the documents/ folder
docs, filenames = load_documents()

# I’m using the all-MiniLM-L6-v2 model from Hugging Face for semantic embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Here I encode all the documents so I can compute similarity later
doc_embeddings = model.encode(docs, convert_to_tensor=True)

# I extract keywords from the entire corpus for suggestion display
keywords = extract_keywords(docs)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""
    answer = None

    # I use Flask sessions to store search history and favorites per user session
    if "history" not in session:
        session["history"] = []
    if "favorites" not in session:
        session["favorites"] = []

    # This is triggered when the user submits a search query
    if request.method == "POST":
        query = request.form["query"]
        session["history"].append(query)

        # I compute similarity between the query and all document vectors
        query_embedding = model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, doc_embeddings)[0]
        ranked = zip(filenames, docs, scores)

        # For each matching document, I extract the top sentence and its similarity score
        for name, content, score in ranked:
            score_val = float(score)
            if score_val > 0:
                snippet = content.split(".")[0]
                results.append({
                    "filename": name,
                    "score": round(score_val * 100, 2),
                    "snippet": snippet.strip()
                })

        # I sort the results by highest similarity score
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        # I optionally use OpenAI to return a smart answer to the query
        try:
            import openai
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            if openai.api_key:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": query}]
                )
                answer = response.choices[0].message.content.strip()
        except:
            answer = None

    # This returns the search results along with query, history, and favorites
    return render_template("index.html", results=results, query=query, answer=answer,
                           keywords=keywords, history=session["history"], favorites=session["favorites"])

@app.route("/document/<filename>")
def view_document(filename):
    # This route displays full content of a clicked document
    filepath = os.path.join("documents", filename)
    if not os.path.exists(filepath):
        return "File not found."
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return render_template("document.html", filename=filename, content=content)

@app.route("/upload", methods=["POST"])
def upload_file():
    # I allow the user to upload .txt, .pdf, or .docx files for dynamic search
    file = request.files["file"]
    if file:
        text = extract_text_from_file(file)
        filename = file.filename
        path = os.path.join("documents", filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        docs.append(text)
        filenames.append(filename)
        global doc_embeddings
        # After upload, I re-encode all docs to include the new one
        doc_embeddings = model.encode(docs, convert_to_tensor=True)
    return redirect(url_for("index"))

@app.route("/favorite/<filename>")
def favorite(filename):
    # This lets users mark documents as favorites
    if "favorites" not in session:
        session["favorites"] = []
    if filename not in session["favorites"]:
        session["favorites"].append(filename)
    return redirect(url_for("index"))

if __name__ == "__main__":
    # This starts the local server with debug mode for development
    app.run(debug=True)
