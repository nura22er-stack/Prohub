from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from bot.database import Database
from bot.config import API_PORT, API_HOST

app = Flask(__name__)
CORS(app)

db = Database()


@app.route('/', methods=['GET'])
def index():
    """Basic deployment status page."""
    return jsonify({
        "service": "ProHub Bot",
        "status": "ok",
        "health": "/health",
        "stats": "/api/stats"
    })


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


@app.route('/api/apps/<code>', methods=['GET'])
def get_app(code):
    """Get app by code"""
    app = db.get_app_by_code(code)
    
    if not app:
        return jsonify({"error": "App not found"}), 404
    
    return jsonify(app)


@app.route('/api/apps/search', methods=['GET'])
def search_apps():
    """Search apps by name"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"error": "Search query required"}), 400
    
    apps = db.get_app_by_name(query)
    return jsonify({"results": apps, "count": len(apps)})


@app.route('/api/top-apps', methods=['GET'])
def top_apps():
    """Get top downloaded apps"""
    limit = request.args.get('limit', 5, type=int)
    apps = db.get_top_apps(limit)
    return jsonify({"apps": apps})


@app.route('/api/stats/downloads', methods=['GET'])
def download_stats():
    """Get download statistics"""
    apps = db.get_all_apps()
    
    stats = {
        "total_downloads": sum(app["downloads"] for app in apps),
        "most_downloaded": sorted(apps, key=lambda x: x["downloads"], reverse=True)[:5],
        "least_downloaded": sorted(apps, key=lambda x: x["downloads"])[:5]
    }
    
    return jsonify(stats)


@app.route('/api/users/count', methods=['GET'])
def user_count():
    """Get total users"""
    users = db.get_all_users()
    return jsonify({"count": len(users)})


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT, debug=False, use_reloader=False)
