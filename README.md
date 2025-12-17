# Airline Buddy

A **conversational AI solution** designed for airlines to automate **review collection**, perform **sentiment analysis**, and provide **dynamic Q&A** using a **Retrieval-Augmented Generation (RAG)** approach.  

---

## Problem Statement

Airlines struggle to efficiently process the large volume of customer reviews and provide accurate, timely answers to complex service questions (e.g., baggage fees, rescheduling policies). Manual review is slow, and generic FAQ bots often fail to address specific queries, leading to frustrated customers and missed opportunities for service improvement.

---

## Project Goal

The goal of **AirlineBuddy** is to create a functional conversational AI system that:

1. **Automates Review Collection & Analysis:**  
   Provides a guided interface for customers to submit reviews, which are stored in a database for sentiment-based analysis.

2. **Provides Dynamic Q&A:**  
   Answers airline-related questions in real-time using **RAG**, ensuring responses reflect the latest external data.

---

## Dataset

Customer review text data sourced from public datasets:  
[Airline Quality Reviews](https://www.airlinequality.com)  

---

## Technical Approach

### Part A: Sentiment Analysis Model (`Project_Application_Part_1.ipynb`)

- **Data Collection:**  
  Collected customer reviews from the top 10 rated airlines in 2023.

- **Pre-processing & Labeling:**  
  - **Sentiment Labels:** Reviews labelled as `Positive`, `Negative`, or `Neutral`.  
  - **Text Cleaning:** Tokenization, Stopword Removal, Lemmatization.

- **Model Selection:**  
  - Evaluated models trained on unbalanced, balanced, and fine-tuned datasets.  
  - **Final Model:** Logistic Regression trained on a balanced dataset, generating metrics including Accuracy, Precision, Recall, F1-score, and a Confusion Matrix.

---

### Part B: Rasa Chatbot Implementation (`domain.yml`, `nlu.yml`, `rules.yml`, `stories.yml`, `actions.py`)

- **Dialogue Design:**  
  - Defined intents: `submit_review`, `ask_question`.  
  - Created multi-turn conversation flows (`stories.yml`) for review submission and Q&A.  
  - Defined entities (`airline`, `rating`, `review`) and slots (`domain.yml`) to capture key user information.

- **Review Submission Pipeline (`action_review_summary`):**  
  - Triggered after collecting airline, rating, and review.  
  - Connects to a **MySQL database** (`airline_reviews`).  
  - Validates inputs and stores review data.

- **RAG-Powered Q&A Pipeline (`action_fetch_answer`):**  
  - Triggered by `ask_question` intent.  
  - Uses **Google Custom Search API** to retrieve relevant data.  
  - Top 2 search snippets are fed into **Ollama RAG** (`Gemma:2b`) for response generation.  
  - Returns a concise, user-friendly answer.

---

## Key Challenges Faced

- **RAG Enhancement:**
  - Initial PDF reading for airline documents was unsuccessful.
  - Improving this pipeline would reduce reliance on external APIs.

---

## Installation & Execution

### Prerequisites

Ensure you have the following installed:

  - Python 3.8 - 3.10 (Required for Rasa compatibility)
  -  MySQL Server (To host the airline_reviews database)
  -  Ollama (Running locally with the gemma:2b model pulled)

### Steps

- Clone the repository
- Create and activate a virtual environment
- Install required dependencies
- Database Configuration
  - Open MySQL and create the database:
    - `CREATE DATABASE airline_reviews`
  - Update the credentials (user and password) in the create_db_connection() function within actions.py.
- Run the Action Server
  - `rasa run actions`
- Train the Model
  - `rasa train`
- Launch the Chatbot by opening a new terminal 
  - `rasa shell`
