from requests import get
from flask import redirect, url_for
from cs50 import SQL
import uuid

# Function to generate an image based on a prompt description
def generate_image(prompt_description, client, user_id,  db, image_queue):
    try:
        # Generate an image using the OpenAI API
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_description,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # Get the URL of the generated image
        image_url = response.data[0].url
        # Download the image
        response = get(image_url)

        # If the image was downloaded successfully
        if response.status_code == 200:
            # Get the image data
            image_data = response.content
            # Generate a unique ID for the image
            image_id = str(uuid.uuid4())
            # Define the path where the image will be saved
            image_path = f"static/{image_id}.png"

            # Save the image data to a file
            with open(image_path, "wb") as file:
                file.write(image_data)

            # Insert the image data into the database
            db.execute(
                "INSERT INTO images (prompt, image_data, user_id) VALUES (?, ?, ?)",
                prompt_description, image_data, user_id
            )
            # Add the image path to the image queue
            image_queue.put(image_path)
            # Return the image path
            return image_path
        else:
            # If the image was not downloaded successfully, return None
            return None
    except Exception as e:
        # If an error occurred, print the error and return None
        print(f"Error in generate_image: {str(e)}")
        return None
