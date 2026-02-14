# app/routes/help.py - COMPLETE VERSION with all guide routes
"""
Help and documentation routes
Version: 1.0.0
"""
from flask import Blueprint, render_template, request, jsonify, abort
from app.models import Settings, Log
import markdown
import os
from app import mongo
from datetime import datetime
from bson import ObjectId

help_bp = Blueprint('help', __name__)


class ContactMessage:
    """Contact message model"""
    
    @staticmethod
    def create(data):
        """Save contact message to database"""
        data['created_at'] = datetime.now()
        data['status'] = 'unread'  # unread, read, replied
        
        # Ensure required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if field not in data:
                data[field] = ''
        
        result = mongo.db.contact_messages.insert_one(data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all(filters=None, page=1, per_page=20):
        """Get all contact messages"""
        query = filters or {}
        skip = (page - 1) * per_page
        
        messages = list(mongo.db.contact_messages.find(query)
                       .sort('created_at', -1)
                       .skip(skip)
                       .limit(per_page))
        
        total = mongo.db.contact_messages.count_documents(query)
        
        for msg in messages:
            msg['id'] = str(msg['_id'])
            del msg['_id']
        
        return {
            'items': messages,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def update_status(message_id, status):
        """Update message status"""
        result = mongo.db.contact_messages.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': {'status': status, 'updated_at': datetime.now()}}
        )
        return result.modified_count > 0

@help_bp.route('/')
def index():
    """Help center homepage"""
    return render_template('help/index.html')

@help_bp.route('/guides')
def guides():
    """All guides listing page"""
    return render_template('help/guides/index.html')

@help_bp.route('/guide/<topic>')
def guide(topic):
    """Individual guide pages"""
    valid_topics = [
        'getting-started',
        'transactions', 
        'accounts',
        'budgets',
        'categories',
        'export',
        'api',
        'filters',
        'reports',
        'troubleshooting',
        'timezone-settings',
        'date-formatting',
        'dark-mode',     
        'number-formats',
        'currency-settings'
    ]
    
    if topic not in valid_topics:
        abort(404)
    
    return render_template(f'help/guides/{topic}.html')

@help_bp.route('/faq')
def faq():
    """Frequently Asked Questions page"""
    return render_template('help/faq.html')

@help_bp.route('/api-docs')
def api_docs():
    """API documentation page"""
    return render_template('help/guides/api.html')

@help_bp.route('/search')
def search_help():
    """Search help documentation"""
    query = request.args.get('q', '').lower().strip()
    
    if not query or len(query) < 2:
        return jsonify({'success': True, 'results': []})
    
    # Help topics database
    topics = [
        {
            'id': 'getting-started',
            'title': 'Getting Started with Expense Tracker',
            'description': 'Learn the basics of setting up your account and first transaction',
            'keywords': ['start', 'begin', 'first', 'setup', 'initial', 'create account'],
            'category': 'guide'
        },
        {
            'id': 'transactions',
            'title': 'Managing Transactions',
            'description': 'How to add, edit, delete, and filter transactions',
            'keywords': ['transaction', 'add', 'edit', 'delete', 'remove', 'update', 'filter'],
            'category': 'guide'
        },
        {
            'id': 'accounts',
            'title': 'Account Management',
            'description': 'Create and manage different types of financial accounts',
            'keywords': ['account', 'balance', 'credit card', 'bank', 'asset', 'liability'],
            'category': 'guide'
        },
        {
            'id': 'budgets',
            'title': 'Budget Planning',
            'description': 'Set spending limits and track your budget progress',
            'keywords': ['budget', 'spending', 'track', 'limit', 'period', 'monthly'],
            'category': 'guide'
        },
        {
            'id': 'categories',
            'title': 'Category Management',
            'description': 'Organize transactions with custom categories',
            'keywords': ['category', 'organize', 'group', 'tag', 'classify'],
            'category': 'guide'
        },
        {
            'id': 'export',
            'title': 'Exporting Data',
            'description': 'Export your financial data to CSV, JSON, or Excel',
            'keywords': ['export', 'download', 'csv', 'excel', 'json', 'backup'],
            'category': 'guide'
        },
        {
            'id': 'api',
            'title': 'API Integration',
            'description': 'Use the Expense Tracker API for third-party integration',
            'keywords': ['api', 'rest', 'endpoint', 'developer', 'integration'],
            'category': 'guide'
        },
        {
            'id': 'filters',
            'title': 'Using Filters',
            'description': 'Advanced filtering options for finding transactions',
            'keywords': ['filter', 'search', 'find', 'date range', 'category filter'],
            'category': 'guide'
        },
        {
            'id': 'reports',
            'title': 'Reports & Analytics',
            'description': 'Generate financial reports and analyze spending patterns',
            'keywords': ['report', 'chart', 'graph', 'analytics', 'insights'],
            'category': 'guide'
        },
        {
            'id': 'troubleshooting',
            'title': 'Troubleshooting Common Issues',
            'description': 'Solutions for common problems and error messages',
            'keywords': ['error', 'problem', 'issue', 'fix', 'help', 'support'],
            'category': 'guide'
        }
    ]
    
    # Search in topics
    results = []
    for topic in topics:
        # Search in title
        if query in topic['title'].lower():
            results.append(topic)
            continue
        
        # Search in keywords
        if any(query in kw for kw in topic['keywords']):
            results.append(topic)
            continue
        
        # Search in description
        if query in topic['description'].lower():
            results.append(topic)
            continue
    
    # Search in FAQs
    faqs = [
        {
            'id': 'faq-1',
            'title': 'How do I add my first transaction?',
            'description': 'Step-by-step guide to add your first income or expense',
            'keywords': ['add transaction', 'first transaction', 'create transaction'],
            'category': 'faq'
        },
        {
            'id': 'faq-2',
            'title': 'How do I create a budget?',
            'description': 'Learn how to set up and manage budgets',
            'keywords': ['create budget', 'set budget', 'budget setup'],
            'category': 'faq'
        },
        {
            'id': 'faq-3',
            'title': 'Can I export my data?',
            'description': 'Export your financial data in various formats',
            'keywords': ['export data', 'download data', 'backup'],
            'category': 'faq'
        },
        {
            'id': 'faq-4',
            'title': 'How are budgets calculated?',
            'description': 'Understanding how budget spending is calculated',
            'keywords': ['budget calculation', 'spent amount', 'budget tracking'],
            'category': 'faq'
        },
        {
            'id': 'faq-5',
            'title': 'What account types are supported?',
            'description': 'Overview of all supported account types',
            'keywords': ['account types', 'credit card', 'bank account'],
            'category': 'faq'
        }
    ]
    
    for faq in faqs:
        if (query in faq['title'].lower() or 
            query in faq['description'].lower() or 
            any(query in kw for kw in faq['keywords'])):
            results.append(faq)
    
    # Log search query
    Log.create({
        'level': 'INFO',
        'category': 'HELP_SEARCH',
        'message': f'Help search: {query}',
        'details': {'query': query, 'results': len(results)}
    })
    
    return jsonify({
        'success': True,
        'query': query,
        'results': results[:10]  # Limit to 10 results
    })

@help_bp.route('/api/search')
def search_api():
    """API documentation search"""
    query = request.args.get('q', '').lower()
    
    api_endpoints = [
        {'path': '/transactions', 'method': 'GET', 'description': 'List transactions'},
        {'path': '/transactions', 'method': 'POST', 'description': 'Create transaction'},
        {'path': '/transactions/{id}', 'method': 'GET', 'description': 'Get transaction'},
        {'path': '/transactions/{id}', 'method': 'PUT', 'description': 'Update transaction'},
        {'path': '/transactions/{id}', 'method': 'DELETE', 'description': 'Delete transaction'},
        {'path': '/accounts', 'method': 'GET', 'description': 'List accounts'},
        {'path': '/accounts', 'method': 'POST', 'description': 'Create account'},
        {'path': '/budgets', 'method': 'GET', 'description': 'List budgets'},
        {'path': '/categories', 'method': 'GET', 'description': 'List categories'},
        {'path': '/reports/summary', 'method': 'GET', 'description': 'Financial summary'}
    ]
    
    results = []
    for endpoint in api_endpoints:
        if (query in endpoint['path'].lower() or 
            query in endpoint['description'].lower()):
            results.append(endpoint)
    
    return jsonify({
        'success': True,
        'results': results
    })

@help_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit help feedback"""
    try:
        data = request.get_json()
        
        Log.create({
            'level': 'FEEDBACK',
            'category': 'HELP_FEEDBACK',
            'message': f'Help feedback: {data.get("type", "general")}',
            'details': {
                'guide': data.get('guide'),
                'rating': data.get('rating'),
                'feedback': data.get('feedback')
            }
        })
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@help_bp.route('/glossary')
def glossary():
    """Financial terms glossary"""
    return render_template('help/glossary.html')

@help_bp.route('/shortcuts')
def shortcuts():
    """Keyboard shortcuts"""
    shortcuts = [
        {'key': 'Ctrl + N', 'description': 'New transaction', 'category': 'Global'},
        {'key': 'Ctrl + F', 'description': 'Focus search', 'category': 'Global'},
        {'key': 'Ctrl + E', 'description': 'Export data', 'category': 'Global'},
        {'key': 'Ctrl + H', 'description': 'Help center', 'category': 'Global'},
        {'key': 'Ctrl + D', 'description': 'Dashboard', 'category': 'Navigation'},
        {'key': 'Ctrl + T', 'description': 'Transactions', 'category': 'Navigation'},
        {'key': 'Ctrl + A', 'description': 'Accounts', 'category': 'Navigation'},
        {'key': 'Ctrl + B', 'description': 'Budgets', 'category': 'Navigation'},
        {'key': 'Ctrl + G', 'description': 'Categories', 'category': 'Navigation'},
        {'key': 'Ctrl + L', 'description': 'Logs', 'category': 'Navigation'},
        {'key': 'Esc', 'description': 'Close modal', 'category': 'UI'},
        {'key': '/', 'description': 'Quick search', 'category': 'UI'},
        {'key': '?', 'description': 'Show shortcuts', 'category': 'UI'}
    ]
    
    return jsonify({
        'success': True,
        'data': shortcuts
    })

@help_bp.route('/system-info')
def system_info():
    """System information"""
    try:
        from flask import __version__ as flask_version
        import pymongo
        import platform
        import sys
        
        info = {
            'application': {
                'name': Settings.get('app_name', 'Expense Tracker System'),
                'version': Settings.get('app_version', '1.0.0'),
                'environment': os.getenv('FLASK_ENV', 'development'),
                'debug': os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
            },
            'python': {
                'version': platform.python_version(),
                'implementation': platform.python_implementation(),
                'path': sys.executable
            },
            'flask': {
                'version': flask_version
            },
            'mongodb': {
                'status': 'connected',
                'database': mongo.db.name
            },
            'system': {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'hostname': platform.node(),
                'cpu_count': os.cpu_count()
            },
            'paths': {
                'static': os.path.abspath('app/static'),
                'templates': os.path.abspath('app/templates'),
                'data': os.path.abspath('data')
            }
        }
        
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@help_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact support page"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['name', 'email', 'subject', 'message']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({
                        'success': False, 
                        'error': f'{field} is required'
                    }), 400
            
            # Save to database
            message_id = ContactMessage.create(data)
            
            # Log the action
            Log.create({
                'level': 'CONTACT',
                'category': 'CONTACT_FORM',
                'message': f'Contact form submitted by {data["name"]}',
                'details': {
                    'message_id': message_id,
                    'name': data['name'],
                    'email': data['email'],
                    'subject': data['subject']
                }
            })
            
            # Optional: Send email notification
            # send_email_notification(data)
            
            return jsonify({
                'success': True,
                'message': 'Your message has been sent. We\'ll respond within 24 hours.',
                'message_id': message_id
            }), 201
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        
    return render_template('help/contact.html')

# Add after the existing routes (around line 300)

@help_bp.route('/guide/timezone-settings')
def guide_timezone():
    """Guide for timezone settings"""
    return render_template('help/guides/timezone-settings.html')

@help_bp.route('/guide/date-formatting')
def guide_date_formatting():
    """Guide for date formatting options"""
    return render_template('help/guides/date-formatting.html')

@help_bp.route('/guide/dark-mode')
def guide_dark_mode():
    """Guide for dark mode customization"""
    return render_template('help/guides/dark-mode.html')

@help_bp.route('/guide/number-formats')
def guide_number_formats():
    """Guide for number formatting options"""
    return render_template('help/guides/number-formats.html')