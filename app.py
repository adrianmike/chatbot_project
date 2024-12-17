from flask import Flask, render_template, request, jsonify
import mysql.connector
import logging
from fuzzywuzzy import process
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import sqlparse
from sqlparse.tokens import Keyword, DML
import random
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    filename='chatbot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add NLTK data path (adjust if necessary)
nltk.data.path.append('/home/adrian/nltk_data')
logging.debug("NLTK data path set.")

# Preprocessing function
def preprocess_input(user_input):
    logging.debug(f"Preprocessing input: {user_input}")
    user_input = user_input.lower()
    user_input = user_input.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(user_input)
    filtered_tokens = [word for word in tokens if word not in stopwords.words('english')]
    processed = ' '.join(filtered_tokens)
    logging.debug(f"Filtered tokens: {filtered_tokens}")
    return processed

# Connect to the database
def connect_to_db():
    try:
        logging.debug("Attempting to connect to the database.")
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
    logging.debug("Fetching all questions from the database.")
    conn = connect_to_db()
    if not conn:
        logging.error("Failed to connect to the database while fetching questions.")
        return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT question FROM sample_data")
        questions = [row[0] for row in cursor.fetchall()]
        logging.debug(f"Questions fetched: {questions}")
        return questions
    except mysql.connector.Error as err:
        logging.error(f"Error fetching questions: {err}")
        return []
    finally:
        cursor.close()
        conn.close()
        logging.debug("Database connection closed after fetching questions.")

# Get tutorial based on the topic
def get_tutorial(topic):
    conn = connect_to_db()
    if not conn:
        return "Sorry, I'm having trouble connecting to the database."

    cursor = conn.cursor()
    try:
        query = "SELECT Content FROM tutorials WHERE Topic = %s"
        cursor.execute(query, (topic,))
        result = cursor.fetchone()
        return result[0] if result else f"Sorry, I don't have a tutorial for the topic '{topic}'."
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return "Sorry, an error occurred while fetching the tutorial."
    finally:
        cursor.close()
        conn.close()

# Get scenario
def get_scenario():
    conn = connect_to_db()
    if not conn:
        return "Sorry, I'm having trouble connecting to the database."

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, description, dataset_link FROM scenarios ORDER BY RAND() LIMIT 1")
        result = cursor.fetchone()
        if result:
            return f"Scenario #{result['id']}: {result['description']}\nDataset: {result['dataset_link']}"
        else:
            return "Sorry, no scenarios are available at the moment."
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return "Sorry, an error occurred while fetching the scenario."
    finally:
        cursor.close()
        conn.close()

# Get response from the chatbot
def get_response(user_input):
    logging.debug(f"Received user input: {user_input}")
    conn = connect_to_db()
    if not conn:
        return "Sorry, I'm having trouble connecting to the database."

    cursor = conn.cursor()
    try:
        questions = get_all_questions()
        if not questions:
            logging.warning("No questions found in the database.")
            return "Sorry, I don't have any answers right now."

        processed_input = preprocess_input(user_input)
        logging.debug(f"Processed input for matching: {processed_input}")

        best_match, confidence = process.extractOne(processed_input, questions)
        logging.debug(f"Best match: {best_match}, Confidence: {confidence}")

        if confidence >= 70:
            query = "SELECT answer FROM sample_data WHERE question = %s"
            cursor.execute(query, (best_match,))
            result = cursor.fetchone()

            # Ensure all results are consumed to avoid "Unread result found" error
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
        logging.debug("Database connection closed after getting response.")



# Flask routes
@app.route('/')
def home():
    logging.debug("Home route accessed.")
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    logging.debug("Ask route accessed.")
    user_input = request.json.get('question')
    logging.debug(f"User question received via /ask endpoint: {user_input}")
    response = get_response(user_input)
    logging.debug(f"Response to be sent: {response}")
    return jsonify({'response': response})

# Debug endpoint to test database connection
@app.route('/debug_db')
def debug_db():
    conn = connect_to_db()
    if conn:
        return jsonify({"status": "success", "message": "Database connection successful!"})
    else:
        return jsonify({"status": "error", "message": "Database connection failed!"})

# Run Flask app
if __name__ == '__main__':
    logging.debug("Starting Flask app.")
    app.run(host='0.0.0.0', port=5000, debug=True)
