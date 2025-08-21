import cv2 as cv
import numpy as np
import pandas as pd
import svgwrite
from svgpathtools import svg2paths
import os
from io import BytesIO
import uuid

class ImageProcessor:
    def __init__(self):
        self.default_canvas_size = (512, 512)
        
    def image_to_svg(self, img, contours_to_draw, circle_info, bounding_box, linesToDraw, filename="output.svg"):
        """Convert processed image to SVG format"""
        try:
            height, width = img.shape[:2]
            dwg = svgwrite.Drawing(filename, profile='full', size=(width, height))
            
            # Add contours
            for contour, color in contours_to_draw:
                points = contour[:, 0, :].tolist()
                path_data = f"M {points[0][0]},{points[0][1]} " + " ".join([f"L {p[0]},{p[1]}" for p in points[1:]])
                path_data += " Z"
                path = dwg.path(d=path_data, stroke=svgwrite.rgb(*color, '%'), fill="none", stroke_width=1)
                dwg.add(path)
            
            # Add circles
            for center, radius in circle_info:
                dwg.add(dwg.circle(center=center, r=radius, stroke=svgwrite.rgb(0, 0, 255, '%'), fill="none", stroke_width=1))
            
            # Add bounding boxes
            for box in bounding_box:
                points = box.tolist()
                for i in range(4):
                    x1, y1 = points[i]
                    x2, y2 = points[(i + 1) % 4]
                    dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(255, 0, 0, '%'), stroke_width=1))

            # Add lines
            for line in linesToDraw:
                dwg.add(dwg.line((int(a) for a in line[0]), (int(a) for a in line[1]), stroke=svgwrite.rgb(0, 255, 0, '%'), stroke_width=1))

            dwg.save()
            return True
        except Exception as e:
            print(f"SVG generation failed: {str(e)}")
            return False

    def svg2polylines(self, svg_path):
        """Convert SVG to polylines"""
        try:
            paths, attributes = svg2paths(svg_path)
            polylines = []
            
            for path in paths:
                polyline = []
                for segment in path:
                    start_point = segment.start
                    end_point = segment.end
                    
                    polyline.append((start_point.real, start_point.imag))
                    
                    if segment.__class__.__name__ != 'Line':
                        for t in np.linspace(0, 1, num=100):
                            point = segment.point(t)
                            polyline.append((point.real, point.imag))
                    
                    polyline.append((end_point.real, end_point.imag))
                
                polylines.append(np.array(polyline))
            
            return polylines
        except Exception as e:
            print(f"SVG to polylines conversion failed: {str(e)}")
            return []

    def process_csv_to_image(self, polylines):
        """Process CSV data and generate image"""
        try:
            img = np.zeros(self.default_canvas_size, dtype=np.uint8)
            current_polyline = None

            for i in range(len(polylines)):
                if [polylines.iloc[i, 0], polylines.iloc[i, 1]] != current_polyline:
                    current_polyline = [polylines.iloc[i, 0], polylines.iloc[i, 1]]
                else:
                    pt1 = (int(round(polylines.iloc[i-1, 2])), int(round(polylines.iloc[i-1, 3])))
                    pt2 = (int(round(polylines.iloc[i, 2])), int(round(polylines.iloc[i, 3])))
                    cv.line(img, pt1, pt2, color=255, thickness=1)

            return img
        except Exception as e:
            print(f"CSV to image processing failed: {str(e)}")
            return None

    def detect_shapes(self, img):
        """Detect shapes in the image"""
        try:
            blur = cv.blur(img, (1, 1))
            _, binary = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
            img_rgb = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

            shape_info = []
            for contour in contours:
                if cv.contourArea(contour) < 3:
                    shape_info.append(("unidentified", contour))
                    continue

                eps = 0.01 * cv.arcLength(contour, True)
                approx = cv.approxPolyDP(contour, eps, True)
                shape = "unidentified"
                peri = cv.arcLength(contour, True)
                area = cv.contourArea(contour)
                vertices = len(approx)

                if vertices >= 7:
                    (x, y), radius = cv.minEnclosingCircle(contour)
                    circle_area = np.pi * (radius ** 2)
                    if abs(area - circle_area) < 0.2 * circle_area:
                        center = (int(x), int(y))
                        shape = "circle"
                        shape_info.append((shape, (center, int(radius), contour)))
                        continue
                    circularity = 4 * np.pi * area / (peri ** 2)
                    if 0.43 < circularity < 0.79:
                        shape_info.append(("unidentified", contour))
                        continue
                else:
                    eps = 0.02 * cv.arcLength(contour, True)
                    approx = cv.approxPolyDP(contour, eps, True)
                    vertices = len(approx)
                    
                    if vertices == 3:
                        shape = "triangle"
                    elif vertices == 4:
                        shape = "rectangle"
                    elif vertices == 5:
                        shape = "pentagon"
                    elif vertices == 6:
                        shape = "hexagon"
                    elif vertices == 7:
                        if peri / area > 0.05:
                            shape_info.append(("unidentified", contour))
                            continue
                        shape = "heptagon"
                    elif vertices == 8:
                        shape = "octagon"
                    elif vertices == 9:
                        shape = "nonagon"
                    elif vertices == 10:
                        if peri / area > 0.105:
                            shape_info.append(("unidentified", contour))
                            continue
                        shape = "circle"

                if shape != "unidentified":
                    shape_info.append((shape, (contour, approx)))
                else:
                    shape_info.append((shape, contour))

            return shape_info, img_rgb
        except Exception as e:
            print(f"Shape detection failed: {str(e)}")
            return [], None

    def process_shapes(self, shape_info, img_rgb):
        """Process detected shapes and generate final image"""
        try:
            mask = np.ones(self.default_canvas_size, dtype=np.uint8) * 255
            circleInfo = []
            boundingBox = []
            contoursToDraw = []
            finalContours = []
            linesToDraw = []

            for shape, contour in shape_info:
                if shape == "triangle":
                    cv.drawContours(mask, [contour[0]], -1, 0, 1)
                    contoursToDraw.append((contour[1], (0, 128, 0)))
                elif shape == "rectangle":
                    rect = cv.minAreaRect(contour[0])
                    box = cv.boxPoints(rect)
                    box = box.astype(int)
                    boundingBox.append(box)
                    cv.drawContours(mask, [contour[0]], -1, 0, 1)
                elif shape == "pentagon":
                    cv.drawContours(mask, [contour[0]], -1, 0, 1)
                    contoursToDraw.append((contour[1], (128, 0, 128)))
                elif shape == "hexagon":
                    cv.drawContours(mask, [contour[0]], -1, 0, 1)
                    contoursToDraw.append((contour[1], (0, 128, 128)))
                elif shape == "heptagon":
                    cv.drawContours(mask, [contour[0]], -1, 0, 1)
                    contoursToDraw.append((contour[1], (255, 165, 0)))
                elif shape == "octagon":
                    cv.drawContours(mask, [contour[0]], -1, 0, 1)
                    contoursToDraw.append((contour[1], (0, 165, 255)))
                elif shape == "nonagon":
                    cv.drawContours(mask, [contour[0]], -1, 0, 1)
                    contoursToDraw.append((contour[1], (75, 0, 130)))
                elif shape == "circle":
                    center, radius = contour[0], contour[1]
                    circleInfo.append((center, radius))
                    cv.drawContours(mask, [contour[2]], -1, 0, 1)
                else:
                    cv.drawContours(img_rgb, [contour], -1, (255, 255, 0), 1)
                    finalContours.append((contour, (255, 255, 0)))

            img_rgb = cv.bitwise_and(img_rgb, img_rgb, mask=mask)

            # Process circles
            for info in circleInfo:
                center, radius = info
                cv.circle(img_rgb, center, radius - 5, (0, 0, 255), 1)
                cv.line(img_rgb, (center[0] - radius, center[1]), (center[0] + radius, center[1]), (0, 255, 0), 1)
                cv.line(img_rgb, (center[0], center[1] - radius), (center[0], center[1] + radius), (0, 255, 0), 1)
                linesToDraw.append([(int(center[0] - radius), int(center[1])), (int(center[0] + radius), int(center[1]))])
                linesToDraw.append([(int(center[0]), int(center[1] - radius)), (int(center[0]), int(center[1] + radius))])

            # Process rectangles
            for box in boundingBox:
                cv.drawContours(img_rgb, [box], 0, (255, 0, 0), 1)
                p1_h = tuple(box[1])
                p2_h = tuple(box[3])
                cv.line(img_rgb, p1_h, p2_h, (0, 255, 0), 1)
                linesToDraw.append([p1_h, p2_h])
                
                mid1 = tuple(((box[0] + box[1]) // 2).astype(int))
                mid2 = tuple(((box[1] + box[2]) // 2).astype(int))
                mid3 = tuple(((box[2] + box[3]) // 2).astype(int))
                mid4 = tuple(((box[3] + box[0]) // 2).astype(int))
                
                cv.line(img_rgb, mid1, mid3, (0, 255, 0), 1)
                cv.line(img_rgb, mid2, mid4, (0, 255, 0), 1)
                linesToDraw.append([mid1, mid3])
                linesToDraw.append([mid2, mid4])

            # Process other contours
            for contour in contoursToDraw:
                cv.drawContours(img_rgb, [contour[0]], -1, contour[1], 1)
                finalContours.append(contour)

                M = cv.moments(contour[0])
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    
                    contour_points = np.squeeze(contour[0]).astype(np.float32)
                    mean, eigenvectors = cv.PCACompute(contour_points, mean=np.array([]).astype(np.float32))
                    principal_axis = eigenvectors[0]
                    length = 100
                    x1 = int(cx - length * principal_axis[0])
                    y1 = int(cy - length * principal_axis[1])
                    x2 = int(cx + length * principal_axis[0])
                    y2 = int(cy + length * principal_axis[1])
                    
                    cv.line(img_rgb, (x1, y1), (x2, y2), (0, 255, 0), 1)
                    linesToDraw.append([(x1, y1), (x2, y2)])

            return img_rgb, finalContours, circleInfo, boundingBox, linesToDraw
        except Exception as e:
            print(f"Shape processing failed: {str(e)}")
            return None, [], [], [], []

    def image_to_sketch(self, image_path, style='pencil'):
        """Convert image to sketch"""
        try:
            img = cv.imread(image_path)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            
            # Apply different sketch styles
            if style == 'pencil':
                blurred = cv.GaussianBlur(gray, (5, 5), 1.5)
                edges = cv.Canny(blurred, 50, 150)
                sketch = cv.bitwise_not(edges)
            elif style == 'pen':
                blurred = cv.GaussianBlur(gray, (3, 3), 0)
                edges = cv.Canny(blurred, 100, 200)
                sketch = cv.bitwise_not(edges)
            elif style == 'charcoal':
                blurred = cv.GaussianBlur(gray, (7, 7), 2)
                edges = cv.Canny(blurred, 30, 100)
                sketch = cv.bitwise_not(edges)
            else:
                blurred = cv.GaussianBlur(gray, (5, 5), 1.5)
                edges = cv.Canny(blurred, 50, 150)
                sketch = cv.bitwise_not(edges)
            
            # Clean up noise
            kernel = np.ones((2,2), np.uint8)
            sketch = cv.morphologyEx(sketch, cv.MORPH_CLOSE, kernel)
            
            return sketch
        except Exception as e:
            print(f"Image to sketch conversion failed: {str(e)}")
            return None

    def extract_outlines(self, image_path):
        """Extract clean outlines from image"""
        try:
            img = cv.imread(image_path)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            
            # Multiple edge detection methods
            edges_canny = cv.Canny(gray, 50, 150)
            laplacian = cv.Laplacian(gray, cv.CV_64F)
            edges_laplacian = np.uint8(np.absolute(laplacian))
            
            sobelx = cv.Sobel(gray, cv.CV_64F, 1, 0, ksize=3)
            sobely = cv.Sobel(gray, cv.CV_64F, 0, 1, ksize=3)
            edges_sobel = np.sqrt(sobelx**2 + sobely**2)
            edges_sobel = np.uint8(edges_sobel)
            
            # Combine methods
            combined_edges = cv.bitwise_or(edges_canny, edges_laplacian)
            combined_edges = cv.bitwise_or(combined_edges, edges_sobel)
            
            # Clean edges
            kernel = np.ones((2,2), np.uint8)
            cleaned_edges = cv.morphologyEx(combined_edges, cv.MORPH_CLOSE, kernel)
            
            return cleaned_edges
        except Exception as e:
            print(f"Outline extraction failed: {str(e)}")
            return None

    def process_csv_and_generate_image(self, polylines):
        """Main processing function for CSV to image conversion"""
        try:
            # Process CSV to image
            img = self.process_csv_to_image(polylines)
            if img is None:
                return None, None, None, None
            
            # Detect shapes
            shape_info, img_rgb = self.detect_shapes(img)
            if img_rgb is None:
                return None, None, None, None
            
            # Process shapes
            processed_img, finalContours, circleInfo, boundingBox, linesToDraw = self.process_shapes(shape_info, img_rgb)
            if processed_img is None:
                return None, None, None, None
            
            # Generate output files
            input_img_bytes = self.image_to_bytes(img)
            input_csv_buffer = self.dataframe_to_csv_buffer(polylines)
            
            # Generate SVG
            output_filename = f"svg-{uuid.uuid4().hex}.svg"
            self.image_to_svg(processed_img, finalContours, circleInfo, boundingBox, linesToDraw, filename=output_filename)
            
            # Convert SVG to polylines
            output_polylines = self.svg2polylines(output_filename)
            
            # Clean up
            if os.path.exists(output_filename):
                os.remove(output_filename)
            
            # Generate output CSV
            csv_data = []
            for index, polyline in enumerate(output_polylines):
                for point in polyline:
                    csv_data.append([index, 0, point[0], point[1]])
            
            csv_df = pd.DataFrame(csv_data)
            output_csv_buffer = self.dataframe_to_csv_buffer(csv_df)
            
            # Convert processed image to bytes
            output_img_bytes = self.image_to_bytes(processed_img)
            
            return input_img_bytes, input_csv_buffer, output_img_bytes, output_csv_buffer
            
        except Exception as e:
            print(f"CSV processing failed: {str(e)}")
            return None, None, None, None

    def image_to_bytes(self, image):
        """Convert OpenCV image to bytes"""
        try:
            _, img_encoded = cv.imencode('.png', image)
            return img_encoded.tobytes()
        except Exception as e:
            print(f"Image to bytes conversion failed: {str(e)}")
            return None

    def dataframe_to_csv_buffer(self, df):
        """Convert DataFrame to CSV buffer"""
        try:
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False, header=False)
            csv_buffer.seek(0)
            return csv_buffer.getvalue()
        except Exception as e:
            print(f"DataFrame to CSV conversion failed: {str(e)}")
            return None 