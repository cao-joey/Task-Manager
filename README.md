# Task-Manager
This is a simple web-based to-do list application that can support multiple users. Each user is able to register, login, create and manage their own list of personal tasks.

## Installation
Before you run this project, be sure to install all required packages:
```
pip install flask flask-sqlalchemy flask-login
```
Additionally, in `taskapp.py` make sure to change this line:
app.config['SECRET_KEY'] = 'some key here'
To another secure random key. You can generate this by running:
```
import secrets
print(secrets.token_hex(16)
```
Or just choose your own.

## Running the Application
To run the application:
```
python taskapp.py
```
Or you can use `python3`.
Then start the server by opening `https://127.0.0.1:5000` on a web broswer. 
