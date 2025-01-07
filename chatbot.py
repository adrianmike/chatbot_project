#=======================================================================================
# prima varianta
# import mysql.connector

# Connect to the MySQL database
# def connect_to_db():
#     try:
#         conn = mysql.connector.connect(
#             host="localhost",
#             user="adrian",
#             password="Runceanu_123",
#             database="chatbot_db"
#         )
#         return conn
#     except mysql.connector.Error as err:
#         print(f"Error: {err}")
#         return None

# Function to fetch a response based on user input
# def get_response(question):
#     conn = connect_to_db()
#     if not conn:
#         return "Sorry, I'm having trouble connecting to the database."

#     cursor = conn.cursor()
#     try:
#         query = "SELECT answer FROM sample_data WHERE question = %s"
#         cursor.execute(query, (question,))
#         result = cursor.fetchone()
#         cursor.fetchall()  # Fetch any remaining results to clear the cursor
#         return result[0] if result else "Sorry, I don't know the answer to that."
#     except mysql.connector.Error as err:
#         return f"Database error: {err}"
#     finally:
#         cursor.close()
#         conn.close()


# Main chatbot loop
# def main():
#     print("Hello! Ask me a question (type 'exit' to quit).")
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() == 'exit':
#             print("Goodbye!")
#             break
#         response = get_response(user_input)
#         print(f"Bot: {response}")

# if __name__ == "__main__":
#     main()
#=======================================================================================


#=======================================================================================
# a doua varianta
import logging
import mysql.connector
import nltk
import os
import string
from fuzzywuzzy import process
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Step 2: Configure Logging
logging.basicConfig(
    filename='chatbot.log',          # Log file name
    level=logging.DEBUG,             # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log messages to console as well
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Add the NLTK data path explicitly
nltk.data.path.append('/home/adrian/nltk_data')

# Download necessary nltk data
nltk.download('punkt')
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Preprocessing function to clean user input
def preprocess_input(user_input):
    user_input = user_input.lower()
    user_input = user_input.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(user_input)
    filtered_tokens = [word for word in tokens if word not in stopwords.words('english')]
    return ' '.join(filtered_tokens)

# Connect to the MySQL database
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
        print(f"Error: {err}")
        return None

# Function to get all questions from the database
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

# Function to fetch a response based on fuzzy matching
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
            cursor.fetchall()  # Clear any remaining results
            logging.info(f"User question: '{user_input}' | Best match: '{best_match}' | Confidence: {confidence}")
            return result[0] if result else "Sorry, I don't know the answer to that."
        else:
            logging.info(f"No good match found for user question: '{user_input}'")
            return "Sorry, I don't know the answer to that."
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return "Sorry, there was a problem retrieving the answer."

    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return "Sorry, an unexpected error occurred."
    finally:
        cursor.close()
        conn.close()

# Main chatbot loop
def main():
    logging.info("Chatbot started.")
    print("Hello! Ask me a question (type 'exit' to quit).")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                logging.info("User exited the chatbot.")
                print("Goodbye!")
                break
            response = get_response(user_input)
            print(f"Asistent_virtual: {response}")
        except KeyboardInterrupt:
            logging.info("Chatbot interrupted by user (Ctrl+C).")
            print("\nGoodbye!")
            break
        except Exception as e:
            logging.exception(f"Error during main loop: {e}")
            print("An error occurred. Please try again.")

if __name__ == "__main__":
    main()
