from flask import Blueprint, request, jsonify

calculator_bp = Blueprint('calculator', __name__)

@calculator_bp.route('/calculate', methods=['POST'])
def calculate():
    from finance import FinancialManager
    
    try:
        data = request.get_json()
        
        total_capital = float(data.get('total_capital', 20000000))
        annual_return_rate = float(data.get('annual_return_rate', 20)) / 100
        savings_return_rate = float(data.get('savings_return_rate', 4)) / 100
        monthly_expense_allocation = float(data.get('monthly_expense_allocation', 150000))
        expense_utilization_rate = float(data.get('expense_utilization_rate', 80)) / 100
        annual_expense_increase_rate = float(data.get('annual_expense_increase_rate', 10)) / 100
        years = int(data.get('years', 5))
        
        monthly_income = float(data.get('monthly_income', 0))
        has_active_income = monthly_income > 0
        years_of_active_income = int(data.get('years_of_active_income', 0)) if has_active_income else 0
        annual_income_increase_rate = float(data.get('annual_income_increase_rate', 10)) / 100
        
        emergency_withdrawals_list = data.get('emergency_withdrawals', [])
        emergency_withdrawals = {}
        for withdrawal in emergency_withdrawals_list:
            year = int(withdrawal.get('year'))
            amount = float(withdrawal.get('amount'))
            if 1 <= year <= years and amount > 0:
                emergency_withdrawals[year] = amount
        
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
        
        fm = FinancialManager()
        results = []
        
        investment_percentage = 0.80 if has_active_income else 0.75
        savings_percentage = 0.20 if has_active_income else 0.25
        
        investment_capital = total_capital * investment_percentage
        savings_capital = total_capital * savings_percentage
        yearly_expense_allocation = monthly_expense_allocation * 12
        
        initial_investment = investment_capital
        initial_savings = savings_capital
        initial_total = total_capital
        
        current_monthly_income = monthly_income
        total_income_received = 0
        
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
            'expense_from_income': 0,
            'income_to_savings': 0,
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
        
        for year in range(1, years + 1):
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
            
            income_active_this_year = has_active_income and year <= years_of_active_income
            monthly_income_this_year = current_monthly_income if income_active_this_year else 0
            
            if year == 1:
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
                
                for month in range(1, 13):
                    month_start_investment = investment_capital
                    month_start_savings = savings_capital
                    
                    monthly_income_received = monthly_income_this_year
                    year_income_received += monthly_income_received
                    
                    monthly_expense_needed = monthly_expense_allocation
                    expense_withdrawn_from_savings = 0
                    expense_covered_by_income = 0
                    income_surplus = 0
                    
                    if monthly_income_received >= monthly_expense_needed:
                        expense_covered_by_income = monthly_expense_needed
                        income_surplus = monthly_income_received - monthly_expense_needed
                        total_expense_from_income += expense_covered_by_income
                        savings_capital += income_surplus
                        year_income_to_savings += income_surplus
                    else:
                        expense_covered_by_income = monthly_income_received
                        total_expense_from_income += expense_covered_by_income
                        remaining_expense = monthly_expense_needed - monthly_income_received
                        
                        if savings_capital >= remaining_expense:
                            savings_capital -= remaining_expense
                            expense_withdrawn_from_savings = remaining_expense
                        else:
                            expense_withdrawn_from_savings = savings_capital
                            savings_capital = 0
                    
                    total_expense_withdrawn += expense_withdrawn_from_savings
                    total_expense_covered = expense_covered_by_income + expense_withdrawn_from_savings
                    
                    monthly_actual_expense = total_expense_covered * current_utilization_rate
                    monthly_savings_from_expense = total_expense_covered * (1 - current_utilization_rate)
                    
                    year_actual_expense += monthly_actual_expense
                    year_savings_from_expense += monthly_savings_from_expense
                    
                    savings_capital += monthly_savings_from_expense
                    
                    monthly_inv_return = investment_capital * monthly_investment_rate
                    monthly_sav_return = savings_capital * monthly_savings_rate
                    
                    investment_capital += monthly_inv_return
                    savings_capital += monthly_sav_return
                    
                    year_investment_return += monthly_inv_return
                    year_savings_return += monthly_sav_return
                    
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
                
                investment_return = year_investment_return
                savings_return = year_savings_return
                total_returns = investment_return + savings_return
                actual_expense = year_actual_expense
                savings_from_expense = year_savings_from_expense
                total_income_received += year_income_received
                
                expense_from_investment = 0
                expense_from_savings = total_expense_withdrawn
                expense_from_income = total_expense_from_income
                income_to_savings = year_income_to_savings
                remaining_investment_return = investment_return
                remaining_savings_return = savings_return
                expense_from_returns = 0
                deficit_covered_from_savings = 0
                
            else:
                investment_return = investment_capital_start * annual_return_rate
                savings_return = savings_capital_start * savings_return_rate
                total_returns = investment_return + savings_return
                
                yearly_income = monthly_income_this_year * 12
                total_income_received += yearly_income
                
                expense_from_investment = 0
                expense_from_savings = 0
                expense_from_income = 0
                income_to_savings = 0
                remaining_investment_return = 0
                remaining_savings_return = 0
                expense_from_returns = 0
                deficit_covered_from_savings = 0
                
                if yearly_income >= yearly_expense_allocation:
                    expense_from_income = yearly_expense_allocation
                    income_to_savings = yearly_income - yearly_expense_allocation
                    savings_capital += income_to_savings
                    
                    remaining_investment_return = investment_return
                    remaining_savings_return = savings_return
                    expense_from_returns = 0
                    
                elif yearly_income > 0:
                    expense_from_income = yearly_income
                    remaining_expense = yearly_expense_allocation - yearly_income
                    
                    if total_returns >= remaining_expense:
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
                        expense_from_returns = total_returns
                        deficit = remaining_expense - total_returns
                        
                        if savings_capital >= deficit:
                            savings_capital -= deficit
                            deficit_covered_from_savings = deficit
                        else:
                            deficit_covered_from_savings = savings_capital
                            savings_capital = 0
                else:
                    if total_returns < yearly_expense_allocation:
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
                
                total_expense_covered = expense_from_income + expense_from_returns + deficit_covered_from_savings
                actual_expense = total_expense_covered * current_utilization_rate
                savings_from_expense = total_expense_covered * (1 - current_utilization_rate)
                
                investment_capital += remaining_investment_return
                savings_capital += remaining_savings_return + savings_from_expense
            
            emergency_withdrawal_amount = 0
            withdrawal_from_savings = 0
            withdrawal_from_investment = 0
            
            if year in emergency_withdrawals:
                emergency_withdrawal_amount = emergency_withdrawals[year]
                
                if savings_capital >= emergency_withdrawal_amount:
                    withdrawal_from_savings = emergency_withdrawal_amount
                    savings_capital -= emergency_withdrawal_amount
                else:
                    withdrawal_from_savings = savings_capital
                    remaining_needed = emergency_withdrawal_amount - savings_capital
                    savings_capital = 0
                    
                    if investment_capital >= remaining_needed:
                        withdrawal_from_investment = remaining_needed
                        investment_capital -= remaining_needed
                    else:
                        withdrawal_from_investment = investment_capital
                        investment_capital = 0
            
            total_capital_end = investment_capital + savings_capital
            
            coverage_pct = (min(total_returns, yearly_expense_allocation) / yearly_expense_allocation) * 100 if yearly_expense_allocation > 0 else 0
            
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
            
            if year == 1 and 'monthly_details' in locals():
                year_result['monthly_details'] = monthly_details
            
            results.append(year_result)
            
            if income_active_this_year and year < years_of_active_income:
                current_monthly_income = current_monthly_income * (1 + annual_income_increase_rate)
            
            next_year_expense = yearly_expense_allocation * (1 + annual_expense_increase_rate)
            
            projected_investment_return = investment_capital * annual_return_rate
            projected_savings_return = savings_capital * savings_return_rate
            projected_total_returns = projected_investment_return + projected_savings_return
            
            next_year_income = current_monthly_income * 12 if (year + 1) <= years_of_active_income else 0
            projected_total_available = projected_total_returns + next_year_income
            
            if next_year_expense <= projected_total_available:
                yearly_expense_allocation = next_year_expense
            else:
                year_result['expense_frozen'] = True
        
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

@calculator_bp.route('/compare', methods=['POST'])
def compare_scenarios():
    try:
        data = request.get_json()
        scenarios = data.get('scenarios', [])
        
        comparison_results = []
        
        for scenario in scenarios:
            total_capital = float(scenario.get('total_capital', 20000000))
            annual_return_rate = float(scenario.get('annual_return_rate', 20)) / 100
            savings_return_rate = float(scenario.get('savings_return_rate', 4)) / 100
            years = int(scenario.get('years', 5))
            
            investment_capital = total_capital * 0.75
            savings_capital = total_capital * 0.25
            
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

@calculator_bp.route('/save-calculation', methods=['POST'])
def save_calculation():
    try:
        data = request.get_json()
        
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
