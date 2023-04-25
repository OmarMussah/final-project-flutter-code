import os
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import functions_framework

cred = credentials.Certificate('omarfinal.json')
default_app = initialize_app(cred)
db = firestore.client()
app = Flask(__name__)
students_ref = db.collection('students')
posts_ref = db.collection('posts')
CORS(app)




@app.route('/login', methods=['POST'])
def login():
    # Get the request data
    data = request.get_json()

    # Find the user with the given email and id
    query = students_ref.where('email', '==', data['email']).where('id', '==', data['id']).get()

    # If the user doesn't exist, return an error
    if len(query) == 0:
        return jsonify({'error': 'Invalid email or ID.'}), 400

    # If the user exists, return their profile information
    else:
        user = query[0].to_dict()
        return jsonify(user)





@app.route('/students', methods=['POST'])
def create_student():
    # Get the request data
    data = request.get_json()

    # Check if the id or email already exist in the database
    id_query = students_ref.where('id', '==', data['id']).get()
    email_query = students_ref.where('email', '==', data['email']).get()

    if id_query or email_query:
        return jsonify({'error': 'Student with that id or email already exists.'})

    # Create a new student document with only the allowed fields
    new_student = {
        'id': data['id'],
        'name': data['name'],
        'email': data['email'],
        'date_of_birth': data['date_of_birth'],
        'year_group': data['year_group'],
        'major': data['major'],
        'campus_residence': data['campus_residence'],
        'best_food': data['best_food'],
        'best_movie': data['best_movie']
    }

    students_ref.add(new_student)

    return jsonify({'message': 'Student created successfully.'})



# Endpoint for retrieving a student profile by name
# @app.route('/students/<string:name>', methods=['GET'])
# def get_student(name):
#     query = students_ref.where('name', '==', name).get()
#     student = query[0].to_dict()
#     return jsonify(student)
@app.route('/students', methods=['GET'])
def get_student():
    # Get the request data
    data = request.get_json()

    # Retrieve the student document by name
    query = students_ref.where('id', '==', data['id']).get()
    
    # If the student exists, return it as a JSON object
    if query:
        student = query[0].to_dict()
        return jsonify(student)
    
    # Otherwise, return an error message
    else:
        return jsonify({'error': 'Student not found.'}), 404




@app.route('/students_update', methods=['PATCH'])
def update_student():
    # Get the student data to be updated from the request body
    student_data = request.get_json()

    # Get the existing student data from the database based on the student ID
    query = students_ref.where('id', '==', student_data['id']).get()
    if len(query) == 0:
        return jsonify({'error': 'Student not found.'}), 404
    student = query[0].to_dict()

    # Update the fields that are provided in the request body
    for field, value in student_data.items():
        if field not in ('name', 'email', 'id'):
            student[field] = value

    # Validate that the email id and name fields are not being modified
    if 'email' in student_data and student_data['email'] != student['email']:
        return jsonify({'error': 'Cannot modify email field.'}), 400
    
    if 'id' in student_data and student_data['id'] != student['id']:
        return jsonify({'error': 'Cannot modify student ID field.'}), 400
    
    if 'name' in student_data and student_data['name'] != student['name']:
        return jsonify({'error': 'Cannot modify name field.'}), 400

    # Update the student data in the database
    students_ref.document(query[0].id).update(student)
    return jsonify({'message': 'Student updated successfully.'})



posts = posts_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()

# Endpoint for creating a new post
@app.route('/create_post', methods=['POST'])
def create_post():
    # Get the author and content from the request body
    author = request.json.get('author')
    content = request.json.get('content')

    # Create a new post document in Firestore
    new_post = dict()
    new_post['author'] = author
    new_post['content'] = content
    new_post['timestamp'] = datetime.now()

    posts_ref.add(new_post)

    # Add the new post to the posts list
    # new_post_id = doc_ref[1].id
    # new_post['id'] = new_post_id

    # Send the new post to the client
    return new_post


# Endpoint for getting all posts
@app.route('/posts', methods=['GET'])
def get_posts():
    # Query the posts from the Firestore database
    posts = posts_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()

    # Convert each post document to a dictionary
    all_posts = [post.to_dict() for post in posts]

    # Return the posts to the client
    return jsonify(all_posts)


app.run(debug=True)
