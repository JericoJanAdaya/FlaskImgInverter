import cv2

def edge_smoothing(input_image_path, output_image_path, kernel_size=(5, 5), sigma_x=0):
    # Read the input image
    image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)

    # Apply Gaussian blur for edge smoothing
    smoothed_image = cv2.GaussianBlur(image, kernel_size, sigma_x)

    # Write the smoothed image to output
    cv2.imwrite(output_image_path, smoothed_image)

if __name__ == "__main__":
    input_image_path = r"D:\COLLEGE STUFF\4TH YEAR\Taiwan\Practicum\HEAD Lab Projects\tactales-library-demo\backend\flask\2-flask-img-inverter\demo\uploads\edited_image.png"
    output_image_path = "smoothed_image.png"
    
    # Adjust the parameters as needed
    kernel_size = (5, 5)  # Kernel size for Gaussian blur
    sigma_x = 0  # Standard deviation in X direction (0 means auto calculated based on kernel size)
    
    edge_smoothing(input_image_path, output_image_path, kernel_size, sigma_x)
