# CycleSync-Backend
This repository contains the backend source code for the CycleSync fitness app project.

## Contents:

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)


## Project Overview

CycleSync is a menstrual cycle based workout tracking app built for weightlifting women who experience regular menstrual cycles.

This source code contains the project settings, model schema, and API for the app. 

This repository has been deployed to Railway.com via the URL: https://cyclesync-backend-production.up.railway.app/

The API endpoints, which are used by the frontend app, can be accessed via: https://cyclesync-backend-production.up.railway.app/api 

## Tech Stack

- **Python**  
- **Django**  
- **SQLite / PostgreSQL**  
- **Django REST Framework**  
- **CORS Headers**  
- **JWT Authentication**
- **Deployed via Railway**

## Setup Instructions

Please follow these instructions if you would like to setup the source code locally:

### 1. **Clone the Repository**


To get started, clone the repository to your local machine. Open your terminal or Git bash and change to the directory on your local machine where you would like to save the repository (using ```cd``` command) and run the following command:

``` git clone https://github.com/kdd333/CycleSync-Backend.git ```

For more help on cloning a repository, check out the following GitHub documentation: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository


After cloning successfully, move into the root directory by running the command:

``` cd CycleSync-Backend ```


### 2. Create and Activate a Conda Environment

Make sure you have Miniconda installed for this step. Follow these instructions on how to install Miniconda if you do not have it installed on your device: https://www.anaconda.com/docs/getting-started/miniconda/install


After installing Miniconda, create a new environment in your terminal by running the command: 

``` conda create --name cyclesync-env ```

Then activate it by running:

``` conda activate cyclesync-env ```


### 3. Install Dependencies

The next step after activating a virtual environment is to install the required python packaged used in this project by running:

``` pip install -r requirements.txt ```


### 4. Create Environment 

You will need to create an environment file to set important variables for the local environment. To get started on this, create a `.env` file:

``` echo. > .env ```

Then open the .env file in a text editor and add the following:

```
SECRET_KEY=cyclesync_backend_secret_key
DATABASE_URL=sqlite:///db.sqlite3
```

Make sure to save the `.env` file before moving on to the next step.


### 5. Run Database Migrations

Apply the Django migrations to set up the database schema:

``` python manage.py migrate ```


### 6. Run the Development Server

Start the Django development server by running the command:

``` python manage.py runserver ```

You will now be able to access the backend server at http://127.0.0.1:8000/ or http://localhost:8000/ (check the terminal logs after running the command for the exact URL).


### *Note

If you would like to view debugging logs, make sure to go to the `settings.py` file (located in the `cyclesync/` directory), and find the line that says `DEBUG = False` and set this to `true`.
