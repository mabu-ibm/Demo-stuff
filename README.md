# Demo-stuff
Demo Apps Turbo, Instana, concert

🎯 Hauptfunktionen der Application:
Python Webserver (app.py):

Flask-basierter Webserver mit Web-Interface und REST API
Stress-ng Integration für CPU- und Memory-Load-Tests
Monitoring & Metriken für Turbonomic und Instana
Tracing-ready mit strukturierten Logs und Metriken-Endpoints

Key Features:

⚡ Stress Tests: Konfigurierbare CPU/Memory-Load mit stress-ng
📊 Metriken: Real-time System- und Application-Metriken
🌐 Web Interface: Benutzerfreundliche Oberfläche für Tests
🔍 Health Checks: Kubernetes-ready Liveness/Readiness Probes
🎛️ API Endpoints: REST API für automatisierte Tests


Python App
----------------------------------------
Python-Programm mit einem Webserver, der Stress-ng für Lasttests aufruft und für Tracing mit Instana und Turbonomic vorbereitet ist.
app.py :

API Endpoints
GET /health</code> - Health Check
GET /metrics</code> - System Metriken
POST /stress</code> - Stress Test starten
GET /status</code> - Aktueller Status


Create Push Docker Image 
-----------------------
# 1. DockerHub Login
docker login --username mbx1010

# 2. Image bauen
docker build -t load-test-app:latest .

# 3. Für DockerHub taggen
docker tag load-test-app:latest mbx1010/load-test-app:latest

# 4. Zu DockerHub pushen
docker push mbx1010/load-test-app:latest

# 5. Kubernetes Manifest aktualisieren (in k8s-manifests.yaml)
# Ändere: image: load-test-app:latest
# Zu:     image: mbx1010/load-test-app:latest
