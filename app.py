from flask import Flask, request, jsonify
import re
from db_connection import get_db_connection

app = Flask(__name__)


# Extragerea cuvintelor-cheie folosind regex
def parse_question(question):
    question = question.lower()

    if re.search(r"cele mai vândute produse", question):
        return "vandute"
    elif re.search(r"produse în categoria (.*)", question):
        match = re.search(r"categoria (.*)", question)
        return "categorie", match.group(1)
    elif re.search(r"prețul produsului (.*)", question):
        match = re.search(r"produsului (.*)", question)
        return "pret", match.group(1)
    else:
        return None


# Funcție pentru interogarea bazei de date
def execute_query(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result


# Răspunsuri chatbot
def get_chatbot_response(question):
    parsed = parse_question(question)

    if parsed == "vandute":
        query = "SELECT nume, vandute FROM produse ORDER BY vandute DESC LIMIT 5"
        result = execute_query(query)
        return result
    elif parsed and parsed[0] == "categorie":
        query = "SELECT nume FROM produse WHERE categorie = %s"
        result = execute_query(query, (parsed[1],))
        return result
    elif parsed and parsed[0] == "pret":
        query = "SELECT pret FROM produse WHERE nume = %s"
        result = execute_query(query, (parsed[1],))
        return result
    else:
        return "Îmi pare rău, nu pot răspunde la această întrebare."


# Endpoint pentru chatbot
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get("question")
    response = get_chatbot_response(question)
    return jsonify(response)

@app.route('/chat', methods=['POST'])
def chat_v2():
    data = request.json
    question = data.get("question")
    print(f"Received question: {question}")  # Adaugă această linie
    response = get_chatbot_response(question)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
