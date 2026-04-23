FROM python:3.12-slim

WORKDIR /app

EXPOSE 8001

# Inference service — stub only. No application code yet.
CMD ["python", "-c", "import http.server, os; http.server.HTTPServer(('', int(os.getenv('PORT','8001'))), http.server.BaseHTTPRequestHandler).serve_forever()"]
