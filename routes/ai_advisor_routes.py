from flask import Blueprint, render_template, request, jsonify
from utils.ai_recommendations import generate_smart_recommendations

ai_advisor_bp = Blueprint('ai_advisor', __name__)

@ai_advisor_bp.route('/ai-advisor')
def ai_advisor():
    return render_template('ai_advisor.html')

@ai_advisor_bp.route('/api/ai/recommendations', methods=['POST'])
def get_ai_recommendations():
    try:
        data = request.get_json()
        
        age = int(data.get('age', 30))
        risk_tolerance = data.get('riskTolerance', 'moderate')
        investment_goal = data.get('investmentGoal', 'retirement')
        time_horizon = int(data.get('timeHorizon', 10))
        current_capital = float(data.get('currentCapital', 0))
        monthly_income = float(data.get('monthlyIncome', 0))
        monthly_expenses = float(data.get('monthlyExpenses', 0))
        existing_debts = float(data.get('existingDebts', 0))
        emergency_fund = float(data.get('emergencyFund', 0))
        expected_return = float(data.get('expectedReturn', 8))
        current_allocation = data.get('currentAllocation', '')
        has_retirement_plan = data.get('hasRetirementPlan', False)
        has_health_insurance = data.get('hasHealthInsurance', False)
        willing_to_increase_savings = data.get('willingToIncreaseSavings', False)
        planning_major_purchase = data.get('planningMajorPurchase', False)
        specific_questions = data.get('specificQuestions', '')
        
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
        annual_savings = monthly_savings * 12
        emergency_fund_months = emergency_fund
        recommended_emergency_months = 6
        debt_to_income = (existing_debts / (monthly_income * 12) * 100) if monthly_income > 0 else 0
        
        annual_return_rate = expected_return / 100
        future_value = current_capital
        yearly_projections = []
        
        for year in range(1, time_horizon + 1):
            future_value = (future_value + annual_savings) * (1 + annual_return_rate)
            yearly_projections.append({
                'year': year,
                'value': round(future_value, 2)
            })
        
        final_value = future_value
        total_invested = current_capital + (annual_savings * time_horizon)
        total_returns = final_value - total_invested
        
        recommendations = generate_smart_recommendations(
            age=age,
            risk_tolerance=risk_tolerance,
            investment_goal=investment_goal,
            time_horizon=time_horizon,
            current_capital=current_capital,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            monthly_savings=monthly_savings,
            savings_rate=savings_rate,
            existing_debts=existing_debts,
            emergency_fund_months=emergency_fund_months,
            expected_return=expected_return,
            has_retirement_plan=has_retirement_plan,
            has_health_insurance=has_health_insurance,
            willing_to_increase_savings=willing_to_increase_savings,
            planning_major_purchase=planning_major_purchase,
            debt_to_income=debt_to_income,
            final_value=final_value,
            total_invested=total_invested,
            total_returns=total_returns,
            current_allocation=current_allocation
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'projections': yearly_projections,
            'metrics': {
                'monthly_savings': round(monthly_savings, 2),
                'savings_rate': round(savings_rate, 2),
                'annual_savings': round(annual_savings, 2),
                'final_value': round(final_value, 2),
                'total_invested': round(total_invested, 2),
                'total_returns': round(total_returns, 2),
                'emergency_fund_months': emergency_fund_months,
                'debt_to_income': round(debt_to_income, 2)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
