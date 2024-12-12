from flask import Flask, render_template, request, jsonify
import mysql.connector
import logging
from fuzzywuzzy import process
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename='chatbot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add NLTK data path (adjust if necessary)
nltk.data.path.append('/home/adrian/nltk_data')

# Preprocessing function
def preprocess_input(user_input):
    user_input = user_input.lower()
    user_input = user_input.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(user_input)
    filtered_tokens = [word for word in tokens if word not in stopwords.words('english')]
    return ' '.join(filtered_tokens)

# Connect to the database
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="adrian",
            password="Runceanu_123",
            database="chatbot_db"
        )
        logging.info("Database connection successful.")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        return None

# Fetch all questions from the database
def get_all_questions():
    conn = connect_to_db()
    if not conn:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT question FROM sample_data")
        questions = [row[0] for row in cursor.fetchall()]
        return questions
    finally:
        cursor.close()
        conn.close()

# Get response from the chatbot
def get_response(user_input):
    conn = connect_to_db()
    if not conn:
        return "Sorry, I'm having trouble connecting to the database."

    cursor = conn.cursor()
    try:
        questions = get_all_questions()
        if not questions:
            logging.warning("No questions found in the database.")
            return "Sorry, I don't have any answers right now."

        best_match, confidence = process.extractOne(preprocess_input(user_input), questions)

        if confidence >= 70:
            query = "SELECT answer FROM sample_data WHERE question = %s"
            cursor.execute(query, (best_match,))
            result = cursor.fetchone()
            cursor.fetchall()
            logging.info(f"User question: '{user_input}' | Best match: '{best_match}' | Confidence: {confidence}")
            return result[0] if result else "Sorry, I don't know the answer to that."
        else:
            logging.info(f"No good match found for user question: '{user_input}'")
            return "Sorry, I don't know the answer to that."
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return "Sorry, there was a problem retrieving the answer."
    finally:
        cursor.close()
        conn.close()

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('question')
    response = get_response(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
