import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

# --- Load template images ---
template_dir = "templates/"
templates = {}
for file in os.listdir(template_dir):
    if file.endswith(".png", ".jpg", ".jpeg"):
        name = file.split(".")[0]  # e.g., "wP"
        img = cv2.imread(os.path.join(template_dir, file), cv2.IMREAD_UNCHANGED)
        templates[name] = img

# --- Load test board ---
board_img = cv2.imread("test_boards/board1.jpg")
board_gray = cv2.cvtColor(board_img, cv2.COLOR_BGR2GRAY)

# --- Optional: resize board if needed ---
board_gray = cv2.resize(board_gray, (400, 400))  # standardize to 8x8 grid later

# --- Iterate over squares and try template matching ---
square_size = board_gray.shape[0] // 8
detections = []

for row in range(8):
    for col in range(8):
        x = col * square_size
        y = row * square_size
        square = board_gray[y : y + square_size, x : x + square_size]

        best_match = None
        max_val = 0
        for name, tmpl in templates.items():
            tmpl_gray = cv2.cvtColor(tmpl, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(square, tmpl_gray, cv2.TM_CCOEFF_NORMED)
            _, val, _, _ = cv2.minMaxLoc(res)
            if val > max_val:
                max_val = val
                best_match = name

        if max_val > 0.6:  # threshold for match confidence
            detections.append((row, col, best_match, max_val))
            cv2.putText(
                board_img,
                best_match,
                (x + 5, y + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
            )

# --- Show results ---
plt.imshow(cv2.cvtColor(board_img, cv2.COLOR_BGR2RGB))
plt.title("Template Matching Detections")
plt.show()

# Print raw detections
for det in detections:
    print(det)
