from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import os
import pandas as pd
import zipfile
from io import BytesIO
import uuid
from datetime import datetime
import cv2
import base64

# Fix imports - use absolute imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_processor import ImageProcessor
from utils.firebase_service import FirebaseService
from utils.email_service import EmailService
from config import Config

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def get_firebase_service():
    """Get Firebase service from app context"""
    return current_app.firebase_service

def get_email_service():
    """Get Email service from app context"""
    return current_app.email_service

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/auth/register', methods=['POST'])
def register_user():
    """Register new user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not all([email, password, name]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        firebase_service = get_firebase_service()
        if not firebase_service:
            return jsonify({'error': 'Service unavailable'}), 500
        
        # Create user data
        user_data = {
            'email': email,
            'name': name,
            'created_at': datetime.now(),
            'status': 'active'
        }
        
        # Save user to Firebase
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        success = firebase_service.save_user_data(user_id, user_data)
        
        if not success:
            return jsonify({'error': 'User registration failed'}), 500
        
        # Send welcome email
        email_service = get_email_service()
        if email_service:
            email_service.send_welcome_email(email, name)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/auth/login', methods=['POST'])
def login_user():
    """User login"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Missing credentials'}), 400
        
        firebase_service = get_firebase_service()
        if not firebase_service:
            return jsonify({'error': 'Service unavailable'}), 500
        
        # Get user by email (simplified - in real app, use Firebase Auth)
        # For now, we'll create a simple user lookup
        user_id = f"user_{email.split('@')[0]}"
        user_data = firebase_service.get_user_data(user_id)
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # In real app, verify password here
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user_id': user_id,
            'user_data': user_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/upload-csv', methods=['POST'])
def upload_csv():
    """Upload and process CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Read CSV file
        csv_df = pd.read_csv(file)
        
        # Initialize image processor
        image_processor = ImageProcessor()
        
        # Process CSV and generate images
        input_img_bytes, input_csv_buffer, output_img_bytes, output_csv_buffer = \
            image_processor.process_csv_and_generate_image(csv_df)
        
        if input_img_bytes is None:
            return jsonify({'error': 'Processing failed'}), 500
        
        # Generate unique filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_filename = f"input_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        output_filename = f"output_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        input_csv_filename = f"input_{timestamp}_{uuid.uuid4().hex[:8]}.csv"
        output_csv_filename = f"output_{timestamp}_{uuid.uuid4().hex[:8]}.csv"
        
        # Upload files to Firebase
        firebase_service = get_firebase_service()
        if firebase_service:
            input_img_upload = firebase_service.upload_image(input_img_bytes, input_filename)
            output_img_upload = firebase_service.upload_image(output_img_bytes, output_filename)
            input_csv_upload = firebase_service.upload_csv(input_csv_buffer, input_csv_filename)
            output_csv_upload = firebase_service.upload_csv(output_csv_buffer, output_csv_filename)
            
            if not all([input_img_upload, output_img_upload, input_csv_upload, output_csv_upload]):
                return jsonify({'error': 'File upload failed'}), 500
            
            # Create ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                zip_file.writestr(input_filename, input_img_bytes)
                zip_file.writestr(output_filename, output_img_bytes)
                zip_file.writestr(input_csv_filename, input_csv_buffer)
                zip_file.writestr(output_csv_filename, output_csv_buffer)
            
            zip_buffer.seek(0)
            zip_filename = f"results_{timestamp}_{uuid.uuid4().hex[:8]}.zip"
            zip_upload = firebase_service.upload_zip(zip_buffer.getvalue(), zip_filename)
            
            # Save processing record
            user_id = request.form.get('user_id', 'anonymous')
            processing_record = {
                'input_file': input_img_upload,
                'output_files': [output_img_upload, input_csv_upload, output_csv_upload, zip_upload],
                'processing_type': 'csv_to_image'
            }
            firebase_service.save_processing_record(user_id, **processing_record)
            
            return jsonify({
                'success': True,
                'message': 'Processing completed successfully',
                'files': {
                    'input_image': input_img_upload,
                    'output_image': output_img_upload,
                    'input_csv': input_csv_upload,
                    'output_csv': output_csv_upload,
                    'zip_file': zip_upload
                },
                'download_url': zip_upload['url']
            })
        else:
            # Fallback: return files directly
            return send_file(
                zip_buffer, 
                mimetype='application/zip', 
                as_attachment=True, 
                download_name=f'processed_files_{timestamp}.zip'
            )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """Upload image and convert to sketch"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        file.save(temp_path)
        
        # Initialize image processor
        image_processor = ImageProcessor()
        
        # Convert to sketch
        sketch_style = request.form.get('style', 'pencil')
        sketch_image = image_processor.image_to_sketch(temp_path, sketch_style)
        
        if sketch_image is None:
            return jsonify({'error': 'Sketch conversion failed'}), 500
        
        # Extract outlines
        outlines = image_processor.extract_outlines(temp_path)
        
        # Convert to bytes
        _, sketch_buffer = cv2.imencode('.png', sketch_image)
        sketch_bytes = sketch_buffer.tobytes()
        
        _, outline_buffer = cv2.imencode('.png', outlines)
        outline_bytes = outline_buffer.tobytes()
        
        # Generate filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sketch_filename = f"sketch_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        outline_filename = f"outline_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        original_filename = f"original_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        
        # Upload to Firebase
        firebase_service = get_firebase_service()
        if firebase_service:
            with open(temp_path, 'rb') as f:
                original_bytes = f.read()
            
            sketch_upload = firebase_service.upload_image(sketch_bytes, sketch_filename)
            outline_upload = firebase_service.upload_image(outline_bytes, outline_filename)
            original_upload = firebase_service.upload_image(original_bytes, original_filename)
            
            # Clean up temp file
            os.remove(temp_path)
            
            if not all([sketch_upload, outline_upload, original_upload]):
                return jsonify({'error': 'File upload failed'}), 500
            
            return jsonify({
                'success': True,
                'message': 'Image processing completed',
                'files': {
                    'original_image': original_upload,
                    'sketch_image': sketch_upload,
                    'outline_image': outline_upload
                }
            })
        else:
            # Fallback: return base64 encoded images
            _, original_buffer = cv2.imencode('.png', cv2.imread(temp_path))
            original_base64 = base64.b64encode(original_buffer).decode('utf-8')
            sketch_base64 = base64.b64encode(sketch_buffer).decode('utf-8')
            outline_base64 = base64.b64encode(outline_buffer).decode('utf-8')
            
            os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'message': 'Image processing completed',
                'files': {
                    'original_image': {'url': f"data:image/png;base64,{original_base64}"},
                    'sketch_image': {'url': f"data:image/png;base64,{sketch_base64}"},
                    'outline_image': {'url': f"data:image/png;base64,{outline_base64}"}
                }
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/drawing/save', methods=['POST'])
def save_drawing():
    """Save user drawing"""
    try:
        data = request.json
        drawing_data = data.get('drawingData')
        user_id = data.get('userId', 'anonymous')
        title = data.get('title', 'Untitled Drawing')
        description = data.get('description', '')
        
        if not drawing_data:
            return jsonify({'error': 'No drawing data provided'}), 400
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"drawing_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        
        # Convert base64 to image and upload
        image_data = base64.b64decode(drawing_data.split(',')[1])
        
        firebase_service = get_firebase_service()
        if firebase_service:
            upload_result = firebase_service.upload_image(image_data, filename)
            
            if not upload_result:
                return jsonify({'error': 'Drawing upload failed'}), 500
            
            # Save drawing record
            drawing_record = {
                'title': title,
                'description': description,
                'image_url': upload_result['url'],
                'file_path': upload_result['path'],
                'file_size': upload_result['size']
            }
            
            drawing_id = firebase_service.save_drawing(user_id, drawing_record)
            
            return jsonify({
                'success': True,
                'message': 'Drawing saved successfully',
                'drawing_id': drawing_id,
                'file_url': upload_result['url']
            })
        else:
            return jsonify({'error': 'Service unavailable'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/drawing/list', methods=['GET'])
def list_drawings():
    """Get user's drawings"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        limit = int(request.args.get('limit', 50))
        
        firebase_service = get_firebase_service()
        if not firebase_service:
            return jsonify({'error': 'Service unavailable'}), 500
        
        drawings = firebase_service.get_user_drawings(user_id, limit)
        
        return jsonify({
            'success': True,
            'drawings': drawings,
            'count': len(drawings)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/user/profile', methods=['GET'])
def get_user_profile():
    """Get user profile"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        firebase_service = get_firebase_service()
        if not firebase_service:
            return jsonify({'error': 'Service unavailable'}), 500
        
        user_data = firebase_service.get_user_data(user_id)
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/user/profile', methods=['PUT'])
def update_user_profile():
    """Update user profile"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        user_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'bio': data.get('bio'),
            'avatar_url': data.get('avatar_url'),
            'preferences': data.get('preferences', {})
        }
        
        firebase_service = get_firebase_service()
        if not firebase_service:
            return jsonify({'error': 'Service unavailable'}), 500
        
        success = firebase_service.save_user_data(user_id, user_data)
        
        if not success:
            return jsonify({'error': 'Profile update failed'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/processing/history', methods=['GET'])
def get_processing_history():
    """Get user's processing history"""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 20))
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        firebase_service = get_firebase_service()
        if not firebase_service:
            return jsonify({'error': 'Service unavailable'}), 500
        
        history = firebase_service.get_user_processing_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/blog/posts', methods=['GET'])
def get_blog_posts():
    """Get blog posts"""
    try:
        limit = int(request.args.get('limit', 20))
        status = request.args.get('status', 'published')
        
        firebase_service = get_firebase_service()
        if not firebase_service:
            return jsonify({'error': 'Service unavailable'}), 500
        
        posts = firebase_service.get_blog_posts(limit, status)
        
        return jsonify({
            'success': True,
            'posts': posts,
            'count': len(posts)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/blog/posts', methods=['POST'])
def create_blog_post():
    """Create new blog post"""
    try:
        data = request.json
        author_id = data.get('author_id')
        title = data.get('title')
        content = data.get('content')
        
        if not all([author_id, title, content]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        firebase_service = get_firebase_service()
        if not firebase_service:
            return jsonify({'error': 'Service unavailable'}), 500
        
        post_data = {
            'title': title,
            'content': content,
            'tags': data.get('tags', []),
            'category': data.get('category', 'general'),
            'featured_image': data.get('featured_image'),
            'excerpt': data.get('excerpt', content[:200] + '...')
        }
        
        post_id = firebase_service.save_blog_post(author_id, post_data)
        
        if not post_id:
            return jsonify({'error': 'Blog post creation failed'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Blog post created successfully',
            'post_id': post_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/email/send', methods=['POST'])
def send_email():
    """Send email notification"""
    try:
        data = request.json
        email_type = data.get('type')
        user_email = data.get('user_email')
        user_name = data.get('user_name')
        
        if not all([email_type, user_email, user_name]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        email_service = get_email_service()
        if not email_service:
            return jsonify({'error': 'Email service unavailable'}), 500
        
        success = False
        
        if email_type == 'welcome':
            success = email_service.send_welcome_email(user_email, user_name)
        elif email_type == 'password_reset':
            reset_token = data.get('reset_token')
            success = email_service.send_password_reset_email(user_email, reset_token, user_name)
        elif email_type == 'processing_complete':
            processing_type = data.get('processing_type')
            download_url = data.get('download_url')
            success = email_service.send_processing_complete_email(user_email, user_name, processing_type, download_url)
        elif email_type == 'community_notification':
            notification_type = data.get('notification_type')
            content = data.get('content')
            success = email_service.send_community_notification(user_email, user_name, notification_type, content)
        else:
            return jsonify({'error': 'Invalid email type'}), 400
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully'
            })
        else:
            return jsonify({'error': 'Email sending failed'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 