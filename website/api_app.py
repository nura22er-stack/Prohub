from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bot.database import Database

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
CORS(app)

db = Database()


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get bot statistics"""
    stats = db.get_stats()
    return jsonify(stats)


@app.route('/api/apps', methods=['GET'])
def get_apps():
    """Get all apps"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    apps, total_pages = db.get_apps_paginated(page, per_page)
    
    return jsonify({
        "apps": apps,
        "page": page,
        "total_pages": total_pages,
        "total": len(db.get_all_apps())
    })


@app.route('/api/top-apps', methods=['GET'])
def top_apps():
    """Get top downloaded apps"""
    limit = request.args.get('limit', 5, type=int)
    apps = db.get_top_apps(limit)
    return jsonify({"apps": apps})


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')), debug=False, use_reloader=False)
