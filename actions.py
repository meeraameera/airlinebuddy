import mysql.connector
import requests
import ollama
from typing import Any, Text, Dict, List
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk import Tracker

# Create a connection to the MySQL database
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  
            user="root",       
            password="TPG158410@#&", 
            database="airline_reviews"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None  # Return None if connection fails
    

class ActionReviewSummary(Action):

    def name(self) -> Text:
        return "action_review_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Retrieve slot values
        airline = tracker.get_slot('airline')
        rating = tracker.get_slot('rating')
        review = tracker.get_slot('review')

        # Debugging: Print retrieved values
        print(f"DEBUG: Airline={airline}, Rating={rating}, Review={review}")

        # Ensure the airline slot is not empty or just whitespace
        if not airline or airline.strip() == '':
            dispatcher.utter_message(text="The airline name cannot be empty. Please enter the airline that you would like to leave a review for again.")
            return []

        # Ensure rating is not None or empty
        if not rating or rating.strip() == '':
            dispatcher.utter_message(text="The rating cannot be empty. Please provide a valid rating between 1 and 5.")
            return []

        # Try to convert rating to a float and check if it's a valid number
        try:
            rating_value = float(rating.strip())
        except ValueError:
            dispatcher.utter_message(text="Invalid rating format. Please enter a valid number between 1 and 5.")
            return []

        # Ensure rating is within the range of 1 to 5
        if not (1 <= rating_value <= 5):
            dispatcher.utter_message(text="Rating must be between 1 and 5. Please enter a valid rating.")
            return []
        
        # Ensure the review slot is not empty or just whitespace
        if not review or review.strip() == '':
            dispatcher.utter_message(text="The review cannot be empty. Please provide your review.")
            return []

        # Handle long review text by truncating to 1000 characters 
        MAX_REVIEW_LENGTH = 1000
        if len(review) > MAX_REVIEW_LENGTH:
            review = review[:MAX_REVIEW_LENGTH]
            print(f"DEBUG: Review truncated to {MAX_REVIEW_LENGTH} characters.")

        # Connect to MySQL
        connection = create_db_connection()
        if connection is None:
            dispatcher.utter_message(text="Database connection failed. Please try again later.")
            return []

        try:
            cursor = connection.cursor(buffered=True)  # Use buffered cursor

            # SQL query to insert the review into the reviews table
            sql_query = "INSERT INTO reviews (airline, rating, review) VALUES (%s, %s, %s)"
            cursor.execute(sql_query, (airline, rating, review))

            connection.commit()  # Ensure data is saved

            print("DEBUG: Data inserted successfully into MySQL")  # Debugging confirmation

            # Summary message
            summary_message = (
                f"Here’s a summary:\n"
                f"- Airline: {airline}\n"
                f"- Rating: {rating}/5\n"
                f"- Review: {review}\n"
                f"Your review has successfully been submitted!\n"
                f"Would you like to leave another review?\n"
            )

        except mysql.connector.Error as err:
            print(f"Database Insertion Error: {err}")  # Debugging print
            summary_message = "There was an issue saving your review. Please try again."

        finally:
            cursor.close()
            connection.close()

        # Send the summary to the user
        dispatcher.utter_message(text=summary_message)

        return []


class ActionFetchAnswer(Action):
    def name(self) -> str:
        return "action_fetch_answer"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        query = tracker.latest_message.get("text")  # Get user query
        google_api_key = "AIzaSyBjvAA6-mGumNJ0dtriS4XXIbPj5Gn0cYA"
        search_engine_id = "6000a65278f5a4295"

        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={google_api_key}&cx={search_engine_id}"
        response = requests.get(url).json()

        # Fallback for no search results
        if "items" in response:
            results = response["items"][:2]  # Only take 2 results to reduce memory load
            raw_text = "\n".join([f"{item['title']}: {item['snippet']}" for item in results])
            raw_text = raw_text[:1000]  # Limit text to 1000 characters to reduce processing load

            # Use Ollama RAG to summarize & enhance response
            rag_response = ollama.chat(
                model="gemma:2b",  # Use the Gemma model
                messages=[{"role": "system", "content": "Summarize the following airline information in a user-friendly format:"},
                          {"role": "user", "content": raw_text}]
            )

            try:
                final_message = rag_response['message']['content']
            except KeyError:
                final_message = "Unable to retrieve an answer at the moment."

        else:
            final_message = "Sorry, I couldn't find the relevant answers."

        # Fallback for API failure
        if not final_message:
            final_message = "Sorry, there was an issue retrieving the airline information. Please try again later."

        dispatcher.utter_message(text=final_message)
        return []