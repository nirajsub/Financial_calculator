from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from ai_coach import coach

coach_bp = Blueprint('coach', __name__)

@coach_bp.route('/coach')
def ai_coach():
    return render_template('coach.html')

@coach_bp.route('/api/coach/chat', methods=['POST'])
def coach_chat():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id or not message:
            return jsonify({
                'success': False,
                'error': 'Missing session_id or message'
            }), 400
        
        result = coach.chat(session_id, message)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coach_bp.route('/api/coach/context', methods=['POST'])
def coach_context():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        context = data.get('context', {})
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        coach.add_user_context(session_id, context)
        
        return jsonify({
            'success': True,
            'message': 'Context updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coach_bp.route('/api/coach/suggestions', methods=['POST'])
def coach_suggestions():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        suggestions = coach.suggest_questions(session_id)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coach_bp.route('/api/coach/clear', methods=['POST'])
def coach_clear():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        coach.clear_conversation(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Conversation cleared successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coach_bp.route('/api/coach/summary', methods=['POST'])
def coach_summary():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        summary = coach.get_conversation_summary(session_id)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@coach_bp.route('/api/coach/import-calculation', methods=['POST'])
def coach_import_calculation():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        calculation_data = data.get('calculation_data')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        if not calculation_data:
            return jsonify({
                'success': False,
                'error': 'Missing calculation_data'
            }), 400
        
        context_update = {}
        
        if 'total_capital' in calculation_data:
            context_update['total_capital'] = calculation_data['total_capital']
        
        if 'monthly_income' in calculation_data:
            context_update['monthly_income'] = calculation_data['monthly_income']
        
        if 'monthly_expense_allocation' in calculation_data:
            context_update['monthly_expenses'] = calculation_data['monthly_expense_allocation']
        
        if 'investment_allocation' in calculation_data:
            context_update['investment_allocation'] = calculation_data['investment_allocation']
        
        if 'annual_return_rate' in calculation_data:
            context_update['annual_return_rate'] = calculation_data['annual_return_rate'] * 100
        
        if 'savings_return_rate' in calculation_data:
            context_update['savings_return_rate'] = calculation_data['savings_return_rate'] * 100
        
        if 'years' in calculation_data:
            context_update['years'] = calculation_data['years']
        
        if 'years_of_active_income' in calculation_data:
            context_update['years_of_active_income'] = calculation_data['years_of_active_income']
        
        if 'investment_goal' in calculation_data:
            context_update['investment_goal'] = calculation_data['investment_goal']
        
        if 'results' in calculation_data or 'summary' in calculation_data:
            context_update['calculation_results'] = {
                'results': calculation_data.get('results', []),
                'summary': calculation_data.get('summary', {}),
                'imported_at': datetime.now().isoformat()
            }
        
        coach.add_user_context(session_id, context_update)
        
        return jsonify({
            'success': True,
            'message': 'Calculation results imported successfully',
            'context_fields': len(context_update)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
