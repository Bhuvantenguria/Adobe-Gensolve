# Adobe-GenSolve Hackathon Project

### DrawingApp with SVG Shape Detection and Image Processing

## Overview

This project is an advanced web application that allows users to draw on a canvas, generate CSV data from their drawings, and upload or download results as a ZIP file. It also includes a powerful SVG shape detection and image processing feature that can detect various shapes in an image, process them, and convert the output into SVG format. This application is built using React and `react-konva` for interactive drawing and integrates with a backend API for processing.

## Features

### DrawingApp

- **Interactive Drawing Canvas**: Users can draw lines and shapes on a canvas.
- **CSV Generation**: Automatically generate CSV data based on the drawn points.
- **File Upload**: Upload a CSV file and process it through the backend.
- **File Download**: Download the processed results as a ZIP file containing the CSV data and additional files.
- **Responsive Design**: The application is fully responsive and works across different devices.

### SVG Shape Detection and Image Processing

- **Shape Detection**: Automatically detects common shapes (circle, rectangle, triangle, etc.) in an image.
- **Contour Processing**: Extracts and processes contours to identify and visualize shapes.
- **SVG Conversion**: Converts the detected shapes and contours into an SVG file.
- **Polyline Extraction**: Extracts polylines from the SVG paths for further processing or analysis.
- **CSV Generation**: Generates CSV data from the processed shapes for data analysis or storage.

## Installation

### Frontend (DrawingApp)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DrawingApp.git
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following content:
   ```bash
   REACT_APP_API_URL=http://localhost:5000
   ```

4. Start the development server:
   ```bash
   npm start
   ```

   The app will be available at `http://localhost:3000`.

### Backend (SVG Shape Detection and Image Processing)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/svg-shape-detection.git
   cd backend
   ```

2. **Install Dependencies**:
   Make sure you have Python installed. Install the required libraries using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Project**:
   You can run the project using:
   ```bash
   python run.py
   ```

## Usage

### DrawingApp

1. **Draw on the Canvas**:
   - Click and drag on the canvas to start drawing.
   - The drawing will automatically generate CSV data.

2. **Upload CSV**:
   - Click on the "Upload CSV" button to upload a CSV file.
   - The file will be processed by the backend, and the results can be downloaded.

3. **Download Results**:
   - Click on the "Download Results" button to download the processed files as a ZIP archive.

### SVG Shape Detection and Image Processing

1. Place your input images in the `input_images` directory.
2. Run the script, and it will process the images to detect shapes and generate corresponding SVG files.
3. The output files, including processed images, SVGs, and CSVs, will be saved in the `output` directory.

## Technologies Used

### Frontend

- React.js
- react-konva
- axios
- React Icons

### Backend

- Node.js (Express)
- Python (for shape detection and image processing)
- Konva.js
- CSV Parsing and Generation
- File Handling
- Firebase (storing input and output image)


## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, feel free to open an issue or submit a pull request.

## Demo Video

[![Watch the video](https://img.youtube.com/vi/LS7qxnYSiOU/0.jpg)](https://youtu.be/LS7qxnYSiOU)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
