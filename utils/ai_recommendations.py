def calculate_required_savings(current_amount, target_amount, annual_return, years):
    if years <= 0:
        return target_amount - current_amount
    
    fv_current = current_amount * ((1 + annual_return) ** years)
    amount_needed = max(0, target_amount - fv_current)
    
    if amount_needed == 0:
        return 0
    
    monthly_rate = annual_return / 12
    months = years * 12
    
    if monthly_rate == 0:
        return amount_needed / months if months > 0 else 0
    
    monthly_payment = amount_needed * monthly_rate / (((1 + monthly_rate) ** months) - 1)
    return monthly_payment


def generate_smart_recommendations(**kwargs):
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
    
    if savings_rate >= 20:
        assessment = "Excellent! Your savings rate is strong and puts you in a great position for financial success."
    elif savings_rate >= 10:
        assessment = "Good progress! You're saving consistently, but there's room for improvement."
    elif savings_rate >= 5:
        assessment = "You're on the right track, but increasing your savings rate should be a priority."
    else:
        assessment = "Your current savings rate is concerning. We need to develop a strategy to increase it significantly."
    
    recommendations['overall_assessment'] = assessment
    
    priority_actions = []
    
    if emergency_fund_months < 3:
        priority_actions.append({
            'priority': 'HIGH',
            'category': 'Emergency Fund',
            'action': f'Build emergency fund to at least 3-6 months of expenses (${kwargs.get("monthly_expenses") * 3:,.2f} - ${kwargs.get("monthly_expenses") * 6:,.2f})',
            'reason': 'Having an emergency fund is crucial for financial stability and prevents debt accumulation during unexpected events.'
        })
    
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
    
    if not has_retirement_plan and age < 50:
        priority_actions.append({
            'priority': 'HIGH',
            'category': 'Retirement Planning',
            'action': 'Start contributing to a retirement account (401k, IRA) immediately',
            'reason': 'The power of compound interest means every year of delay significantly impacts your retirement savings.'
        })
    
    if savings_rate < 15:
        priority_actions.append({
            'priority': 'MEDIUM',
            'category': 'Increase Savings',
            'action': f'Work towards increasing your savings rate from {savings_rate:.1f}% to at least 15-20%',
            'reason': 'Higher savings rate accelerates goal achievement and provides more financial security.'
        })
    
    recommendations['priority_actions'] = priority_actions
    
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
    else:
        allocation = {
            'stocks': 80,
            'bonds': 15,
            'cash': 5,
            'rationale': 'Aggressive allocation maximizes growth potential, suitable for long-term investors who can handle volatility.'
        }
    
    if age > 50:
        allocation['stocks'] -= 10
        allocation['bonds'] += 10
        allocation['rationale'] += ' Adjusted for age to reduce risk as retirement approaches.'
    
    recommendations['portfolio_allocation'] = allocation
    
    current_allocation_str = kwargs.get('current_allocation', '').lower()
    rebalancing_needed = False
    rebalancing_actions = []
    
    if current_allocation_str:
        if 'stock' in current_allocation_str or 'equit' in current_allocation_str:
            if age > 60 and 'aggressive' not in current_allocation_str:
                rebalancing_actions.append('Consider reducing stock exposure as you approach retirement')
                rebalancing_needed = True
            elif age < 40 and 'conservative' in current_allocation_str:
                rebalancing_actions.append('You may benefit from higher stock allocation given your age and time horizon')
                rebalancing_needed = True
        
        if 'crypto' in current_allocation_str or 'bitcoin' in current_allocation_str:
            rebalancing_actions.append('CAUTION: Cryptocurrency should not exceed 5% of portfolio due to high volatility')
            rebalancing_needed = True
        
        if 'single stock' in current_allocation_str or 'one stock' in current_allocation_str:
            rebalancing_actions.append('Diversify away from single-stock concentration - aim for index funds or 20+ holdings')
            rebalancing_needed = True
    
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
    
    monthly_income = kwargs.get('monthly_income', 0)
    monthly_expenses = kwargs.get('monthly_expenses', 0)
    expense_categories = []
    potential_savings = 0
    
    expense_ratio = (monthly_expenses / monthly_income * 100) if monthly_income > 0 else 0
    
    recommended_housing = monthly_income * 0.28
    if monthly_expenses > recommended_housing:
        housing_excess = (monthly_expenses - recommended_housing) * 0.35
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
    
    if expense_ratio > 80:
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
        'target_expense_ratio': 70,
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
        avg_home_price = monthly_income * 12 * 5
        down_payment = avg_home_price * 0.20
        closing_costs = avg_home_price * 0.03
        total_needed = down_payment + closing_costs
        required_monthly = calculate_required_savings(current_capital, total_needed, expected_return * 0.5, time_horizon)
        
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
        cost_per_year = 30000
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
        target_multiple = 10
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
    
    annual_income = monthly_income * 12
    tax_strategies = []
    estimated_tax_savings = 0
    
    if not has_retirement_plan or (has_retirement_plan and savings_rate < 15):
        max_401k = 23000
        max_ira = 7000
        potential_contribution = min(annual_income * 0.15, max_401k)
        tax_rate = 0.22 if annual_income > 50000 else 0.12
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
    
    has_health_insurance = kwargs.get('has_health_insurance', False)
    if has_health_insurance or kwargs.get('willing_to_increase_savings'):
        hsa_limit = 4150
        hsa_tax_savings = hsa_limit * 0.22
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
    
    if current_capital > 50000:
        tlh_savings = current_capital * 0.001
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
    
    recommendations['goal_projection'] = {
        'goal_name': goal_names.get(investment_goal, 'Financial Goal'),
        'time_horizon': time_horizon,
        'projected_value': round(final_value, 2),
        'likelihood': 'High' if savings_rate >= 15 else 'Medium' if savings_rate >= 10 else 'Low',
        'monthly_target': round(kwargs.get('monthly_income') * 0.20, 2)
    }
    
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
