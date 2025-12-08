from flask import Flask, render_template, request, jsonify
import json
from decouple import config
from finance import FinancialManager

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        # Extract parameters from request
        total_capital = float(data.get('total_capital', 20000000))
        annual_return_rate = float(data.get('annual_return_rate', 20)) / 100
        savings_return_rate = float(data.get('savings_return_rate', 4)) / 100
        monthly_expense_allocation = float(data.get('monthly_expense_allocation', 150000))
        expense_utilization_rate = float(data.get('expense_utilization_rate', 80)) / 100
        annual_expense_increase_rate = float(data.get('annual_expense_increase_rate', 10)) / 100
        years = int(data.get('years', 5))
        
        # Extract emergency withdrawals if provided
        emergency_withdrawals_list = data.get('emergency_withdrawals', [])
        emergency_withdrawals = {}
        for withdrawal in emergency_withdrawals_list:
            year = int(withdrawal.get('year'))
            amount = float(withdrawal.get('amount'))
            if 1 <= year <= years and amount > 0:
                emergency_withdrawals[year] = amount
        
        # Extract expense utilization overrides if provided
        expense_utilization_overrides_list = data.get('expense_utilization_overrides', [])
        expense_utilization_overrides = []
        for override in expense_utilization_overrides_list:
            start_year = int(override.get('start_year'))
            end_year = int(override.get('end_year'))
            rate = float(override.get('rate')) / 100
            reason = override.get('reason', 'Custom override')
            if 1 <= start_year <= years and start_year <= end_year:
                expense_utilization_overrides.append({
                    'start_year': start_year,
                    'end_year': min(end_year, years),
                    'rate': rate,
                    'reason': reason
                })
        
        # Create financial manager and calculate
        fm = FinancialManager()
        
        # Calculate results
        results = []
        
        # Initial allocation
        investment_capital = total_capital * 0.75
        savings_capital = total_capital * 0.25
        yearly_expense_allocation = monthly_expense_allocation * 12
        
        # Store initial values for growth calculation
        initial_investment = investment_capital
        initial_savings = savings_capital
        initial_total = total_capital
        
        # Calculate for each year
        for year in range(1, years + 1):
            # Determine expense utilization rate for this year
            current_utilization_rate = expense_utilization_rate
            utilization_reason = "Default"
            
            if expense_utilization_overrides:
                for override in expense_utilization_overrides:
                    start = override.get('start_year', 1)
                    end = override.get('end_year', years)
                    if start <= year <= end:
                        current_utilization_rate = override.get('rate', expense_utilization_rate)
                        utilization_reason = override.get('reason', 'Custom override')
                        break
            
            investment_capital_start = investment_capital
            savings_capital_start = savings_capital
            
            # Calculate returns
            investment_return = investment_capital_start * annual_return_rate
            savings_return = savings_capital_start * savings_return_rate
            total_returns = investment_return + savings_return
            
            # Handle expense allocation
            expense_from_investment = 0
            expense_from_savings = 0
            remaining_investment_return = 0
            remaining_savings_return = 0
            expense_from_returns = 0
            deficit_covered_from_savings = 0
            
            if total_returns < yearly_expense_allocation:
                # Insufficient returns
                deficit = yearly_expense_allocation - total_returns
                if savings_capital >= deficit:
                    savings_capital -= deficit
                    deficit_covered_from_savings = deficit
                    expense_from_returns = yearly_expense_allocation
                else:
                    expense_from_returns = total_returns + savings_capital
                    deficit_covered_from_savings = savings_capital
                    savings_capital = 0
            else:
                # Sufficient returns
                if investment_return >= yearly_expense_allocation:
                    expense_from_investment = yearly_expense_allocation
                    expense_from_savings = 0
                    remaining_investment_return = investment_return - yearly_expense_allocation
                    remaining_savings_return = savings_return
                else:
                    expense_from_investment = investment_return
                    expense_from_savings = yearly_expense_allocation - investment_return
                    remaining_investment_return = 0
                    remaining_savings_return = savings_return - expense_from_savings
                
                expense_from_returns = yearly_expense_allocation
            
            # Calculate actual expenses and savings
            actual_expense = expense_from_returns * current_utilization_rate
            savings_from_expense = expense_from_returns * (1 - current_utilization_rate)
            
            # Update capitals
            investment_capital += remaining_investment_return
            savings_capital += remaining_savings_return + savings_from_expense
            
            # Handle emergency withdrawals for this year
            emergency_withdrawal_amount = 0
            withdrawal_from_savings = 0
            withdrawal_from_investment = 0
            
            if year in emergency_withdrawals:
                emergency_withdrawal_amount = emergency_withdrawals[year]
                
                # First, try to withdraw from savings
                if savings_capital >= emergency_withdrawal_amount:
                    withdrawal_from_savings = emergency_withdrawal_amount
                    savings_capital -= emergency_withdrawal_amount
                else:
                    # Withdraw all available savings first
                    withdrawal_from_savings = savings_capital
                    remaining_needed = emergency_withdrawal_amount - savings_capital
                    savings_capital = 0
                    
                    # Then withdraw from investment capital
                    if investment_capital >= remaining_needed:
                        withdrawal_from_investment = remaining_needed
                        investment_capital -= remaining_needed
                    else:
                        # Not enough capital to cover emergency
                        withdrawal_from_investment = investment_capital
                        investment_capital = 0
            
            total_capital_end = investment_capital + savings_capital
            
            # Calculate coverage percentage
            coverage_pct = (min(total_returns, yearly_expense_allocation) / yearly_expense_allocation) * 100
            
            # Store year result
            year_result = {
                'year': year,
                'investment_capital_start': investment_capital_start,
                'savings_capital_start': savings_capital_start,
                'investment_return': investment_return,
                'savings_return': savings_return,
                'total_returns': total_returns,
                'expense_allocation': yearly_expense_allocation,
                'expense_utilization_rate': current_utilization_rate * 100,
                'utilization_reason': utilization_reason,
                'actual_expense': actual_expense,
                'savings_from_expense': savings_from_expense,
                'expense_from_investment': expense_from_investment,
                'expense_from_savings': expense_from_savings,
                'remaining_investment_return': remaining_investment_return,
                'remaining_savings_return': remaining_savings_return,
                'deficit_covered': deficit_covered_from_savings,
                'emergency_withdrawal': emergency_withdrawal_amount,
                'withdrawal_from_savings': withdrawal_from_savings,
                'withdrawal_from_investment': withdrawal_from_investment,
                'investment_capital_end': investment_capital,
                'savings_capital_end': savings_capital,
                'total_capital_end': total_capital_end,
                'monthly_expense_allocation': yearly_expense_allocation / 12,
                'coverage_percentage': coverage_pct,
                'expense_frozen': False
            }
            
            results.append(year_result)
            
            # Increase expense for next year with EXPENSE BARRIER
            # Only increase if next year's expense won't exceed projected returns
            next_year_expense = yearly_expense_allocation * (1 + annual_expense_increase_rate)
            
            # Project next year's returns based on current capital
            projected_investment_return = investment_capital * annual_return_rate
            projected_savings_return = savings_capital * savings_return_rate
            projected_total_returns = projected_investment_return + projected_savings_return
            
            # Only increase expense if projected returns can cover it
            if next_year_expense <= projected_total_returns:
                yearly_expense_allocation = next_year_expense
            else:
                # Keep expense allocation frozen at current level
                year_result['expense_frozen'] = True
                # yearly_expense_allocation remains same
        
        # Calculate summary statistics
        last_year = results[-1]
        
        investment_growth = ((last_year['investment_capital_end'] - initial_investment) / initial_investment) * 100
        savings_growth = ((last_year['savings_capital_end'] - initial_savings) / initial_savings) * 100
        total_growth = ((last_year['total_capital_end'] - initial_total) / initial_total) * 100
        
        total_investment_returns = sum(y['investment_return'] for y in results)
        total_savings_returns = sum(y['savings_return'] for y in results)
        total_actual_expenses = sum(y['actual_expense'] for y in results)
        total_savings_from_expenses = sum(y['savings_from_expense'] for y in results)
        total_emergency_withdrawals = sum(y['emergency_withdrawal'] for y in results)
        
        summary = {
            'initial': {
                'investment': initial_investment,
                'savings': initial_savings,
                'total': initial_total
            },
            'final': {
                'investment': last_year['investment_capital_end'],
                'savings': last_year['savings_capital_end'],
                'total': last_year['total_capital_end']
            },
            'growth': {
                'investment': investment_growth,
                'savings': savings_growth,
                'total': total_growth
            },
            'returns': {
                'investment': total_investment_returns,
                'savings': total_savings_returns,
                'total': total_investment_returns + total_savings_returns
            },
            'expenses': {
                'total_actual': total_actual_expenses,
                'total_saved': total_savings_from_expenses,
                'initial_monthly': results[0]['monthly_expense_allocation'],
                'final_monthly': last_year['monthly_expense_allocation']
            },
            'emergency': {
                'total_withdrawals': total_emergency_withdrawals,
                'withdrawal_count': sum(1 for y in results if y['emergency_withdrawal'] > 0)
            },
            'asset_allocation': {
                'investment_percentage': (last_year['investment_capital_end'] / last_year['total_capital_end']) * 100,
                'savings_percentage': (last_year['savings_capital_end'] / last_year['total_capital_end']) * 100
            }
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/compare', methods=['POST'])
def compare_scenarios():
    """Compare different scenarios"""
    try:
        data = request.get_json()
        scenarios = data.get('scenarios', [])
        
        comparison_results = []
        
        for scenario in scenarios:
            # Extract parameters
            total_capital = float(scenario.get('total_capital', 20000000))
            annual_return_rate = float(scenario.get('annual_return_rate', 20)) / 100
            savings_return_rate = float(scenario.get('savings_return_rate', 4)) / 100
            years = int(scenario.get('years', 5))
            
            # Quick calculation for final values
            investment_capital = total_capital * 0.75
            savings_capital = total_capital * 0.25
            
            # Simple projection (without expenses for comparison)
            for _ in range(years):
                investment_return = investment_capital * annual_return_rate
                savings_return = savings_capital * savings_return_rate
                investment_capital += investment_return
                savings_capital += savings_return
            
            comparison_results.append({
                'name': scenario.get('name', 'Scenario'),
                'investment_rate': annual_return_rate * 100,
                'savings_rate': savings_return_rate * 100,
                'final_total': investment_capital + savings_capital,
                'final_investment': investment_capital,
                'final_savings': savings_capital
            })
        
        return jsonify({
            'success': True,
            'comparisons': comparison_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/save-calculation', methods=['POST'])
def save_calculation():
    """Save a calculation with metadata"""
    try:
        data = request.get_json()
        
        # Return the data back with a timestamp
        saved_data = {
            'id': data.get('id'),
            'name': data.get('name'),
            'timestamp': data.get('timestamp'),
            'inputs': data.get('inputs'),
            'results': data.get('results'),
            'summary': data.get('summary')
        }
        
        return jsonify({
            'success': True,
            'data': saved_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
