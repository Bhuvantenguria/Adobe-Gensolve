from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_mail import Mail
from flask_jwt_extended import JWTManager
import os
import cv2
from datetime import datetime

from config import Config
from routes.api import api_bp
from utils.firebase_service import FirebaseService
from utils.email_service import EmailService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={r"/*": {"origins": Config.CORS_ORIGINS}})
    jwt = JWTManager(app)
    
    try:
        firebase_service = FirebaseService(Config.FIREBASE_CREDENTIALS_PATH, Config.FIREBASE_BUCKET)
        app.firebase_service = firebase_service
    except Exception as e:
        print(f"Firebase initialization failed: {str(e)}")
        app.firebase_service = None
    
    email_service = EmailService(app)
    app.email_service = email_service
    
    app.register_blueprint(api_bp)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/upload-csv', methods=['POST'])
    def legacy_upload_csv():
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.endswith('.csv'):
                return jsonify({'error': 'Invalid file type'}), 400
            
            from utils.image_processor import ImageProcessor
            image_processor = ImageProcessor()
            
            import pandas as pd
            csv_df = pd.read_csv(file)
            
            input_img_bytes, input_csv_buffer, output_img_bytes, output_csv_buffer = \
                image_processor.process_csv_and_generate_image(csv_df)
            
            if input_img_bytes is None:
                return jsonify({'error': 'Processing failed'}), 500
            
            import uuid
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            input_filename = f"input_{timestamp}_{uuid.uuid4().hex[:8]}.png"
            output_filename = f"output_{timestamp}_{uuid.uuid4().hex[:8]}.png"
            input_csv_filename = f"input_{timestamp}_{uuid.uuid4().hex[:8]}.csv"
            output_csv_filename = f"output_{timestamp}_{uuid.uuid4().hex[:8]}.csv"
            
            if app.firebase_service:
                input_img_upload = app.firebase_service.upload_image(input_img_bytes, input_filename)
                output_img_upload = app.firebase_service.upload_image(output_img_bytes, output_filename)
                input_csv_upload = app.firebase_service.upload_csv(input_csv_buffer, input_csv_filename)
                output_csv_upload = app.firebase_service.upload_csv(output_csv_buffer, output_csv_filename)
                
                if all([input_img_upload, output_img_upload, input_csv_upload, output_csv_upload]):
                    user_id = request.form.get('user_id', 'anonymous')
                    processing_record = {
                        'input_file': input_img_upload,
                        'output_files': [output_img_upload, input_csv_upload, output_csv_upload],
                        'processing_type': 'csv_to_image'
                    }
                    app.firebase_service.save_processing_record(user_id, **processing_record)
            
            import zipfile
            from io import BytesIO
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                zip_file.writestr(input_filename, input_img_bytes)
                zip_file.writestr(output_filename, output_img_bytes)
                zip_file.writestr(input_csv_filename, input_csv_buffer)
                zip_file.writestr(output_csv_filename, output_csv_buffer)
            
            zip_buffer.seek(0)
            
            return send_file(
                zip_buffer, 
                mimetype='application/zip', 
                as_attachment=True, 
                download_name=f'processed_files_{timestamp}.zip'
            )
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=port)
