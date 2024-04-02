from flask import Flask, render_template, request, redirect, url_for
import base64
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Configure MongoDB connection
client = MongoClient('localhost', 27017)
db = client['image_database']
collection = db['images']

# Flask route
@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        
        image = request.files['image']
        if image.filename == '':
            return redirect(request.url)
        
        # Read additional parameters from the form
        quiz_name = request.form['quiz_name']
        score = request.form['score']
        description_line1 = request.form['description_line1']
        description_line2 = request.form['description_line2']
        
        # Read the image file and convert it to base64
        image_data = image.read()
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # Save the image data and additional parameters to MongoDB
        image_document = {
            'filename': image.filename,
            'data': base64_data,
            'quiz_name': quiz_name,
            'score': int(score),  # Convert score to integer
            'description_line1': description_line1,
            'description_line2': description_line2
        }
        collection.insert_one(image_document)
    
    # Retrieve all images from MongoDB
    images = list(collection.find())

    quizzes = list(collection.find({}, {'name': 1, '_id': 0}))
    
    return render_template('upload.html', images=images, quizzes=quizzes)


@app.route('/image/<image_id>')
def display_image(image_id):
    # Retrieve the image data from MongoDB
    image_document = collection.find_one({'_id': ObjectId(image_id)})
    if image_document:
        base64_data = image_document['data']
        return f'<img src="data:image/jpeg;base64,{base64_data}" alt="{image_document["filename"]}">'
    else:
        return 'Image not found'


# Flask route for updating image
@app.route('/update_image/<image_id>', methods=['POST'])
def update_image(image_id):
    if request.method == 'POST':
        # Retrieve updated image details from request data
        updated_data = request.json

        # Update the image document in MongoDB
        result = collection.update_one({'_id': ObjectId(image_id)}, {'$set': updated_data})
        if result.modified_count == 1:
            return 'Image updated successfully'
        else:
            return 'Failed to update image'


# Flask route for deleting image
@app.route('/delete_image/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    result = collection.delete_one({'_id': ObjectId(image_id)})
    if result.deleted_count == 1:
        return 'Image deleted successfully'
    else:
        return 'Failed to delete image'


if __name__ == '__main__':
    app.run( debug=True)