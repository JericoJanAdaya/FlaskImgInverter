import logging
from flask import Flask, request, send_file, render_template, redirect, url_for
import numpy as np
from PIL import Image
import os
import open3d as o3d

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_mesh(vertices, faces):
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(faces)
    return mesh

def image_to_obj(image_path, output_file):
    try:
        # Load the image and convert to grayscale
        img = Image.open(image_path).convert('L')
        data = 255 - np.array(img)

        # Define vertices for the top surface
        top_vertices = []
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                z = data[i][j] * 0.2  # Adjust the scale factor as needed
                top_vertices.append([i, j, z])
        top_vertices = np.array(top_vertices)

        # Create faces for the top surface
        top_faces = []
        for i in range(data.shape[0] - 1):
            for j in range(data.shape[1] - 1):
                v0 = i * data.shape[1] + j
                v1 = v0 + 1
                v2 = v0 + data.shape[1]
                v3 = v2 + 1

                top_faces.append([v0, v1, v2])
                top_faces.append([v2, v1, v3])

        # Create and smooth the top surface mesh
        top_mesh = create_mesh(top_vertices, top_faces)
        top_mesh.compute_vertex_normals()
        smoothed_top_mesh = top_mesh.filter_smooth_simple(number_of_iterations=2)

        # Extract smoothed top surface vertices
        smoothed_top_vertices = np.asarray(smoothed_top_mesh.vertices)

        # Prepare bottom surface vertices with correct dimensions
        bottom_vertices = np.hstack([top_vertices[:, :2], np.zeros((top_vertices.shape[0], 1))])

        # Create full vertices array by concatenating smoothed top vertices with bottom vertices
        vertices = np.vstack([smoothed_top_vertices, bottom_vertices])

        # Initialize faces array with top surface faces
        faces = top_faces.copy()  # Make a copy of the top_faces to start with top surface faces

        # Calculate offset for bottom vertices (after the smoothed top vertices)
        offset = smoothed_top_vertices.shape[0]

        # Bottom surface faces
        for i in range(data.shape[0] - 1):
            for j in range(data.shape[1] - 1):
                v0 = offset + i * data.shape[1] + j
                v1 = v0 + 1
                v2 = v0 + data.shape[1]
                v3 = v2 + 1

                faces.append([v0, v2, v1])
                faces.append([v2, v3, v1])

        # Create faces for the sides
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                if i < data.shape[0] - 1:
                    # Side faces in i direction
                    v0 = i * data.shape[1] + j
                    v1 = v0 + data.shape[1]
                    v2 = v1 + offset
                    v3 = v0 + offset

                    faces.append([v0, v1, v2])
                    faces.append([v0, v2, v3])

                if j < data.shape[1] - 1:
                    # Side faces in j direction
                    v0 = i * data.shape[1] + j
                    v1 = v0 + 1
                    v2 = v1 + offset
                    v3 = v0 + offset

                    faces.append([v0, v1, v2])
                    faces.append([v0, v2, v3])

        # Create the final mesh
        mesh = create_mesh(vertices, faces)
        mesh.compute_vertex_normals()   

        # Save the smoothed mesh
        o3d.io.write_triangle_mesh(output_file, mesh)

        return {'message': 'OBJ file saved successfully', 'filename': os.path.basename(output_file)}

    except Exception as e:
        print(f'Error while converting image to OBJ: {str(e)}')
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
        logger.warning('No image file provided')
        return {'message': 'No image file provided'}, 400

    image = request.files['image']
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)

    # Save the image
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)
    logger.info(f'Image saved at {image_path}')

    # Create the OBJ file path
    obj_file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(image.filename)[0] + '.obj')

    # Convert the image to OBJ and save
    result = image_to_obj(image_path, obj_file_path)
    if result['message'] == 'OBJ file saved successfully':
        return {'message': 'OBJ file saved successfully', 'filename': os.path.basename(obj_file_path)}
    else:
        return {'message': result['message'], 'filename': ''}, 500


if __name__ == '__main__':
    app.run(debug=True)
