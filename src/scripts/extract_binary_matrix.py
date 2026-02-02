import cv2
import numpy as np

# Read the image
img = cv2.imread('p01-br.png')

if img is None:
    print("Error: Could not load image")
    exit(1)

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Find the grid boundary using adaptive threshold
binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 11, 2)

# Find contours to locate the grid square
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Find the square contour (should be 4-sided and reasonably sized)
square_contour = None
min_area = gray.shape[0] * gray.shape[1] * 0.1  # At least 10% of image area

for contour in contours:
    area = cv2.contourArea(contour)
    if area > min_area:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:  # Square has 4 vertices
            square_contour = approx
            break

if square_contour is None:
    # Fallback: use largest contour
    if contours:
        square_contour = max(contours, key=cv2.contourArea)

if square_contour is not None:
    x, y, w, h = cv2.boundingRect(square_contour)
    # Crop to the square region with some margin
    margin = 5
    grid_region = gray[y+margin:y+h-margin, x+margin:x+w-margin]
else:
    # Use center region of image
    h_img, w_img = gray.shape
    margin = 20
    grid_region = gray[margin:h_img-margin, margin:w_img-margin]

# Now extract the 5x5 grid pattern from the grid region
h, w = grid_region.shape

# Divide into 5x5 grid cells
cell_h = h // 5
cell_w = w // 5

# Extract pattern - check if cells are filled (dark)
pattern_5x5 = np.zeros((5, 5), dtype=int)

for i in range(5):
    for j in range(5):
        # Sample the cell region (avoid edges)
        y_start = i * cell_h + cell_h // 8
        y_end = (i + 1) * cell_h - cell_h // 8
        x_start = j * cell_w + cell_w // 8
        x_end = (j + 1) * cell_w - cell_w // 8
        
        if y_end > y_start and x_end > x_start:
            cell_region = grid_region[y_start:y_end, x_start:x_end]
            # Dark squares have low pixel values
            # If mean is below threshold (e.g., 128), it's filled
            mean_value = np.mean(cell_region)
            if mean_value < 128:  # Dark = filled square
                pattern_5x5[i, j] = 1

# Convert 5x5 to 6x6 by padding with zeros (add column and row)
pattern_6x6 = np.zeros((6, 6), dtype=int)
pattern_6x6[:5, :5] = pattern_5x5

# Display the result
print("6x6 Binary Matrix:")
print(pattern_6x6.tolist())
print("\nFormatted output:")
for row in pattern_6x6:
    print(' '.join(str(cell) for cell in row))

