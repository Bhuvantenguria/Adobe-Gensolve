import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
from datetime import datetime
import uuid

class FirebaseService:
    def __init__(self, credentials_path, bucket_name):
        """Initialize Firebase service"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': bucket_name
                })
            
            self.bucket = storage.bucket()
            self.db = firestore.client()
        except Exception as e:
            print(f"Firebase initialization failed: {str(e)}")
            raise

    def upload_file(self, file_data, file_name, folder="uploads"):
        """Upload file to Firebase Storage"""
        try:
            blob_path = f"{folder}/{file_name}"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(file_data, content_type=self._get_content_type(file_name))
            
            # Make public
            blob.make_public()
            
            return {
                'url': blob.public_url,
                'path': blob_path,
                'name': file_name,
                'size': len(file_data),
                'uploaded_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"File upload failed: {str(e)}")
            return None

    def upload_image(self, image_data, file_name):
        """Upload image to Firebase Storage"""
        return self.upload_file(image_data, file_name, "images")

    def upload_svg(self, svg_data, file_name):
        """Upload SVG to Firebase Storage"""
        return self.upload_file(svg_data, file_name, "svgs")

    def upload_csv(self, csv_data, file_name):
        """Upload CSV to Firebase Storage"""
        return self.upload_file(csv_data, file_name, "csvs")

    def upload_zip(self, zip_data, file_name):
        """Upload ZIP to Firebase Storage"""
        return self.upload_file(zip_data, file_name, "zips")

    def delete_file(self, file_path):
        """Delete file from Firebase Storage"""
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"File deletion failed: {str(e)}")
            return False

    def get_file_url(self, file_path):
        """Get public URL for file"""
        try:
            blob = self.bucket.blob(file_path)
            return blob.public_url
        except Exception as e:
            print(f"Get file URL failed: {str(e)}")
            return None

    def save_processing_record(self, user_id, input_file, output_files, processing_type):
        """Save processing record to Firestore"""
        try:
            record = {
                'user_id': user_id,
                'input_file': input_file,
                'output_files': output_files,
                'processing_type': processing_type,
                'created_at': datetime.now(),
                'status': 'completed'
            }
            
            doc_ref = self.db.collection('processing_records').document()
            doc_ref.set(record)
            
            return doc_ref.id
        except Exception as e:
            print(f"Save processing record failed: {str(e)}")
            return None

    def get_user_processing_history(self, user_id, limit=50):
        """Get user's processing history"""
        try:
            records = self.db.collection('processing_records')\
                .where('user_id', '==', user_id)\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            return [record.to_dict() for record in records]
        except Exception as e:
            print(f"Get processing history failed: {str(e)}")
            return []

    def save_user_data(self, user_id, user_data):
        """Save user data to Firestore"""
        try:
            user_data['updated_at'] = datetime.now()
            self.db.collection('users').document(user_id).set(user_data, merge=True)
            return True
        except Exception as e:
            print(f"Save user data failed: {str(e)}")
            return False

    def get_user_data(self, user_id):
        """Get user data from Firestore"""
        try:
            doc = self.db.collection('users').document(user_id).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Get user data failed: {str(e)}")
            return None

    def save_drawing(self, user_id, drawing_data):
        """Save drawing to Firestore"""
        try:
            drawing_data.update({
                'user_id': user_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            doc_ref = self.db.collection('drawings').document()
            doc_ref.set(drawing_data)
            
            return doc_ref.id
        except Exception as e:
            print(f"Save drawing failed: {str(e)}")
            return None

    def get_user_drawings(self, user_id, limit=50):
        """Get user's drawings"""
        try:
            drawings = self.db.collection('drawings')\
                .where('user_id', '==', user_id)\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            return [drawing.to_dict() for drawing in drawings]
        except Exception as e:
            print(f"Get user drawings failed: {str(e)}")
            return []

    def save_blog_post(self, author_id, post_data):
        """Save blog post to Firestore"""
        try:
            post_data.update({
                'author_id': author_id,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'status': 'published'
            })
            
            doc_ref = self.db.collection('blog_posts').document()
            doc_ref.set(post_data)
            
            return doc_ref.id
        except Exception as e:
            print(f"Save blog post failed: {str(e)}")
            return None

    def get_blog_posts(self, limit=20, status='published'):
        """Get blog posts"""
        try:
            posts = self.db.collection('blog_posts')\
                .where('status', '==', status)\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            return [post.to_dict() for post in posts]
        except Exception as e:
            print(f"Get blog posts failed: {str(e)}")
            return []

    def _get_content_type(self, file_name):
        """Get content type based on file extension"""
        ext = os.path.splitext(file_name)[1].lower()
        content_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.svg': 'image/svg+xml',
            '.csv': 'text/csv',
            '.zip': 'application/zip',
            '.pdf': 'application/pdf'
        }
        return content_types.get(ext, 'application/octet-stream')

    def generate_unique_filename(self, original_name, prefix=""):
        """Generate unique filename"""
        ext = os.path.splitext(original_name)[1]
        unique_id = uuid.uuid4().hex
        return f"{prefix}{unique_id}{ext}" if prefix else f"{unique_id}{ext}" 