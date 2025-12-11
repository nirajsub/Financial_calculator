from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from decouple import config
from finance import FinancialManager
from ai_coach import coach

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
        
        # Extract monthly income parameters
        monthly_income = float(data.get('monthly_income', 0))
        has_active_income = monthly_income > 0
        years_of_active_income = int(data.get('years_of_active_income', 0)) if has_active_income else 0
        annual_income_increase_rate = float(data.get('annual_income_increase_rate', 10)) / 100
        
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
        
        # Dynamic allocation based on active income
        # If has active income: 80% investment, 20% savings
        # If no active income: 75% investment, 25% savings
        investment_percentage = 0.80 if has_active_income else 0.75
        savings_percentage = 0.20 if has_active_income else 0.25
        
        # Initial allocation
        investment_capital = total_capital * investment_percentage
        savings_capital = total_capital * savings_percentage
        yearly_expense_allocation = monthly_expense_allocation * 12
        
        # Store initial values for growth calculation
        initial_investment = investment_capital
        initial_savings = savings_capital
        initial_total = total_capital
        
        # Track income for the projection
        current_monthly_income = monthly_income
        total_income_received = 0
        
        # Add Year 0 - Initial State (Beginning of Investment)
        year_0_result = {
            'year': 0,
            'investment_capital_start': investment_capital,
            'savings_capital_start': savings_capital,
            'investment_return': 0,
            'savings_return': 0,
            'total_returns': 0,
            'expense_allocation': yearly_expense_allocation,
            'expense_utilization_rate': expense_utilization_rate * 100,
            'utilization_reason': 'Initial State',
            'actual_expense': 0,
            'savings_from_expense': 0,
            'expense_from_investment': 0,
            'expense_from_savings': 0,
            'remaining_investment_return': 0,
            'remaining_savings_return': 0,
            'deficit_covered': 0,
            'emergency_withdrawal': 0,
            'withdrawal_from_savings': 0,
            'withdrawal_from_investment': 0,
            'investment_capital_end': investment_capital,
            'savings_capital_end': savings_capital,
            'total_capital_end': total_capital,
            'monthly_expense_allocation': monthly_expense_allocation,
            'monthly_income': monthly_income,
            'has_active_income': has_active_income,
            'coverage_percentage': 0,
            'expense_frozen': False
        }
        results.append(year_0_result)
        
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
            
            # Check if income is active for this year
            income_active_this_year = has_active_income and year <= years_of_active_income
            monthly_income_this_year = current_monthly_income if income_active_this_year else 0
            
            # SPECIAL CASE: First Year - Month-by-Month Precision Calculation
            if year == 1:
                # Month-by-month calculation for first year with precise interest calculation
                monthly_investment_rate = annual_return_rate / 12
                monthly_savings_rate = savings_return_rate / 12
                
                year_investment_return = 0
                year_savings_return = 0
                year_actual_expense = 0
                year_savings_from_expense = 0
                year_income_received = 0
                year_income_to_savings = 0
                total_expense_withdrawn = 0
                total_expense_from_income = 0
                monthly_details = []
                
                # Process each month
                for month in range(1, 13):
                    month_start_investment = investment_capital
                    month_start_savings = savings_capital
                    
                    # Step 1: Receive monthly income if active
                    monthly_income_received = monthly_income_this_year
                    year_income_received += monthly_income_received
                    
                    # Step 2: Handle monthly expense
                    monthly_expense_needed = monthly_expense_allocation
                    expense_withdrawn_from_savings = 0
                    expense_covered_by_income = 0
                    income_surplus = 0
                    
                    if monthly_income_received >= monthly_expense_needed:
                        # Income covers expense completely
                        expense_covered_by_income = monthly_expense_needed
                        income_surplus = monthly_income_received - monthly_expense_needed
                        total_expense_from_income += expense_covered_by_income
                        # Add surplus income to savings
                        savings_capital += income_surplus
                        year_income_to_savings += income_surplus
                    else:
                        # Income covers partial, withdraw rest from savings
                        expense_covered_by_income = monthly_income_received
                        total_expense_from_income += expense_covered_by_income
                        remaining_expense = monthly_expense_needed - monthly_income_received
                        
                        if savings_capital >= remaining_expense:
                            savings_capital -= remaining_expense
                            expense_withdrawn_from_savings = remaining_expense
                        else:
                            # Insufficient savings - withdraw what's available
                            expense_withdrawn_from_savings = savings_capital
                            savings_capital = 0
                    
                    total_expense_withdrawn += expense_withdrawn_from_savings
                    total_expense_covered = expense_covered_by_income + expense_withdrawn_from_savings
                    
                    # Step 3: Calculate actual expense and savings from utilization
                    monthly_actual_expense = total_expense_covered * current_utilization_rate
                    monthly_savings_from_expense = total_expense_covered * (1 - current_utilization_rate)
                    
                    year_actual_expense += monthly_actual_expense
                    year_savings_from_expense += monthly_savings_from_expense
                    
                    # Step 4: Add unutilized portion back to savings
                    savings_capital += monthly_savings_from_expense
                    
                    # Step 5: Calculate monthly interest on remaining balances
                    monthly_inv_return = investment_capital * monthly_investment_rate
                    monthly_sav_return = savings_capital * monthly_savings_rate
                    
                    investment_capital += monthly_inv_return
                    savings_capital += monthly_sav_return
                    
                    year_investment_return += monthly_inv_return
                    year_savings_return += monthly_sav_return
                    
                    # Track monthly details for chart
                    monthly_details.append({
                        'month': month,
                        'investment_start': month_start_investment,
                        'savings_start': month_start_savings,
                        'monthly_income': monthly_income_received,
                        'expense_from_income': expense_covered_by_income,
                        'expense_withdrawn': expense_withdrawn_from_savings,
                        'income_surplus': income_surplus,
                        'actual_expense': monthly_actual_expense,
                        'savings_from_expense': monthly_savings_from_expense,
                        'investment_return': monthly_inv_return,
                        'savings_return': monthly_sav_return,
                        'investment_end': investment_capital,
                        'savings_end': savings_capital,
                        'total_end': investment_capital + savings_capital
                    })
                
                # Set the calculated values for first year
                investment_return = year_investment_return
                savings_return = year_savings_return
                total_returns = investment_return + savings_return
                actual_expense = year_actual_expense
                savings_from_expense = year_savings_from_expense
                total_income_received += year_income_received
                
                # For first year, track income usage
                expense_from_investment = 0
                expense_from_savings = total_expense_withdrawn
                expense_from_income = total_expense_from_income
                income_to_savings = year_income_to_savings
                remaining_investment_return = investment_return
                remaining_savings_return = savings_return
                expense_from_returns = 0
                deficit_covered_from_savings = 0
                
            else:
                # Standard calculation for years 2 onwards
                # Calculate returns
                investment_return = investment_capital_start * annual_return_rate
                savings_return = savings_capital_start * savings_return_rate
                total_returns = investment_return + savings_return
                
                # Calculate annual income for this year
                yearly_income = monthly_income_this_year * 12
                total_income_received += yearly_income
                
                # Handle expense allocation with income priority
                expense_from_investment = 0
                expense_from_savings = 0
                expense_from_income = 0
                income_to_savings = 0
                remaining_investment_return = 0
                remaining_savings_return = 0
                expense_from_returns = 0
                deficit_covered_from_savings = 0
                
                # Step 1: Use income first for expenses
                if yearly_income >= yearly_expense_allocation:
                    # Income covers all expenses
                    expense_from_income = yearly_expense_allocation
                    income_to_savings = yearly_income - yearly_expense_allocation
                    savings_capital += income_to_savings
                    
                    # All returns go back to capital
                    remaining_investment_return = investment_return
                    remaining_savings_return = savings_return
                    expense_from_returns = 0
                    
                elif yearly_income > 0:
                    # Income covers partial expenses
                    expense_from_income = yearly_income
                    remaining_expense = yearly_expense_allocation - yearly_income
                    
                    # Try to cover remaining from returns
                    if total_returns >= remaining_expense:
                        # Returns can cover the remaining
                        if investment_return >= remaining_expense:
                            expense_from_investment = remaining_expense
                            remaining_investment_return = investment_return - remaining_expense
                            remaining_savings_return = savings_return
                        else:
                            expense_from_investment = investment_return
                            expense_from_savings = remaining_expense - investment_return
                            remaining_investment_return = 0
                            remaining_savings_return = savings_return - expense_from_savings
                        expense_from_returns = remaining_expense
                    else:
                        # Returns insufficient, need to withdraw from savings capital
                        expense_from_returns = total_returns
                        deficit = remaining_expense - total_returns
                        
                        if savings_capital >= deficit:
                            savings_capital -= deficit
                            deficit_covered_from_savings = deficit
                        else:
                            deficit_covered_from_savings = savings_capital
                            savings_capital = 0
                else:
                    # No income, use existing logic
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
                total_expense_covered = expense_from_income + expense_from_returns + deficit_covered_from_savings
                actual_expense = total_expense_covered * current_utilization_rate
                savings_from_expense = total_expense_covered * (1 - current_utilization_rate)
                
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
            coverage_pct = (min(total_returns, yearly_expense_allocation) / yearly_expense_allocation) * 100 if yearly_expense_allocation > 0 else 0
            
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
                'expense_from_income': expense_from_income if 'expense_from_income' in locals() else 0,
                'income_to_savings': income_to_savings if 'income_to_savings' in locals() else 0,
                'monthly_income': monthly_income_this_year,
                'has_active_income': income_active_this_year,
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
            
            # Add monthly details for first year if available
            if year == 1 and 'monthly_details' in locals():
                year_result['monthly_details'] = monthly_details
            
            results.append(year_result)
            
            # Increase income for next year if still active
            if income_active_this_year and year < years_of_active_income:
                current_monthly_income = current_monthly_income * (1 + annual_income_increase_rate)
            
            # Increase expense for next year with EXPENSE BARRIER
            # Only increase if next year's expense won't exceed projected returns + income
            next_year_expense = yearly_expense_allocation * (1 + annual_expense_increase_rate)
            
            # Project next year's returns based on current capital
            projected_investment_return = investment_capital * annual_return_rate
            projected_savings_return = savings_capital * savings_return_rate
            projected_total_returns = projected_investment_return + projected_savings_return
            
            # Check if income will be active next year
            next_year_income = current_monthly_income * 12 if (year + 1) <= years_of_active_income else 0
            projected_total_available = projected_total_returns + next_year_income
            
            # Only increase expense if projected returns + income can cover it
            if next_year_expense <= projected_total_available:
                yearly_expense_allocation = next_year_expense
            else:
                # Keep expense allocation frozen at current level
                year_result['expense_frozen'] = True
                # yearly_expense_allocation remains same
        
        # Calculate summary statistics
        last_year = results[-1]
        
        investment_growth = ((last_year['investment_capital_end'] - initial_investment) / initial_investment) * 100 if initial_investment > 0 else 0
        savings_growth = ((last_year['savings_capital_end'] - initial_savings) / initial_savings) * 100 if initial_savings > 0 else 0
        total_growth = ((last_year['total_capital_end'] - initial_total) / initial_total) * 100 if initial_total > 0 else 0
        
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
                'investment_percentage': (last_year['investment_capital_end'] / last_year['total_capital_end']) * 100 if last_year['total_capital_end'] > 0 else 0,
                'savings_percentage': (last_year['savings_capital_end'] / last_year['total_capital_end']) * 100 if last_year['total_capital_end'] > 0 else 0
            },
            'income': {
                'total_received': total_income_received,
                'monthly_income': monthly_income,
                'has_active_income': has_active_income,
                'years_of_income': years_of_active_income
            }
        }
        
        # Initial configuration information
        configuration = {
            'total_capital': initial_total,
            'investment_capital': initial_investment,
            'investment_percentage': investment_percentage * 100,
            'savings_capital': initial_savings,
            'savings_percentage': savings_percentage * 100,
            'annual_return_rate': annual_return_rate * 100,
            'savings_return_rate': savings_return_rate * 100,
            'initial_monthly_expense': monthly_expense_allocation,
            'initial_yearly_expense': monthly_expense_allocation * 12,
            'annual_expense_increase_rate': annual_expense_increase_rate * 100,
            'expense_utilization_rate': expense_utilization_rate * 100,
            'projection_years': years,
            'monthly_income': monthly_income,
            'has_active_income': has_active_income,
            'years_of_active_income': years_of_active_income,
            'annual_income_increase_rate': annual_income_increase_rate * 100
        }
        
        return jsonify({
            'success': True,
            'configuration': configuration,
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

@app.route('/ai-advisor')
def ai_advisor():
    """AI Financial Advisor page"""
    return render_template('ai_advisor.html')

@app.route('/api/ai/recommendations', methods=['POST'])
def get_ai_recommendations():
    """Get AI-powered financial recommendations"""
    try:
        data = request.get_json()
        
        # Extract user inputs
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
        
        # Calculate key metrics
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
        annual_savings = monthly_savings * 12
        emergency_fund_months = emergency_fund
        recommended_emergency_months = 6
        debt_to_income = (existing_debts / (monthly_income * 12) * 100) if monthly_income > 0 else 0
        
        # Calculate future projections
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
        
        # Generate AI recommendations using rule-based logic
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
            total_returns=total_returns
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

def calculate_required_savings(current_amount, target_amount, annual_return, years):
    """Calculate required monthly savings to reach target"""
    if years <= 0:
        return target_amount - current_amount
    
    # Future value of current amount
    fv_current = current_amount * ((1 + annual_return) ** years)
    
    # Amount still needed
    amount_needed = max(0, target_amount - fv_current)
    
    if amount_needed == 0:
        return 0
    
    # Monthly payment needed (ordinary annuity formula)
    monthly_rate = annual_return / 12
    months = years * 12
    
    if monthly_rate == 0:
        return amount_needed / months if months > 0 else 0
    
    monthly_payment = amount_needed * monthly_rate / (((1 + monthly_rate) ** months) - 1)
    return monthly_payment

def generate_smart_recommendations(**kwargs):
    """Generate comprehensive financial recommendations based on user profile"""
    
    recommendations = {
        'overall_assessment': '',
        'priority_actions': [],
        'portfolio_allocation': {},
        'savings_strategy': {},
        'risk_analysis': {},
        'goal_projection': {},
        'detailed_insights': [],
        'action_plan': []
    }
    
    # Extract parameters
    age = kwargs.get('age')
    risk_tolerance = kwargs.get('risk_tolerance')
    savings_rate = kwargs.get('savings_rate')
    emergency_fund_months = kwargs.get('emergency_fund_months')
    debt_to_income = kwargs.get('debt_to_income')
    monthly_savings = kwargs.get('monthly_savings')
    existing_debts = kwargs.get('existing_debts')
    has_retirement_plan = kwargs.get('has_retirement_plan')
    time_horizon = kwargs.get('time_horizon')
    final_value = kwargs.get('final_value')
    investment_goal = kwargs.get('investment_goal')
    
    # Overall Assessment
    if savings_rate >= 20:
        assessment = "Excellent! Your savings rate is strong and puts you in a great position for financial success."
    elif savings_rate >= 10:
        assessment = "Good progress! You're saving consistently, but there's room for improvement."
    elif savings_rate >= 5:
        assessment = "You're on the right track, but increasing your savings rate should be a priority."
    else:
        assessment = "Your current savings rate is concerning. We need to develop a strategy to increase it significantly."
    
    recommendations['overall_assessment'] = assessment
    
    # Priority Actions
    priority_actions = []
    
    # Emergency Fund Check
    if emergency_fund_months < 3:
        priority_actions.append({
            'priority': 'HIGH',
            'category': 'Emergency Fund',
            'action': f'Build emergency fund to at least 3-6 months of expenses (${kwargs.get("monthly_expenses") * 3:,.2f} - ${kwargs.get("monthly_expenses") * 6:,.2f})',
            'reason': 'Having an emergency fund is crucial for financial stability and prevents debt accumulation during unexpected events.'
        })
    
    # Debt Management
    if debt_to_income > 40:
        priority_actions.append({
            'priority': 'HIGH',
            'category': 'Debt Reduction',
            'action': 'Focus on aggressive debt repayment - your debt-to-income ratio is too high',
            'reason': f'With a {debt_to_income:.1f}% debt-to-income ratio, reducing debt should be your top priority before investing.'
        })
    elif existing_debts > 0:
        priority_actions.append({
            'priority': 'MEDIUM',
            'category': 'Debt Management',
            'action': 'Consider debt consolidation and maintain consistent payments',
            'reason': 'Reducing high-interest debt can provide better returns than most investments.'
        })
    
    # Retirement Planning
    if not has_retirement_plan and age < 50:
        priority_actions.append({
            'priority': 'HIGH',
            'category': 'Retirement Planning',
            'action': 'Start contributing to a retirement account (401k, IRA) immediately',
            'reason': 'The power of compound interest means every year of delay significantly impacts your retirement savings.'
        })
    
    # Savings Rate
    if savings_rate < 15:
        priority_actions.append({
            'priority': 'MEDIUM',
            'category': 'Increase Savings',
            'action': f'Work towards increasing your savings rate from {savings_rate:.1f}% to at least 15-20%',
            'reason': 'Higher savings rate accelerates goal achievement and provides more financial security.'
        })
    
    recommendations['priority_actions'] = priority_actions
    
    # Portfolio Allocation
    if risk_tolerance == 'conservative':
        allocation = {
            'stocks': 40,
            'bonds': 45,
            'cash': 15,
            'rationale': 'Conservative allocation prioritizes capital preservation with modest growth potential.'
        }
    elif risk_tolerance == 'moderate':
        allocation = {
            'stocks': 60,
            'bonds': 30,
            'cash': 10,
            'rationale': 'Balanced allocation provides growth potential while managing risk through diversification.'
        }
    else:  # aggressive
        allocation = {
            'stocks': 80,
            'bonds': 15,
            'cash': 5,
            'rationale': 'Aggressive allocation maximizes growth potential, suitable for long-term investors who can handle volatility.'
        }
    
    # Adjust based on age
    if age > 50:
        allocation['stocks'] -= 10
        allocation['bonds'] += 10
        allocation['rationale'] += ' Adjusted for age to reduce risk as retirement approaches.'
    
    recommendations['portfolio_allocation'] = allocation
    
    # ENHANCED: Portfolio Rebalancing Recommendations
    current_allocation_str = kwargs.get('current_allocation', '').lower()
    rebalancing_needed = False
    rebalancing_actions = []
    
    if current_allocation_str:
        # Parse current allocation if provided
        if 'stock' in current_allocation_str or 'equit' in current_allocation_str:
            # User has stocks - check if rebalancing needed
            if age > 60 and 'aggressive' not in current_allocation_str:
                rebalancing_actions.append('Consider reducing stock exposure as you approach retirement')
                rebalancing_needed = True
            elif age < 40 and 'conservative' in current_allocation_str:
                rebalancing_actions.append('You may benefit from higher stock allocation given your age and time horizon')
                rebalancing_needed = True
        
        # Check for over-concentration
        if 'crypto' in current_allocation_str or 'bitcoin' in current_allocation_str:
            rebalancing_actions.append('CAUTION: Cryptocurrency should not exceed 5% of portfolio due to high volatility')
            rebalancing_needed = True
        
        if 'single stock' in current_allocation_str or 'one stock' in current_allocation_str:
            rebalancing_actions.append('Diversify away from single-stock concentration - aim for index funds or 20+ holdings')
            rebalancing_needed = True
    
    # Add rebalancing timing recommendation
    if rebalancing_needed or not current_allocation_str:
        rebalancing_actions.append(f'Target allocation: {allocation["stocks"]}% stocks, {allocation["bonds"]}% bonds, {allocation["cash"]}% cash')
        rebalancing_actions.append('Rebalance quarterly or when allocation drifts >5% from target')
        rebalancing_actions.append('Use tax-advantaged accounts first to minimize capital gains taxes')
    
    recommendations['portfolio_rebalancing'] = {
        'needed': rebalancing_needed or not current_allocation_str,
        'target_allocation': allocation,
        'actions': rebalancing_actions if rebalancing_actions else ['Your current allocation appears balanced'],
        'next_review_date': 'Review in 3 months or after major market movements'
    }
    
    # ENHANCED: Expense Optimization Engine
    monthly_income = kwargs.get('monthly_income', 0)
    monthly_expenses = kwargs.get('monthly_expenses', 0)
    expense_categories = []
    potential_savings = 0
    
    # Calculate expense ratio
    expense_ratio = (monthly_expenses / monthly_income * 100) if monthly_income > 0 else 0
    
    # Housing (typically 25-30%)
    recommended_housing = monthly_income * 0.28
    if monthly_expenses > recommended_housing:
        housing_excess = (monthly_expenses - recommended_housing) * 0.35  # Assume 35% is housing
        if housing_excess > 0:
            expense_categories.append({
                'category': 'Housing',
                'current': f'~${monthly_expenses * 0.35:.0f}/mo',
                'recommended': f'<${recommended_housing:.0f}/mo (28% of income)',
                'savings_potential': round(housing_excess, 2),
                'tips': [
                    'Consider downsizing or roommate situation',
                    'Refinance mortgage if rates are lower',
                    'Negotiate rent or explore cheaper areas'
                ]
            })
            potential_savings += housing_excess
    
    # Transportation (10-15%)
    if expense_ratio > 80:  # High expenses
        transport_current = monthly_expenses * 0.15
        transport_recommended = monthly_income * 0.12
        transport_savings = max(0, transport_current - transport_recommended)
        if transport_savings > 50:
            expense_categories.append({
                'category': 'Transportation',
                'current': f'~${transport_current:.0f}/mo',
                'recommended': f'<${transport_recommended:.0f}/mo (12% of income)',
                'savings_potential': round(transport_savings, 2),
                'tips': [
                    'Consider public transportation or carpooling',
                    'Trade in for more fuel-efficient vehicle',
                    'Reduce car payment by buying used',
                    'Shop for better auto insurance rates'
                ]
            })
            potential_savings += transport_savings
    
    # Food & Dining (10-15%)
    food_current = monthly_expenses * 0.12
    food_recommended = monthly_income * 0.10
    food_savings = max(0, food_current - food_recommended)
    if food_savings > 30:
        expense_categories.append({
            'category': 'Food & Dining',
            'current': f'~${food_current:.0f}/mo',
            'recommended': f'<${food_recommended:.0f}/mo (10% of income)',
            'savings_potential': round(food_savings, 2),
            'tips': [
                'Meal prep on weekends to reduce eating out',
                'Use cashback/rewards cards for groceries',
                'Set a monthly dining out budget and stick to it',
                'Buy generic brands and shop sales'
            ]
        })
        potential_savings += food_savings
    
    # Subscriptions & Entertainment (5-10%)
    if savings_rate < 15:
        subscription_est = monthly_expenses * 0.08
        subscription_recommended = monthly_income * 0.05
        subscription_savings = max(0, subscription_est - subscription_recommended)
        if subscription_savings > 20:
            expense_categories.append({
                'category': 'Subscriptions & Entertainment',
                'current': f'~${subscription_est:.0f}/mo',
                'recommended': f'<${subscription_recommended:.0f}/mo (5% of income)',
                'savings_potential': round(subscription_savings, 2),
                'tips': [
                    'Audit all subscriptions - cancel unused services',
                    'Share family plans for streaming services',
                    'Use free alternatives (library, free events)',
                    'Set entertainment budget and use cash envelope system'
                ]
            })
            potential_savings += subscription_savings
    
    recommendations['expense_optimization'] = {
        'total_potential_savings': round(potential_savings, 2),
        'annual_savings_potential': round(potential_savings * 12, 2),
        'expense_ratio': round(expense_ratio, 1),
        'target_expense_ratio': 70,  # 70% expenses, 30% savings ideal
        'categories': expense_categories if expense_categories else [{
            'category': 'Overall',
            'message': 'Your expense ratio looks reasonable. Focus on maintaining current spending levels while income grows.',
            'tips': ['Track expenses monthly to catch increases early', 'Negotiate bills annually', 'Build $1000 buffer in checking']
        }],
        'quick_wins': [
            'Cancel unused subscriptions (avg savings: $50-100/mo)',
            'Meal prep 3x per week (savings: $100-200/mo)',
            'Refinance high-interest debt (potential savings: varies)',
            'Use cashback credit cards strategically (earn 1-5% back)'
        ]
    }
    
    # ENHANCED: Goal Planning with Specific Targets
    goal_specific_advice = {}
    current_capital = kwargs.get('current_capital', 0)
    expected_return = kwargs.get('expected_return', 8) / 100
    goal_names = {
        'retirement': 'Retirement',
        'wealth': 'Wealth Building',
        'house': 'Home Purchase',
        'education': 'Education Fund',
        'emergency': 'Emergency Fund',
        'other': 'Financial Goal'
    }
    if investment_goal == 'retirement':
        # Rule of 25: Need 25x annual expenses
        annual_expenses = monthly_expenses * 12
        retirement_target = annual_expenses * 25
        years_to_retirement = 65 - age
        required_monthly = calculate_required_savings(current_capital, retirement_target, expected_return, years_to_retirement)
        
        goal_specific_advice = {
            'goal_type': 'Retirement',
            'target_amount': round(retirement_target, 2),
            'years_remaining': years_to_retirement,
            'current_progress': round((current_capital / retirement_target * 100), 1) if retirement_target > 0 else 0,
            'required_monthly_savings': round(required_monthly, 2),
            'on_track': monthly_savings >= required_monthly,
            'recommendations': [
                f'Target nest egg: ${retirement_target:,.0f} (25x annual expenses)',
                f'Required monthly savings: ${required_monthly:,.0f}',
                'Maximize employer 401k match (free money!)',
                'Consider Roth IRA if income allows ($7,000/year limit)',
                f'At {age}, aim for {age}x salary in retirement savings',
                'Use catch-up contributions if age 50+ ($7,500 extra/year)'
            ]
        }
    elif investment_goal == 'house':
        # Typical down payment: 20%
        avg_home_price = monthly_income * 12 * 5  # Rule: 5x annual income
        down_payment = avg_home_price * 0.20
        closing_costs = avg_home_price * 0.03
        total_needed = down_payment + closing_costs
        required_monthly = calculate_required_savings(current_capital, total_needed, expected_return * 0.5, time_horizon)  # Lower return for short-term
        
        goal_specific_advice = {
            'goal_type': 'Home Purchase',
            'target_amount': round(total_needed, 2),
            'years_remaining': time_horizon,
            'current_progress': round((current_capital / total_needed * 100), 1) if total_needed > 0 else 0,
            'required_monthly_savings': round(required_monthly, 2),
            'on_track': monthly_savings >= required_monthly,
            'recommendations': [
                f'Estimated home price range: ${avg_home_price * 0.8:,.0f} - ${avg_home_price * 1.2:,.0f}',
                f'20% down payment needed: ${down_payment:,.0f}',
                f'Closing costs (3%): ${closing_costs:,.0f}',
                f'Total needed: ${total_needed:,.0f}',
                'Save in high-yield savings account (not stocks for short-term goals)',
                'Check first-time homebuyer programs (may reduce down payment)',
                'Maintain credit score above 740 for best mortgage rates',
                'Budget for ongoing costs: Property tax, insurance, maintenance (1% of home value/year)'
            ]
        }
    elif investment_goal == 'education':
        # College costs
        cost_per_year = 30000  # Average including room/board
        years_of_college = 4
        total_education_cost = cost_per_year * years_of_college
        required_monthly = calculate_required_savings(current_capital, total_education_cost, expected_return, time_horizon)
        
        goal_specific_advice = {
            'goal_type': 'Education Fund',
            'target_amount': round(total_education_cost, 2),
            'years_remaining': time_horizon,
            'current_progress': round((current_capital / total_education_cost * 100), 1) if total_education_cost > 0 else 0,
            'required_monthly_savings': round(required_monthly, 2),
            'on_track': monthly_savings >= required_monthly,
            'recommendations': [
                f'Estimated 4-year cost: ${total_education_cost:,.0f}',
                'Open 529 plan for tax-advantaged growth',
                'State tax deductions may be available',
                'Consider community college for first 2 years (save 50%)',
                'Apply for scholarships and grants early',
                'Factor in student working part-time ($5-10k/year)'
            ]
        }
    else:
        # Generic wealth building
        target_multiple = 10  # 10x current savings
        wealth_target = max(current_capital * target_multiple, 1000000)
        required_monthly = calculate_required_savings(current_capital, wealth_target, expected_return, time_horizon)
        goal_specific_advice = {
            'goal_type': goal_names.get(investment_goal, 'Wealth Building'),
            'target_amount': round(wealth_target, 2),
            'years_remaining': time_horizon,
            'current_progress': round((current_capital / wealth_target * 100), 1) if wealth_target > 0 else 0,
            'required_monthly_savings': round(required_monthly, 2),
            'on_track': monthly_savings >= required_monthly,
            'recommendations': [
                f'Target: ${wealth_target:,.0f} in {time_horizon} years',
                'Diversify across asset classes',
                'Keep costs low with index funds (expense ratios <0.2%)',
                'Stay invested through market volatility',
                'Rebalance annually'
            ]
        }
    
    recommendations['goal_planning'] = goal_specific_advice
    
    # ENHANCED: Tax Efficiency Strategies
    annual_income = monthly_income * 12
    tax_strategies = []
    estimated_tax_savings = 0
    
    # Retirement account tax benefits
    if not has_retirement_plan or (has_retirement_plan and savings_rate < 15):
        max_401k = 23000  # 2024 limit
        max_ira = 7000    # 2024 limit
        potential_contribution = min(annual_income * 0.15, max_401k)
        tax_rate = 0.22 if annual_income > 50000 else 0.12  # Estimated marginal rate
        retirement_tax_savings = potential_contribution * tax_rate
        
        tax_strategies.append({
            'strategy': 'Maximize Retirement Contributions',
            'tax_savings': round(retirement_tax_savings, 2),
            'details': [
                f'401(k) limit: ${max_401k:,.0f}/year (pre-tax reduces taxable income)',
                f'IRA limit: ${max_ira:,.0f}/year',
                f'Employer match is FREE money - always take full match',
                f'Est. tax savings at {tax_rate*100:.0f}% bracket: ${retirement_tax_savings:,.0f}/year'
            ]
        })
        estimated_tax_savings += retirement_tax_savings
    
    # HSA if has health insurance
    has_health_insurance = kwargs.get('has_health_insurance', False)
    if has_health_insurance or kwargs.get('willing_to_increase_savings'):
        hsa_limit = 4150  # Individual 2024
        hsa_tax_savings = hsa_limit * 0.22  # Fed income + FICA savings
        tax_strategies.append({
            'strategy': 'Health Savings Account (HSA)',
            'tax_savings': round(hsa_tax_savings, 2),
            'details': [
                'Triple tax advantage: Tax-deductible, grows tax-free, tax-free withdrawals for medical',
                f'Contribution limit: ${hsa_limit:,.0f}/year (individual), ${8300:,.0f} (family)',
                'Can invest HSA funds like IRA once you have buffer',
                'Keep receipts - can reimburse yourself decades later',
                f'Est. tax savings: ${hsa_tax_savings:,.0f}/year'
            ]
        })
        estimated_tax_savings += hsa_tax_savings
    
    # Tax-loss harvesting if investing
    if current_capital > 50000:
        tlh_savings = current_capital * 0.001  # Rough estimate
        tax_strategies.append({
            'strategy': 'Tax-Loss Harvesting',
            'tax_savings': round(tlh_savings, 2),
            'details': [
                'Sell losing investments to offset gains',
                'Can deduct $3,000/year against ordinary income',
                'Losses carry forward indefinitely',
                'Avoid wash sale rule (wait 30 days before repurchasing)',
                'Many robo-advisors automate this'
            ]
        })
        estimated_tax_savings += tlh_savings
    
    # Asset location optimization
    if current_capital > 25000:
        tax_strategies.append({
            'strategy': 'Optimize Asset Location',
            'tax_savings': 'Varies',
            'details': [
                'Tax-inefficient assets (bonds, REITs) → tax-advantaged accounts',
                'Tax-efficient assets (index funds, ETFs) → taxable accounts',
                'Keep high-turnover funds in IRAs/401ks',
                'International stocks in taxable for foreign tax credit',
                'Can save 0.5-1% annually through smart placement'
            ]
        })
    
    # Charitable giving
    if annual_income > 75000:
        tax_strategies.append({
            'strategy': 'Strategic Charitable Giving',
            'tax_savings': 'Varies',
            'details': [
                'Donate appreciated stocks (avoid capital gains + get deduction)',
                'Bunch donations every 2-3 years to exceed standard deduction',
                'Use Donor-Advised Fund (DAF) for tax timing flexibility',
                'QCD from IRA if age 70.5+ (up to $105,000/year)',
                'Document all donations for deduction'
            ]
        })
    
    recommendations['tax_efficiency'] = {
        'estimated_annual_savings': round(estimated_tax_savings, 2),
        'strategies': tax_strategies,
        'priority_order': [
            '1. Max employer 401k match (free money + tax savings)',
            '2. Max HSA if eligible (triple tax benefit)',
            '3. Max IRA ($7,000/year)',
            '4. Max 401k ($23,000/year)',
            '5. Taxable brokerage with tax-efficient funds'
        ],
        'tax_filing_tips': [
            'Consider tax software or CPA if complex situation',
            'Make estimated tax payments if self-employed',
            'Track all investment-related expenses',
            'Keep records for 7 years'
        ]
    }
    
    # Savings Strategy (Enhanced)
    recommendations['savings_strategy'] = {
        'current_monthly': round(monthly_savings, 2),
        'recommended_monthly': round(kwargs.get('monthly_income') * 0.20, 2),
        'potential_annual_increase': round((kwargs.get('monthly_income') * 0.20 - monthly_savings) * 12, 2),
        'with_expense_optimization': round(potential_savings * 12, 2),
        'with_tax_efficiency': round(estimated_tax_savings, 2),
        'total_potential_boost': round((kwargs.get('monthly_income') * 0.20 - monthly_savings) * 12 + potential_savings * 12 + estimated_tax_savings, 2),
        'strategies': [
            'Automate savings transfers on payday',
            'Use "pay yourself first" mentality',
            'Implement the 50/30/20 budgeting rule',
            'Save all raises and bonuses',
            'Round up purchases and save the difference',
            'Try a no-spend challenge monthly'
        ]
    }
    
    # Risk Analysis
    risk_factors = []
    if emergency_fund_months < 6:
        risk_factors.append('Insufficient emergency fund')
    if debt_to_income > 30:
        risk_factors.append('High debt burden')
    if savings_rate < 10:
        risk_factors.append('Low savings rate')
    if not has_retirement_plan:
        risk_factors.append('No retirement savings plan')
    
    recommendations['risk_analysis'] = {
        'risk_score': len(risk_factors),
        'risk_level': 'High' if len(risk_factors) >= 3 else 'Medium' if len(risk_factors) >= 1 else 'Low',
        'risk_factors': risk_factors,
        'mitigation_steps': priority_actions[:3]
    }
    
    # Goal Projection
    
    
    recommendations['goal_projection'] = {
        'goal_name': goal_names.get(investment_goal, 'Financial Goal'),
        'time_horizon': time_horizon,
        'projected_value': round(final_value, 2),
        'likelihood': 'High' if savings_rate >= 15 else 'Medium' if savings_rate >= 10 else 'Low',
        'monthly_target': round(kwargs.get('monthly_income') * 0.20, 2)
    }
    
    # Detailed Insights
    insights = []
    
    insights.append({
        'title': 'Savings Rate Analysis',
        'icon': 'piggy-bank',
        'content': f'Your current savings rate is {savings_rate:.1f}%. Experts recommend saving at least 15-20% of income. {"Great job!" if savings_rate >= 15 else "Consider increasing this gradually."}'
    })
    
    insights.append({
        'title': 'Investment Growth Potential',
        'icon': 'chart-line',
        'content': f'With an expected {kwargs.get("expected_return")}% annual return, your ${kwargs.get("current_capital"):,.0f} could grow to ${final_value:,.0f} in {time_horizon} years.'
    })
    
    insights.append({
        'title': 'Emergency Preparedness',
        'icon': 'shield-alt',
        'content': f'You currently have {emergency_fund_months:.1f} months of expenses saved. {"Excellent!" if emergency_fund_months >= 6 else "Aim for 3-6 months for optimal security."}'
    })
    
    if existing_debts > 0:
        insights.append({
            'title': 'Debt Management',
            'icon': 'credit-card',
            'content': f'Your debt-to-income ratio is {debt_to_income:.1f}%. {"This is manageable." if debt_to_income < 30 else "Focus on reducing this below 30%."}'
        })
    
    recommendations['detailed_insights'] = insights
    
    # Action Plan
    action_plan = [
        {
            'timeline': 'Immediate (This Month)',
            'actions': [
                'Set up automatic savings transfers',
                'Review all current expenses and identify cuts',
                'Open/maximize retirement account contributions' if not has_retirement_plan else 'Verify retirement contributions are maximized'
            ]
        },
        {
            'timeline': '1-3 Months',
            'actions': [
                f'Build emergency fund to ${kwargs.get("monthly_expenses") * 3:,.0f}' if emergency_fund_months < 3 else 'Maintain emergency fund',
                'Research and diversify investments',
                'Consider meeting with a financial advisor'
            ]
        },
        {
            'timeline': '3-6 Months',
            'actions': [
                'Rebalance portfolio if needed',
                'Review and adjust budget based on progress',
                'Explore additional income opportunities'
            ]
        },
        {
            'timeline': 'Ongoing',
            'actions': [
                'Monthly budget review and adjustment',
                'Quarterly investment portfolio review',
                'Annual comprehensive financial check-up',
                'Increase savings rate with income raises'
            ]
        }
    ]
    
    recommendations['action_plan'] = action_plan
    
    return recommendations


# ===================================
# AI COACH ROUTES
# ===================================

@app.route('/coach')
def ai_coach():
    """Render the AI Financial Coach page"""
    return render_template('coach.html')


@app.route('/api/coach/chat', methods=['POST'])
def coach_chat():
    """Handle chat messages from the AI coach"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id or not message:
            return jsonify({
                'success': False,
                'error': 'Missing session_id or message'
            }), 400
        
        # Process message through AI coach
        result = coach.chat(session_id, message)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/coach/context', methods=['POST'])
def coach_context():
    """Update user context for personalized advice"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        context = data.get('context', {})
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        # Add context to AI coach
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


@app.route('/api/coach/suggestions', methods=['POST'])
def coach_suggestions():
    """Get suggested follow-up questions"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        # Get suggestions from AI coach
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


@app.route('/api/coach/clear', methods=['POST'])
def coach_clear():
    """Clear conversation history"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        # Clear conversation
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


@app.route('/api/coach/summary', methods=['POST'])
def coach_summary():
    """Get conversation summary"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Missing session_id'
            }), 400
        
        # Get summary
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


@app.route('/api/coach/import-calculation', methods=['POST'])
def coach_import_calculation():
    """Import calculation results directly into AI coach context"""
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
        
        # Extract key information from calculation
        context_update = {}
        
        # Basic parameters
        if 'total_capital' in calculation_data:
            context_update['total_capital'] = calculation_data['total_capital']
        
        if 'monthly_income' in calculation_data:
            context_update['monthly_income'] = calculation_data['monthly_income']
        
        if 'monthly_expense_allocation' in calculation_data:
            context_update['monthly_expenses'] = calculation_data['monthly_expense_allocation']
        
        if 'investment_allocation' in calculation_data:
            context_update['investment_allocation'] = calculation_data['investment_allocation']
        
        if 'annual_return_rate' in calculation_data:
            context_update['annual_return_rate'] = calculation_data['annual_return_rate'] * 100  # Convert to percentage
        
        if 'savings_return_rate' in calculation_data:
            context_update['savings_return_rate'] = calculation_data['savings_return_rate'] * 100
        
        if 'years' in calculation_data:
            context_update['years'] = calculation_data['years']
        
        if 'years_of_active_income' in calculation_data:
            context_update['years_of_active_income'] = calculation_data['years_of_active_income']
        
        if 'investment_goal' in calculation_data:
            context_update['investment_goal'] = calculation_data['investment_goal']
        
        # Store full calculation results
        if 'results' in calculation_data or 'summary' in calculation_data:
            context_update['calculation_results'] = {
                'results': calculation_data.get('results', []),
                'summary': calculation_data.get('summary', {}),
                'imported_at': datetime.now().isoformat()
            }
        
        # Update context
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
