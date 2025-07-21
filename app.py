from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util
from utils import load_documents

app = Flask(__name__)

# Load and preprocess documents
docs, filenames = load_documents()

# Load Sentence Transformer model
print("🧠 Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
doc_embeddings = model.encode(docs, convert_to_tensor=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ""

    if request.method == 'POST':
        query = request.form['query']
        query_embedding = model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, doc_embeddings)[0]
        ranked = zip(filenames, docs, scores)

        results = []
        for name, content, score in ranked:
            score_float = float(score)
            if score_float > 0:
                # Generate snippet
                sentences = content.split(".")
                snippet = sentences[0] if sentences else content[:120]
                results.append({
                    "filename": name,
                    "score": round(score_float * 100, 2),
                    "snippet": snippet.strip()
                })

        results = sorted(results, key=lambda x: x["score"], reverse=True)

    return render_template('index.html', results=results, query=query)

if __name__ == '__main__':
    print("🚀 Starting Flask server with semantic search and snippet previews...")
    app.run(debug=True)
