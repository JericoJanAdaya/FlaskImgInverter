import logging
from flask import Flask, request, send_file, render_template, redirect, url_for
import numpy as np
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def image_to_obj(image_path, output_file):
    try:
        # Load the image
        img = Image.open(image_path).convert('L')  # Convert to grayscale

        # Convert image to numpy array
        data = np.array(img)

        # Define vertices for the mesh
        vertices = []

        # Define extrusion height for black areas
        extrusion_height = 20.0  # You can adjust this value

        # Iterate through the image and create vertices
        for i in range(len(data)):
            for j in range(len(data[0])):
                # Adjust Z scale according to pixel intensity
                if data[i][j] >= 128:  # If the pixel is white
                    z = 0.0  # White pixels have zero height
                else:
                    z = extrusion_height  # Positive extrusion height for black pixels

                vertices.append([i, j, z])

        # Define the vertices and faces for the mesh
        vertices = np.array(vertices)
        faces = []

        # Create faces for the sides
        num_cols = len(data[0])
        num_rows = len(data)
        for j in range(num_cols - 1):
            for i in range(num_rows - 1):
                v0 = i * num_cols + j
                v1 = v0 + 1
                v2 = v0 + num_cols
                v3 = v2 + 1

                faces.append([v0, v1, v3])
                faces.append([v0, v3, v2])

        # Create faces for the back side
        back_offset = len(vertices)
        for i in range(num_rows):
            for j in range(num_cols):
                vertices = np.append(vertices, [[i, j, 0.0]], axis=0)  # Add vertices at zero height for the back side

        for i in range(num_rows - 1):
            for j in range(num_cols - 1):
                # Define vertices for the current quad on the back side
                v0 = back_offset + i * num_cols + j
                v1 = v0 + 1
                v2 = v0 + num_cols
                v3 = v2 + 1

                faces.append([v0, v2, v1])
                faces.append([v1, v2, v3])

        # Write the vertices and faces to the OBJ file
        with open(output_file, 'w') as f:
            for vertex in vertices:
                f.write('v {} {} {}\n'.format(vertex[0], vertex[1], vertex[2]))

            for face in faces:
                f.write('f {} {} {}\n'.format(face[0] + 1, face[1] + 1, face[2] + 1))

        return {'message': 'OBJ file saved successfully', 'filename': os.path.basename(output_file)}

    except Exception as e:
        return {'message': f'Error while converting image to OBJ: {str(e)}'}


@app.route('/')
def home():
    return render_template('front-display/home-display.html')


@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        # Convert and save the grayscale image
        image = Image.open(file).convert('L')
        grayscale_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'grayscale_' + file.filename)
        image.save(grayscale_filepath)

        return redirect(url_for('display_image', filename='grayscale_' + file.filename))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))


@app.route('/display/<filename>')
def display_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template('front-display/render-display.html', filename=filename)


@app.route('/save-adjusted-image', methods=['POST'])
def save_adjusted_image():
    if 'image' not in request.files:
        return {'message': 'No image file provided'}, 400

    image = request.files['image']
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)

    # Save the adjusted image
    with open(save_path, "wb") as f:
        f.write(image.read())

    return {'message': 'Adjusted image saved successfully', 'filename': image.filename}


@app.route('/save-as-obj', methods=['POST'])
def save_as_obj():
    if 'image' not in request.files:
        return {'message': 'No image file provided'}, 400

    image = request.files['image']
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)

    # Save the image
    image.save(save_path)

    # Create the OBJ file path
    obj_file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(image.filename)[0] + '.obj')

    # Convert the image to OBJ and save
    try:
        image_to_obj(save_path, obj_file_path)
        return {'message': 'OBJ file saved successfully', 'filename': os.path.basename(obj_file_path)}
    except Exception as e:
        return {'message': f'Error saving OBJ file: {str(e)}'}, 500


if __name__ == '__main__':
    app.run(debug=True)
