from flask import Flask, render_template, jsonify, send_file
import os
from lead_gen import run_generation

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate')
def generate_leads():
    try:
        leads = run_generation()
        return jsonify({"status": "success", "data": leads})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/download/excel')
def download_excel():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'leads_output.xlsx')
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"status": "error", "message": "File not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/download/csv')
def download_csv():
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'leads_output.csv')
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"status": "error", "message": "File not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
