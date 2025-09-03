#kp Willy Wijaya
from flask import Flask, request, render_template, url_for, jsonify, Response
import io
import base64
import uuid
import numpy as np
from datetime import datetime, timedelta
from PIL import Image 
from ai_model.model import analyze_image
from reportGenerator.report import buat_pdf
import re

app = Flask(__name__)  
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)  # Session expires after 15 minutes

# untuk menyimpan hasil analisis 
analysis_sessions = {}

# halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# api untuk upload gambar
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    try: 
        image_bytes = file.read()

        # Open image using PIL
        image = Image.open(io.BytesIO(image_bytes))
        image_format = image.format if image.format else "PNG"
        
        nama = request.form.get('nama')
        tanggal = request.form.get('tanggal')
        jam = request.form.get('jam')
        no_rawat = request.form.get('no_rawat')
   

        # Analyze the image (PIL image passed here)
        analysis_results = analyze_image(image)

        # Save to memory and encode to base64
        buffered = io.BytesIO()
        image.save(buffered, format=image_format)
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
        image_data_uri = f"data:image/{image_format.lower()};base64,{encoded_image}"

        # Generate token
        session_token = str(uuid.uuid4())

        # Store session
        analysis_sessions[session_token] = {
            'image': image_data_uri,
            'results': analysis_results,
            'study_description': request.form.get('study_description', 'Radiology Scan'),
            'timestamp': datetime.now(),
            'viewed': False,
            'nama' : nama,
            'tanggal pemeriksaan' : tanggal,
            "jam" : jam,
            "no_rawat" : no_rawat,
        }

        view_url = url_for('view_analysis', token=session_token, _external=True)

        return jsonify({
            'status': 'success',
            'message': 'Image processed successfully',
            'view_url': view_url
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# halaman untuk menampilkan hasil analisis
@app.route('/view/<token>')
def view_analysis(token):
    """View analysis results - can only be viewed once"""
    if token not in analysis_sessions:
        return render_template('error.html', message="Analysis not found or has expired"), 404

    session_data = analysis_sessions[token]

    if session_data['viewed']:
        del analysis_sessions[token]
        return render_template('error.html', message="This analysis has already been viewed"), 403

    session_data['viewed'] = True

    return render_template('analysis.html',
        image_data=session_data['image'],
        results=session_data['results'],
        study_description=session_data['study_description'],
        timestamp=session_data['timestamp'],
        session_id=token
    )
    
@app.route('/download/<token>', methods=['GET'])
def download_pdf(token):
    if token not in analysis_sessions:
        return render_template('error.html', message="Data tidak ditemukan"), 404

    session_data = analysis_sessions[token]

    try:
        # Buat PDF dari session_data (kamu harus implementasi `buat_pdf`)
        pdf_bytes = buat_pdf(session_data)
        nama = session_data['nama']
        nama = session_data.get('nama', 'null')
    # Bersihkan nama dari karakter yang tidak valid di nama file
        safe_nama = re.sub(r'[^\w\s-]', '', nama).strip().replace(' ', '_')

        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename=hasil_radiologi_{safe_nama}.pdf'
            }
        )
    
        
    except Exception as e:
        return render_template('error.html', message=f"Gagal membuat PDF: {e}"), 500



# api untuk membersihkan sesi
@app.route('/api/cleanup/<token>', methods=['POST'])
def cleanup_session(token):
    """Explicit cleanup endpoint called when user leaves the page"""
    if token in analysis_sessions:
        del analysis_sessions[token]
    return '', 204

# api untuk membersihkan sesi yang sudah kadaluarsa
@app.before_request
def cleanup_expired_sessions():
    """Remove sessions older than 15 minutes"""
    current_time = datetime.now()
    expiration_time = timedelta(minutes=15)

    expired_tokens = [token for token, data in analysis_sessions.items()
                      if current_time - data['timestamp'] > expiration_time]

    for token in expired_tokens:
        if token in analysis_sessions:
            del analysis_sessions[token]

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
