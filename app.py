from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import qrcode
import io
import base64
from datetime import datetime
import requests
import json

app = Flask(__name__)

# HTML Template for the webapp
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Equipment QR System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        h1 {
            text-align: center;
            color: #4a5568;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 300;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        h2 {
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 400;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #4a5568;
        }

        input[type="text"], input[type="url"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.8);
        }

        input[type="text"]:focus, input[type="url"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-1px);
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            min-width: 150px;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }

        .btn-option {
            margin: 10px;
            padding: 25px 40px;
            font-size: 20px;
            border-radius: 15px;
            min-width: 200px;
            transition: all 0.3s ease;
        }

        .btn-training {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }

        .btn-training:hover {
            box-shadow: 0 15px 35px rgba(17, 153, 142, 0.4);
        }

        .btn-maintenance {
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            color: #2d3748;
        }

        .btn-maintenance:hover {
            box-shadow: 0 15px 35px rgba(250, 177, 160, 0.4);
        }

        .btn-repair {
            background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
        }

        .btn-repair:hover {
            box-shadow: 0 15px 35px rgba(252, 70, 107, 0.4);
        }

        .equipment-info {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            font-size: 20px;
            font-weight: 600;
            color: #2d3748;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .options-container {
            text-align: center;
            padding: 40px 20px;
        }

        .options-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }

        .qr-display {
            text-align: center;
            margin-top: 30px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 15px;
            border: 2px dashed #cbd5e0;
        }

        .qr-display img {
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .status-message {
            padding: 15px;
            border-radius: 12px;
            margin: 20px 0;
            font-weight: 600;
            text-align: center;
        }

        .status-success {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status-error {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .loading {
            display: none;
            text-align: center;
            color: #667eea;
            font-weight: 600;
        }

        .config-section {
            background: rgba(255, 255, 255, 0.3);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .card {
                padding: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .btn-option {
                margin: 10px 5px;
                padding: 20px 30px;
                font-size: 18px;
                min-width: 180px;
            }

            .options-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🔧 Equipment Management System</h1>
            
            {% if mode == 'generator' %}
            <!-- QR Generator Section -->
            <h2>📱 Generate QR Code</h2>
            
            <div class="config-section">
                <h3 style="margin-bottom: 15px; color: #4a5568;">⚙️ Configuration</h3>
                <form method="POST" action="/generate">
                    <div class="form-group">
                        <label for="crm_api_url">CRM API URL:</label>
                        <input type="url" id="crm_api_url" name="crm_api_url" 
                               placeholder="https://your-crm.com/api/webhook" 
                               value="{{ crm_api_url or 'https://your-crm.com/api/webhook' }}" required>
                    </div>
                    <div class="form-group">
                        <label for="api_key">API Key:</label>
                        <input type="text" id="api_key" name="api_key" 
                               placeholder="your-api-key-here" 
                               value="{{ api_key or 'your-api-key-here' }}" required>
                    </div>
                    <div class="form-group">
                        <label for="equipment_id">Equipment ID:</label>
                        <input type="text" id="equipment_id" name="equipment_id" 
                               placeholder="Enter equipment ID (e.g., EQP-001)" required>
                    </div>
                    
                    <button type="submit" class="btn">🚀 Generate QR Code</button>
                </form>
            </div>
            
            {% if qr_code %}
            <div class="qr-display">
                <img src="data:image/png;base64,{{ qr_code }}" alt="QR Code">
                <p style="margin-top: 15px; color: #4a5568;">
                    Scan this QR code to access equipment options for: <strong>{{ equipment_id }}</strong>
                </p>
            </div>
            {% endif %}
            
            {% elif mode == 'scanner' %}
            <!-- Scanner Result Section -->
            <div class="equipment-info">
                🏭 Equipment ID: <span style="color: #667eea;">{{ equipment_id }}</span>
            </div>
            
            <div class="options-container">
                <h2>Select Service Type:</h2>
                <p style="margin-bottom: 30px; color: #666; font-size: 18px;">
                    What type of service does this equipment need?
                </p>
                
                <div class="options-grid">
                    <button class="btn btn-option btn-training" onclick="selectService('training')">
                        📚 Training<br>
                        <small style="font-weight: 400; font-size: 14px; opacity: 0.8;">
                            Equipment operation training
                        </small>
                    </button>
                    
                    <button class="btn btn-option btn-maintenance" onclick="selectService('maintenance')">
                        🔧 Maintenance<br>
                        <small style="font-weight: 400; font-size: 14px; opacity: 0.8;">
                            Routine maintenance service
                        </small>
                    </button>
                    
                    <button class="btn btn-option btn-repair" onclick="selectService('repair')">
                        ⚠️ Repair<br>
                        <small style="font-weight: 400; font-size: 14px; opacity: 0.8;">
                            Equipment repair needed
                        </small>
                    </button>
                </div>
                
                <div class="loading" id="loading">
                    <p>📤 Sending request to CRM...</p>
                </div>
            </div>
            {% endif %}
            
            <div id="statusMessage">
                {% if message %}
                <div class="status-message status-{{ message_type }}">{{ message }}</div>
                {% endif %}
            </div>
        </div>
    </div>

    {% if mode == 'scanner' %}
    <script>
        async function selectService(serviceType) {
            const loading = document.getElementById('loading');
            const statusDiv = document.getElementById('statusMessage');
            const buttons = document.querySelectorAll('.btn-option');
            
            // Show loading
            loading.style.display = 'block';
            buttons.forEach(btn => btn.disabled = true);
            
            const payload = {
                equipment_id: '{{ equipment_id }}',
                service_type: serviceType,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                location: window.location.href
            };
            
            try {
                const response = await fetch('/submit_service', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = `
                        <div class="status-message status-success">
                            ✅ ${getServiceEmoji(serviceType)} ${serviceType.toUpperCase()} request submitted successfully!<br>
                            Equipment: {{ equipment_id }}
                        </div>
                    `;
                    
                    // Visual feedback
                    buttons.forEach(btn => {
                        if (btn.onclick.toString().includes(serviceType)) {
                            btn.style.transform = 'scale(1.05)';
                            btn.style.boxShadow = '0 20px 40px rgba(102, 126, 234, 0.5)';
                        } else {
                            btn.style.opacity = '0.5';
                        }
                    });
                    
                } else {
                    throw new Error(result.error || 'Failed to submit request');
                }
            } catch (error) {
                console.error('Error:', error);
                statusDiv.innerHTML = `
                    <div class="status-message status-error">
                        ❌ Failed to submit request: ${error.message}
                    </div>
                `;
            } finally {
                loading.style.display = 'none';
                
                // Re-enable buttons after 3 seconds
                setTimeout(() => {
                    buttons.forEach(btn => {
                        btn.disabled = false;
                        btn.style.opacity = '1';
                        btn.style.transform = 'scale(1)';
                        btn.style.boxShadow = '';
                    });
                }, 3000);
            }
        }
        
        function getServiceEmoji(serviceType) {
            const emojis = {
                'training': '📚',
                'maintenance': '🔧', 
                'repair': '⚠️'
            };
            return emojis[serviceType] || '🔧';
        }
    </script>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    """Main page - can be generator or scanner based on URL parameters"""
    equipment_id = request.args.get('equipment_id')
    crm_api_url = request.args.get('api_url')
    api_key = request.args.get('api_key')
    
    if equipment_id and crm_api_url and api_key:
        # This is a scanned QR code - show service options
        return render_template_string(HTML_TEMPLATE, 
                                    mode='scanner',
                                    equipment_id=equipment_id,
                                    crm_api_url=crm_api_url,
                                    api_key=api_key)
    else:
        # Show QR generator
        return render_template_string(HTML_TEMPLATE, mode='generator')

@app.route('/generate', methods=['POST'])
def generate_qr():
    """Generate QR code with equipment details"""
    equipment_id = request.form.get('equipment_id')
    crm_api_url = request.form.get('crm_api_url')
    api_key = request.form.get('api_key')
    
    if not all([equipment_id, crm_api_url, api_key]):
        return render_template_string(HTML_TEMPLATE, 
                                    mode='generator',
                                    message='All fields are required',
                                    message_type='error')
    
    try:
        # Create QR code URL
        base_url = request.url_root.rstrip('/')
        qr_url = f"{base_url}/?equipment_id={equipment_id}&api_url={crm_api_url}&api_key={api_key}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for display
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return render_template_string(HTML_TEMPLATE,
                                    mode='generator',
                                    qr_code=qr_code_base64,
                                    equipment_id=equipment_id,
                                    crm_api_url=crm_api_url,
                                    api_key=api_key,
                                    message='QR Code generated successfully! 🎉',
                                    message_type='success')
        
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
                                    mode='generator',
                                    message=f'Error generating QR code: {str(e)}',
                                    message_type='error')

@app.route('/submit_service', methods=['POST'])
def submit_service():
    """Handle service request submission to CRM"""
    try:
        data = request.get_json()
        equipment_id = data.get('equipment_id')
        service_type = data.get('service_type')
        
        # Get CRM details from URL parameters (stored in session or passed)
        crm_api_url = request.args.get('api_url') or data.get('crm_api_url')
        api_key = request.args.get('api_key') or data.get('api_key')
        
        # Prepare payload for CRM
        crm_payload = {
            'equipment_id': equipment_id,
            'service_type': service_type.upper(),
            'timestamp': data.get('timestamp'),
            'user_agent': data.get('user_agent'),
            'status': 'REQUESTED',
            'priority': get_service_priority(service_type),
            'metadata': {
                'source': 'QR_SCAN',
                'location': data.get('location', ''),
                'request_id': f"{equipment_id}_{service_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        }
        
        # Send to CRM (mock for now - replace with actual CRM endpoint)
        print(f"📤 Sending to CRM: {crm_api_url}")
        print(f"📋 Payload: {json.dumps(crm_payload, indent=2)}")
        
        # Uncomment below to send actual HTTP request to CRM
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'X-API-Key': api_key
        }
        
        response = requests.post(crm_api_url, json=crm_payload, headers=headers, timeout=30)
        
        if not response.ok:
            raise Exception(f"CRM API returned {response.status_code}: {response.text}")
        """
        
        # Log the request
        log_service_request(equipment_id, service_type, crm_payload)
        
        return jsonify({
            'success': True,
            'message': f'{service_type.upper()} request submitted successfully',
            'equipment_id': equipment_id,
            'service_type': service_type,
            'request_id': crm_payload['metadata']['request_id']
        })
        
    except Exception as e:
        print(f"❌ Error submitting service request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_service_priority(service_type):
    """Determine priority based on service type"""
    priority_map = {
        'repair': 'HIGH',
        'maintenance': 'MEDIUM', 
        'training': 'LOW'
    }
    return priority_map.get(service_type.lower(), 'MEDIUM')

def log_service_request(equipment_id, service_type, payload):
    """Log service request to file or database"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'equipment_id': equipment_id,
        'service_type': service_type,
        'payload': payload
    }
    
    try:
        with open('service_requests.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        print(f"📝 Logged request: {equipment_id} - {service_type}")
    except Exception as e:
        print(f"⚠️ Failed to log request: {str(e)}")

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting Equipment QR Management System...")
    print("📱 Generator: http://localhost:5000/")
    print("🏥 Health Check: http://localhost:5000/health")
    print("📋 Service Logs: service_requests.log")
    
    app.run(debug=True, host='0.0.0.0', port=5000)