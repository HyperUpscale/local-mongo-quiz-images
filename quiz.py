from flask import Flask, flash, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import image
import base64

# Configure the upload folder


app = Flask(__name__)
app.secret_key = 'secret@key'

client = MongoClient('localhost', 27017)
db = client['image_database']
collection = db['images']



@app.route('/')
def index():
    quizzes = collection.find()
    return render_template('index.html', quizzes=quizzes)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        collection.insert_one({'name': name, 'category': category})
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/edit/<quiz_id>', methods=('GET', 'POST'))
def edit(quiz_id):
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        images = request.form.getlist('images')  # Get list of image URLs from form
        collection.update_one({'_id': ObjectId(quiz_id)}, {'$set': {'name': name, 'category': category, 'images': images}})
        return redirect(url_for('index'))
    else:
        quiz = collection.find_one({'_id': ObjectId(quiz_id)})
        if quiz is None:
            abort(404)
        return render_template('edit.html', quiz=quiz)

@app.route('/start/<quiz_id>')
def start(quiz_id):
    return render_template('start.html')


@app.route('/upload_image', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        image = request.files['image']
        if image.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        # Read additional parameters from the form
        quiz_id = request.form['quiz_id']
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
            'quiz_id': quiz_id,  # Include quiz ID
            'score': int(score),  # Convert score to integer
            'description_line1': description_line1,
            'description_line2': description_line2
        }
        collection.insert_one(image_document)
        flash('Image uploaded successfully', 'success')
    
    return redirect(url_for('index'))




@app.route('/gallery/<quiz_id>')
def gallery(quiz_id):
    quiz = collection.find_one({'_id': ObjectId(quiz_id)})
    if quiz is None:
        abort(404)
        

    quizzes = list(collection.find({}, {'name': 1, '_id': 0}))
    images = list(collection.find({'quiz_name': quiz['name']}))

    return render_template('gallery.html', images=images, quizzes=quizzes)
    
@app.route('/delete_image/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    collection_images.delete_one({'_id': ObjectId(image_id)})
    return 'Image deleted successfully'

@app.route('/delete_quiz/<quiz_id>', methods=['GET', 'POST'])
def delete_quiz(quiz_id):
    quiz = collection.find_one({'_id': ObjectId(quiz_id)})
    if quiz:
        quiz_name = quiz.get('name', 'Unknown Quiz')
        collection.delete_one({'_id': ObjectId(quiz_id)})
        flash(f'Quiz <span style="color: red;">"{quiz_name}"</span> <span style="color: red;">deleted</span> successfully', 'success')  # Flash a success message with colored quiz name and "deleted"
    else:
        flash('Quiz deletion failed. Quiz not found.', 'error')  # Flash an error message if the quiz is not found
    return redirect(url_for('index'))  # Redirect back to the index page

if __name__ == '__main__':
    app.run(debug=True)

