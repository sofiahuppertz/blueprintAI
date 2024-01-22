from requests import get
from cs50 import SQL
import sqlite3
import uuid



# Function to create tables3
def create_tables():
    conn = sqlite3.connect('blueprintai.db')
    cursor = conn.cursor()
    # Create 'users' table
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, hash TEXT)")
    # Create 'images' table
    cursor.execute("CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY AUTOINCREMENT, prompt TEXT NOT NULL, image_data BLOB NOT NULL, user_id INTEGER NOT NULL)")

    conn.commit()
    conn.close()
    return

# Function to generate an image based on a prompt description
def generate_image(prompt_description, client, session, image_queue):
    try:
        # Generate an image using the OpenAI API
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_description,
            size="1024x1024",
            quality="hd",
            n=1,
        )
        # Get the URL of the generated image
        image_url = response.data[0].url
        image_queue.put(image_url)
    except Exception as e:
        # If an error occurred, print the error and set image_url to None
        print(f"Error in generate_image: {str(e)}")
        
    return
    
def extract_information(text, client):
    template = "Your task is to extract relevant information in a "
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content