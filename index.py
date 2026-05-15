import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify , render_template , redirect , url_for , session
import chromadb
from flask_cors import CORS 
from werkzeug.security import generate_password_hash, check_password_hash



load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY")

users = {}

def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper

latest_response = None

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "Data")
OLLAMA_ORGANIZER_MODEL = os.getenv("OLLAMA_ORGANIZER_MODEL", "mistral")


chroma_client = chromadb.CloudClient(
    api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE")
)

collection = chroma_client.get_collection(name=CHROMA_COLLECTION)


import random

collection = chroma_client.get_collection(name=CHROMA_COLLECTION)


import random
from collections import defaultdict

def parse_prompt_metadata(user_prompt: str) -> dict:
    """
    Extrait thème et tranche d'âge depuis la requête pour guider le filtrage RAG.
    Léger : regex + mots-clés, sans appel LLM.
    """
    import re

    age_match = re.search(r"\b(\d{1,2})\s*(ans?|year)", user_prompt, re.IGNORECASE)
    age = int(age_match.group(1)) if age_match else None

    theme_keywords = {
        "tri": ["tri", "trier", "ordonner", "ordre"],
        "algorithme": ["algorithme", "algo", "étapes", "procédure"],
        "logique": ["logique", "vrai", "faux", "condition", "si"],
        "séquence": ["séquence", "suite", "ordre", "instruction"],
        "réseau": ["réseau", "communication", "message", "chemin"],
        "données": ["données", "information", "stocker", "fichier"],
    }

    detected_theme = None
    prompt_lower = user_prompt.lower()
    for theme, keywords in theme_keywords.items():
        if any(kw in prompt_lower for kw in keywords):
            detected_theme = theme
            break

    return {"theme": detected_theme, "age": age}

def retrieve_rag_context(user_prompt, n_results=5, theme_filter=None):
    total_docs = collection.count()
    if total_docs == 0:
        return "Aucun document pertinent trouvé dans la base RAG."

    # Fetch large pour avoir de la marge après filtrage
    fetch_count = min(n_results * 6, total_docs)

    results = collection.query(
        query_texts=[user_prompt],
        n_results=fetch_count,
        where={"theme": theme_filter} if theme_filter else None  # filtre ChromaDB natif
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return "Aucun document pertinent trouvé dans la base RAG."

    pool = list(zip(documents, metadatas, distances))

    # --- Diversification par thème : 1 doc par thème, puis complétion ---
    seen_themes = set()
    diverse = []
    remainder = []

    for doc, meta, dist in pool:
        theme = meta.get("theme", "inconnu")
        if theme not in seen_themes:
            seen_themes.add(theme)
            diverse.append((doc, meta, dist))
        else:
            remainder.append((doc, meta, dist))

    # Garde le meilleur doc (distance min) + diversifiés + shuffle du reste
    pool_sorted = sorted(pool, key=lambda x: x[2])
    top_one = [pool_sorted[0]]

    # Retire le top_one des diversifiés pour éviter doublon
    top_doc = top_one[0][0]
    diverse = [(d, m, dist) for d, m, dist in diverse if d != top_doc]

    random.shuffle(remainder)
    selected = top_one + diverse + remainder
    selected = selected[:n_results]

    return "\n\n---\n\n".join(doc for doc, _, _ in selected)

def ask_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()
    return response.json()["response"]

def generate_bebras_response(user_prompt, rag_context, history: list[str] = None):
    """
    history : liste des titres ou thèmes des activités déjà générées dans la session,
    pour forcer la variété inter-appels.
    """
    history_block = ""
    if history:
        history_block = f"""
Activités déjà proposées dans cette session (à NE PAS répéter ni paraphraser) :
{chr(10).join(f'- {h}' for h in history)}
"""

    final_prompt = f"""
Tu es un assistant pédagogique spécialisé dans l'éveil à la pensée informatique
pour l'enseignement primaire, inspiré des activités Bebras.

Besoin de l'enseignant :
{user_prompt}

Contexte RAG (activités similaires de référence) :
{rag_context}
{history_block}
Ta mission :
En te basant UNIQUEMENT sur le contexte RAG ci-dessus, génère une activité pédagogique
ORIGINALE et DIFFÉRENTE des précédentes. Varie le contexte narratif (animaux, cuisine,
jeux, voyage, nature…) et le mécanisme pédagogique (classement, élimination, chemin,
correspondance…).

L'activité doit obligatoirement suivre cette structure, dans cet ordre,
sans afficher les titres de section :

1. Le titre de l'activité (une ligne, accrocheur)
2. L'objectif pédagogique (1 à 2 phrases simples)
3. L'énoncé (une histoire courte, concrète et imagée qui pose le problème)
4. La question posée à l'élève (claire, directe, une seule question)
5. Les solutions possibles numérotées (3 à 4 choix plausibles maximum 4 options, sans révéler la bonne)
6. Une invitation finale : "À toi de réfléchir ! Quelle réponse choisis-tu ?"

Contraintes absolues :
- Ne jamais révéler la bonne réponse
- Pas de code, pas de termes techniques complexes
- Activité réalisable sans écran (papier, manipulation, dessin)
- Langage simple, accessible à un enfant de 6 à 12 ans
- Toujours en français
"""
    return ask_ollama(final_prompt)

def organize_activity(raw_response):
    organizer_prompt = f"""
Tu es un agent spécialisé dans l'organisation et la mise en forme d'activités pédagogiques.

Ta mission :
Transformer la réponse brute ci-dessous en une activité claire, lisible et bien structurée
pour une interface HTML.

Réponse brute :
{raw_response}

Règles absolues :
- N'inclure AUCUN titre de section dans la réponse (pas de "# Titre", "## Objectif", etc.)
- Ne jamais résoudre ou répondre à l'activité toi-même
- Corriger les fautes visibles sans changer le sens
- Garder le contenu pédagogique intact
- Toujours en langue Française

Structure du contenu à produire (sans les titres) :

1. Le nom de l'activité en première ligne, en gras

2. L'objectif pédagogique en une ou deux phrases simples

3. La mise en situation (contexte donné à l'élève)

4. La consigne claire pour l'élève

5. L'activité proposée (questions, exercices, tâches)

6. Les solutions possibles, numérotées :
   1. ...
   2. ...
   3. ...
   4. ...
   (Présenter les pistes/solutions sans les développer entièrement,
   laisser l'élève choisir et construire sa réponse / maximum 4 options )

7. Terminer par une invitation à l'étudiant, par exemple :
   "À toi de jouer ! Quelle approche choisis-tu ?"

"""
    return ask_ollama(organizer_prompt)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if email in users:
        return jsonify({
            "success": False,
            "error": "Cet email existe déjà"
        }), 400

    users[email] = {
        "username": username,
        "email" : email , 
        "password": generate_password_hash(password)
    }

    return jsonify({
        "success": True,
        "message": "Inscription réussie"
    }), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if email not in users:
        return jsonify({
            "success": False,
            "error": "Email introuvable"
        }), 404

    if not check_password_hash(users[email]["password"], password):
        return jsonify({
            "success": False,
            "error": "Mot de passe incorrect"
        }), 401

    session["user"] = users[email]

    return jsonify({
        "success": True,
        "message": "Connexion réussie"
    }), 200

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("auth")

@app.route("/")
@login_required
def index():
    return render_template("home.html",user=session["user"])

@app.route("/play")
@login_required
def Play():
    return render_template("index.html",user=session["user"])

@app.route("/auth")
def Auth_Template():
    return render_template("auth.html")


@app.route("/capture-prompt", methods=["GET"])
def capture_prompt():

    prompt = request.args.get("prompt")

    return jsonify({
        "status": "success",
        "prompt_received": prompt
    }), 200


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({
            "success": False,
            "error": "Le champ 'prompt' est obligatoire."
        }), 400

    user_prompt = data["prompt"]

    rag_context = retrieve_rag_context(user_prompt)

    response = generate_bebras_response(
        user_prompt=user_prompt,
        rag_context=rag_context
    )

    return jsonify({
        "success": True,
        "prompt": user_prompt,
        "response": response
    })

@app.route("/organize-response", methods=["POST"])
def organize_response():
    global latest_response

    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({
            "success": False,
            "error": "Le champ 'prompt' est obligatoire."
        }), 400

    raw_response = data["prompt"]

    organized_response = organize_activity(raw_response)

    latest_response = organized_response

    return jsonify({
        "success": True,
        "response": organized_response
    })


@app.route("/get-latest-response", methods=["GET"])
def get_latest_response():
    global latest_response

    if latest_response is None:
        return jsonify({
            "success": False,
            "message": "Aucune réponse disponible"
        }), 200

    response = latest_response

    return jsonify({
        "success": True,
        "response": response
    }), 200

latest_feedback = None

@app.route("/receive-feedback", methods=["POST"])
def receive_feedback():
    global latest_feedback

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Body JSON manquant"
        }), 400

    verdict = data.get("verdict")
    explication_pedagogique = data.get("explication_pedagogique")
    solution_detaillee = data.get("solution_detaillee")
    message_eleve = data.get("message_eleve")
    analyse_des_options = data.get("analyse_des_options")

    latest_feedback = {
        "verdict": verdict,
        "explication_pedagogique": explication_pedagogique,
        "solution_detaillee": solution_detaillee,
        "message_eleve": message_eleve,
        "analyse_des_options" : analyse_des_options
    }

    return jsonify({
        "success": True,
        "message": "Feedback reçu avec succès",
        "feedback": latest_feedback
    }), 200

@app.route("/get-latest-feedback", methods=["GET"])
def get_latest_feedback():
    global latest_feedback

    if latest_feedback is None:
        return jsonify({
            "success": False,
            "message": "Aucun feedback disponible"
        }), 200

    feedback = latest_feedback
    latest_feedback = None

    return jsonify({
        "success": True,
        "feedback": feedback
    }), 200


if __name__ == "__main__":
    app.run(debug=True)