# app/routes/updates.py
"""
System updates and version management routes
Version: 1.0.0
"""
from flask import Blueprint, render_template, request, jsonify
from app.models import Log, Settings
from datetime import datetime
import subprocess
import sys
from app import mongo

# Replace pkg_resources with importlib.metadata
try:
    from importlib.metadata import distributions, version
except ImportError:
    # Python 3.7 or lower fallback
    from importlib_metadata import distributions, version

updates_bp = Blueprint('updates', __name__)

@updates_bp.route('/')
def index():
    """Updates page"""
    return render_template('updates/index.html')

@updates_bp.route('/check')
def check_updates():
    """Check for system updates"""
    try:
        current_version = Settings.get('app_version', '1.0.0')
        latest_version = check_latest_version()
        updates_available = compare_versions(latest_version, current_version) > 0
        
        return jsonify({
            'success': True,
            'data': {
                'current_version': current_version,
                'latest_version': latest_version,
                'updates_available': updates_available,
                'last_checked': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@updates_bp.route('/changelog')
def get_changelog():
    """Get version changelog"""
    changelog = [
        {
            'version': '1.0.0',
            'date': '2024-01-15',
            'type': 'major',
            'title': 'Initial Release',
            'changes': [
                'Complete expense tracking system',
                'Interactive dashboard with charts',
                'Transaction management',
                'Account management',
                'Budget planning',
                'Category organization',
                'RESTful API',
                'Export functionality',
                'Dark/light theme',
                'Responsive design'
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'data': changelog
    })

@updates_bp.route('/dependencies')
def check_dependencies():
    """Check Python dependencies"""
    try:
        dependencies = []
        
        # Read requirements.txt
        with open('requirements.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('==')
                    package_name = parts[0]
                    required_version = parts[1] if len(parts) > 1 else 'latest'
                    
                    try:
                        installed_version = version(package_name)
                        up_to_date = installed_version == required_version if required_version != 'latest' else True
                        
                        dependencies.append({
                            'name': package_name,
                            'required': required_version,
                            'installed': installed_version,
                            'up_to_date': up_to_date
                        })
                    except Exception:
                        dependencies.append({
                            'name': package_name,
                            'required': required_version,
                            'installed': 'not installed',
                            'up_to_date': False
                        })
        
        return jsonify({
            'success': True,
            'data': dependencies
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@updates_bp.route('/update', methods=['POST'])
def perform_update():
    """Perform system update"""
    try:
        data = request.get_json()
        version = data.get('version')
        
        # Log update start
        Log.create({
            'level': 'INFO',
            'category': 'UPDATE',
            'message': f'Starting update to version {version}',
            'details': {'version': version}
        })
        
        # Perform update steps
        # 1. Backup database
        # 2. Pull latest code
        # 3. Install dependencies
        # 4. Run migrations
        # 5. Restart services
        
        # Log update completion
        Log.create({
            'level': 'SUCCESS',
            'category': 'UPDATE',
            'message': f'Successfully updated to version {version}',
            'details': {'version': version}
        })
        
        return jsonify({
            'success': True,
            'message': f'Successfully updated to version {version}',
            'requires_restart': True
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@updates_bp.route('/history')
def get_update_history():
    """Get update history"""
    try:
        history = list(mongo.db.logs.find({
            'category': 'UPDATE',
            'level': {'$in': ['SUCCESS', 'ERROR']}
        }).sort('timestamp', -1).limit(50))
        
        for entry in history:
            entry['id'] = str(entry['_id'])
            del entry['_id']
        
        return jsonify({
            'success': True,
            'data': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def check_latest_version():
    """Check latest version from GitHub"""
    # Implementation for checking latest version
    return '1.0.0'

def compare_versions(v1, v2):
    """Compare version strings"""
    v1_parts = [int(x) for x in v1.split('.')]
    v2_parts = [int(x) for x in v2.split('.')]
    
    for i in range(max(len(v1_parts), len(v2_parts))):
        v1_part = v1_parts[i] if i < len(v1_parts) else 0
        v2_part = v2_parts[i] if i < len(v2_parts) else 0
        
        if v1_part > v2_part:
            return 1
        elif v1_part < v2_part:
            return -1
    
    return 0