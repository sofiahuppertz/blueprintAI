### AI Building Image Generator
#
#
Blueprint AI is a web application designed to generate building images based on user's answers(to a form). This project was developed as part of a final assignment for a CS50's Harvard online course.
#
### Core Features
#
**User Authentication** : Implementation of a login and registration system.
**Descriptive Input Form** : A form that collects user descriptions about a building's style, size, materials, etc.
**Image Generation** : Use of DALL-E 3 API to convert these descriptions into building images.
**Loading Page** : A temporary page displayed while the image is being generated, showcasing previously created images.
**Result Display** : Presentation of the generated building image on building.html.
#
### Technology Utilized
#
**Flask**
**SQLite3**
**HTML & Bootstrap**
**JavaScript**
**OpenAI API**
#
### Application Structure
#
**helpers.py**: Manages the `generate_image()` function for OpenAI API interactions and image generation.
**static/**: Stores generated images and static assets.
**templates/**: Contains HTML files like `index.html` (input form), `loading.html` (loading screen), and `building.html` (image display).
**app.py**: Handles core application logic, including route definitions for `index`, `login`, `register`, `logout`, `check_image`, and `building`. In `index`, it processes form responses to create a prompt with placeholders for `generate_image`.
#
### Workflow
#
**User Registration/Login**: Users can register for a new account or log into an existing one.
**Input Form Submission**: Users fill out a detailed form to describe the building they envision.
**Image Generation**: Based on the form responses, a prompt is created and passed to the `generate_image()` function in `helpers.py`. This function handles the interaction with the OpenAI API, downloading the generated image, and storing it in a specific path. It also inserts image data into the database and adds the image path to a queue for later retrieval.
**Loading Mechanism**: While the image is being processed, `loading.html` is displayed. This page shows a series of previously generated images in rotation and executes a script to periodically check the server for the new image's readiness.
**Displaying Results**: As soon as the new image is ready, users are automatically redirected to `building.html` to view it. This page also offers options to retake the quiz or to log out.
#
### Database Structure (`blueprintai.db`)
#
**Users Table**: Contains user IDs, names, and hashed passwords.
**Images Table**: Stores image prompts, binary image data, and user IDs linking images to users.
#
#
#### 