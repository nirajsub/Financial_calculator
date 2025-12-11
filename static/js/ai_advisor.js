// AI Advisor JavaScript

// Calculate and display savings rate
document.getElementById('monthlyIncome').addEventListener('input', updateSavingsRate);
document.getElementById('monthlyExpenses').addEventListener('input', updateSavingsRate);

function updateSavingsRate() {
    const income = parseFloat(document.getElementById('monthlyIncome').value) || 0;
    const expenses = parseFloat(document.getElementById('monthlyExpenses').value) || 0;
    
    if (income > 0) {
        const savings = income - expenses;
        const savingsRate = (savings / income * 100).toFixed(1);
        const badge = document.getElementById('savingsRate');
        
        if (savings > 0) {
            badge.innerHTML = `<i class="fas fa-info-circle"></i> Savings Rate: ${savingsRate}% ($${savings.toFixed(2)}/month)`;
            badge.className = 'info-badge';
            
            if (savingsRate >= 20) {
                badge.classList.add('text-success');
            } else if (savingsRate >= 10) {
                badge.classList.add('text-warning');
            } else {
                badge.classList.add('text-danger');
            }
        } else {
            badge.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Warning: Expenses exceed income!`;
            badge.className = 'info-badge text-danger';
        }
    }
}

// Form submission
document.getElementById('aiAdvisorForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Collect form data
    const formData = {
        age: parseInt(document.getElementById('age').value),
        riskTolerance: document.getElementById('riskTolerance').value,
        investmentGoal: document.getElementById('investmentGoal').value,
        timeHorizon: parseInt(document.getElementById('timeHorizon').value),
        currentCapital: parseFloat(document.getElementById('currentCapital').value),
        monthlyIncome: parseFloat(document.getElementById('monthlyIncome').value),
        monthlyExpenses: parseFloat(document.getElementById('monthlyExpenses').value),
        existingDebts: parseFloat(document.getElementById('existingDebts').value) || 0,
        emergencyFund: parseFloat(document.getElementById('emergencyFund').value) || 0,
        expectedReturn: parseFloat(document.getElementById('expectedReturn').value),
        currentAllocation: document.getElementById('currentAllocation').value,
        hasRetirementPlan: document.getElementById('hasRetirementPlan').checked,
        hasHealthInsurance: document.getElementById('hasHealthInsurance').checked,
        willingToIncreaseSavings: document.getElementById('willingToIncreaseSavings').checked,
        planningMajorPurchase: document.getElementById('planningMajorPurchase').checked,
        specificQuestions: document.getElementById('specificQuestions').value
    };
    
    // Validate
    if (formData.monthlyExpenses > formData.monthlyIncome) {
        alert('Warning: Your monthly expenses exceed your income. Please review your budget.');
    }
    
    // Show loading
    showLoadingModal();
    
    try {
        const response = await fetch('/api/ai/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayRecommendations(result.recommendations, result.metrics, result.projections);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while getting recommendations. Please try again.');
    } finally {
        hideLoadingModal();
    }
});

function showLoadingModal() {
    const modal = document.getElementById('loadingModal');
    modal.classList.remove('hidden');
    
    const messages = [
        'Analyzing your financial profile...',
        'Calculating projections...',
        'Evaluating risk factors...',
        'Generating recommendations...',
        'Creating action plan...'
    ];
    
    let index = 0;
    let progress = 0;
    
    const messageElement = document.getElementById('loadingMessage');
    const progressBar = document.getElementById('progressBar');
    
    const interval = setInterval(() => {
        index = (index + 1) % messages.length;
        messageElement.textContent = messages[index];
        
        progress += 20;
        progressBar.style.width = Math.min(progress, 90) + '%';
        
        if (progress >= 90) {
            clearInterval(interval);
        }
    }, 600);
    
    // Store interval ID to clear later
    modal.dataset.intervalId = interval;
}

function hideLoadingModal() {
    const modal = document.getElementById('loadingModal');
    const intervalId = modal.dataset.intervalId;
    
    if (intervalId) {
        clearInterval(parseInt(intervalId));
    }
    
    const progressBar = document.getElementById('progressBar');
    progressBar.style.width = '100%';
    
    setTimeout(() => {
        modal.classList.add('hidden');
        progressBar.style.width = '0%';
    }, 500);
}

function displayRecommendations(recommendations, metrics, projections) {
    const content = document.getElementById('recommendationsContent');
    
    // Build HTML
    let html = '';
    
    // Overall Assessment
    html += `
        <div class="assessment-box">
            <h3><i class="fas fa-clipboard-check"></i> Overall Assessment</h3>
            <p>${recommendations.overall_assessment}</p>
        </div>
    `;
    
    // Key Metrics
    html += `
        <div class="recommendation-section">
            <div class="section-header">
                <i class="fas fa-chart-bar"></i>
                <h3>Key Financial Metrics</h3>
            </div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">${metrics.savings_rate.toFixed(1)}%</span>
                    <span class="metric-label">Savings Rate</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">$${formatNumber(metrics.monthly_savings)}</span>
                    <span class="metric-label">Monthly Savings</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">$${formatNumber(metrics.final_value)}</span>
                    <span class="metric-label">Projected Value</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">$${formatNumber(metrics.total_returns)}</span>
                    <span class="metric-label">Total Returns</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">${metrics.emergency_fund_months.toFixed(1)}</span>
                    <span class="metric-label">Emergency Fund (months)</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">${metrics.debt_to_income.toFixed(1)}%</span>
                    <span class="metric-label">Debt-to-Income</span>
                </div>
            </div>
        </div>
    `;
    
    // Priority Actions
    if (recommendations.priority_actions.length > 0) {
        html += `
            <div class="recommendation-section">
                <div class="section-header">
                    <i class="fas fa-exclamation-circle"></i>
                    <h3>Priority Actions</h3>
                </div>
                <ul class="action-list">
        `;
        
        recommendations.priority_actions.forEach(action => {
            html += `
                <li class="action-item">
                    <i class="fas fa-arrow-right"></i>
                    <div class="action-content">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span class="priority-badge ${action.priority.toLowerCase()}">${action.priority}</span>
                            <strong>${action.category}</strong>
                        </div>
                        <h4>${action.action}</h4>
                        <p>${action.reason}</p>
                    </div>
                </li>
            `;
        });
        
        html += `
                </ul>
            </div>
        `;
    }
    
    // Portfolio Allocation
    html += `
        <div class="recommendation-section">
            <div class="section-header">
                <i class="fas fa-chart-pie"></i>
                <h3>Recommended Portfolio Allocation</h3>
            </div>
            <div class="allocation-chart">
                <div class="allocation-item">
                    <span class="allocation-percentage">${recommendations.portfolio_allocation.stocks}%</span>
                    <span class="allocation-label">Stocks/Equities</span>
                </div>
                <div class="allocation-item">
                    <span class="allocation-percentage">${recommendations.portfolio_allocation.bonds}%</span>
                    <span class="allocation-label">Bonds</span>
                </div>
                <div class="allocation-item">
                    <span class="allocation-percentage">${recommendations.portfolio_allocation.cash}%</span>
                    <span class="allocation-label">Cash/Savings</span>
                </div>
            </div>
            <p style="margin-top: 1rem; color: var(--text-secondary); font-style: italic;">
                ${recommendations.portfolio_allocation.rationale}
            </p>
        </div>
    `;
    
    // Risk Analysis
    html += `
        <div class="recommendation-section">
            <div class="section-header">
                <i class="fas fa-shield-alt"></i>
                <h3>Risk Analysis</h3>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 3rem; color: ${recommendations.risk_analysis.risk_level === 'High' ? 'var(--danger-color)' : recommendations.risk_analysis.risk_level === 'Medium' ? 'var(--warning-color)' : 'var(--success-color)'};">
                    ${recommendations.risk_analysis.risk_score}/4
                </div>
                <div>
                    <strong style="font-size: 1.25rem; color: var(--text-primary);">Risk Level: ${recommendations.risk_analysis.risk_level}</strong>
                    <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary);">
                        ${recommendations.risk_analysis.risk_factors.length} risk factors identified
                    </p>
                </div>
            </div>
            ${recommendations.risk_analysis.risk_factors.length > 0 ? `
                <ul style="list-style: none; padding: 0; margin: 1rem 0;">
                    ${recommendations.risk_analysis.risk_factors.map(factor => `
                        <li style="padding: 0.5rem 0; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-exclamation-triangle" style="color: var(--warning-color);"></i>
                            ${factor}
                        </li>
                    `).join('')}
                </ul>
            ` : '<p style="color: var(--success-color);"><i class="fas fa-check-circle"></i> No major risk factors identified!</p>'}
        </div>
    `;
    
    // Goal Projection
    html += `
        <div class="recommendation-section">
            <div class="section-header">
                <i class="fas fa-bullseye"></i>
                <h3>${recommendations.goal_projection.goal_name} Projection</h3>
            </div>
            <div style="padding: 1.5rem; background: var(--bg-primary); border-radius: var(--border-radius); margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="color: var(--text-secondary);">Time Horizon:</span>
                    <strong style="color: var(--text-primary);">${recommendations.goal_projection.time_horizon} years</strong>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="color: var(--text-secondary);">Projected Value:</span>
                    <strong style="color: var(--primary-color); font-size: 1.5rem;">$${formatNumber(recommendations.goal_projection.projected_value)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--text-secondary);">Success Likelihood:</span>
                    <strong style="color: ${recommendations.goal_projection.likelihood === 'High' ? 'var(--success-color)' : recommendations.goal_projection.likelihood === 'Medium' ? 'var(--warning-color)' : 'var(--danger-color)'};">
                        ${recommendations.goal_projection.likelihood}
                    </strong>
                </div>
            </div>
        </div>
    `;
    
    // Detailed Insights
    if (recommendations.detailed_insights.length > 0) {
        html += `
            <div class="recommendation-section">
                <div class="section-header">
                    <i class="fas fa-lightbulb"></i>
                    <h3>Detailed Insights</h3>
                </div>
        `;
        
        recommendations.detailed_insights.forEach(insight => {
            html += `
                <div class="insight-card">
                    <div class="insight-icon">
                        <i class="fas fa-${insight.icon}"></i>
                    </div>
                    <div class="insight-content">
                        <h4>${insight.title}</h4>
                        <p>${insight.content}</p>
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    // Portfolio Rebalancing (NEW)
    if (recommendations.portfolio_rebalancing) {
        html += `
            <div class="recommendation-section ${recommendations.portfolio_rebalancing.needed ? 'priority-medium' : ''}">
                <div class="section-header">
                    <i class="fas fa-balance-scale"></i>
                    <h3>Portfolio Rebalancing</h3>
                    ${recommendations.portfolio_rebalancing.needed ? '<span class="priority-badge medium">Action Needed</span>' : ''}
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Next Review:</strong> ${recommendations.portfolio_rebalancing.next_review_date}
                </div>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    ${recommendations.portfolio_rebalancing.actions.map(action => `
                        <li style="padding: 0.5rem 0; color: var(--text-primary); display: flex; align-items: flex-start; gap: 0.5rem;">
                            <i class="fas fa-${recommendations.portfolio_rebalancing.needed ? 'exclamation-circle' : 'check-circle'}" style="color: var(--${recommendations.portfolio_rebalancing.needed ? 'warning' : 'success'}-color); margin-top: 0.25rem;"></i>
                            <span>${action}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    // Expense Optimization (NEW)
    if (recommendations.expense_optimization) {
        html += `
            <div class="recommendation-section">
                <div class="section-header">
                    <i class="fas fa-cut"></i>
                    <h3>Expense Optimization</h3>
                </div>
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 1.5rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">💰 Total Savings Potential</div>
                    <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">$${formatNumber(recommendations.expense_optimization.total_potential_savings)}/month</div>
                    <div style="font-size: 1.1rem;">$${formatNumber(recommendations.expense_optimization.annual_savings_potential)}/year</div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Current Expense Ratio:</span>
                        <strong>${recommendations.expense_optimization.expense_ratio}%</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Target Ratio:</span>
                        <strong style="color: var(--success-color);">${recommendations.expense_optimization.target_expense_ratio}%</strong>
                    </div>
                </div>
                
                ${recommendations.expense_optimization.categories.map(cat => `
                    <div style="background: var(--bg-primary); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1rem; border-left: 4px solid var(--primary-color);">
                        <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">
                            ${cat.category}
                            ${cat.savings_potential ? `<span style="color: var(--success-color); font-size: 0.9rem;"> (Save: $${formatNumber(cat.savings_potential)}/mo)</span>` : ''}
                        </h4>
                        ${cat.current ? `<div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.25rem;">Current: ${cat.current}</div>` : ''}
                        ${cat.recommended ? `<div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.75rem;">Recommended: ${cat.recommended}</div>` : ''}
                        ${cat.message ? `<div style="color: var(--text-secondary); margin-bottom: 0.75rem;">${cat.message}</div>` : ''}
                        ${cat.tips ? `
                            <ul style="list-style: none; padding: 0; margin: 0;">
                                ${cat.tips.map(tip => `
                                    <li style="padding: 0.25rem 0; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem;">
                                        <i class="fas fa-lightbulb" style="color: var(--warning-color);"></i>
                                        ${tip}
                                    </li>
                                `).join('')}
                            </ul>
                        ` : ''}
                    </div>
                `).join('')}
                
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--border-radius);">
                    <h4 style="margin: 0 0 0.75rem 0;">🎯 Quick Wins</h4>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${recommendations.expense_optimization.quick_wins.map(win => `
                            <li style="padding: 0.5rem 0; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
                                <i class="fas fa-star" style="color: var(--warning-color);"></i>
                                ${win}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    // Goal Planning (NEW - Enhanced)
    if (recommendations.goal_planning) {
        const goal = recommendations.goal_planning;
        html += `
            <div class="recommendation-section">
                <div class="section-header">
                    <i class="fas fa-bullseye"></i>
                    <h3>Goal Planning: ${goal.goal_type}</h3>
                </div>
                
                <div style="background: var(--bg-primary); padding: 1.5rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1rem;">
                        <div>
                            <div style="color: var(--text-secondary); font-size: 0.9rem;">Target Amount</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">$${formatNumber(goal.target_amount)}</div>
                        </div>
                        <div>
                            <div style="color: var(--text-secondary); font-size: 0.9rem;">Time Remaining</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">${goal.years_remaining} years</div>
                        </div>
                        <div>
                            <div style="color: var(--text-secondary); font-size: 0.9rem;">Current Progress</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: ${goal.current_progress >= 50 ? 'var(--success-color)' : 'var(--warning-color)'};">${goal.current_progress}%</div>
                        </div>
                        <div>
                            <div style="color: var(--text-secondary); font-size: 0.9rem;">Required Monthly</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: ${goal.on_track ? 'var(--success-color)' : 'var(--danger-color)'};">$${formatNumber(goal.required_monthly_savings)}</div>
                        </div>
                    </div>
                    
                    <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--border-radius); text-align: center;">
                        <strong style="color: ${goal.on_track ? 'var(--success-color)' : 'var(--danger-color)'};">
                            ${goal.on_track ? '✓ On Track!' : '⚠ Need to Increase Savings'}
                        </strong>
                    </div>
                </div>
                
                <h4 style="margin: 1rem 0 0.75rem 0;">📋 Specific Recommendations:</h4>
                <ul style="list-style: none; padding: 0; margin: 0;">
                    ${goal.recommendations.map(rec => `
                        <li style="padding: 0.5rem 0; color: var(--text-primary); display: flex; align-items: flex-start; gap: 0.5rem;">
                            <i class="fas fa-check-circle" style="color: var(--success-color); margin-top: 0.25rem;"></i>
                            <span>${rec}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    // Tax Efficiency (NEW)
    if (recommendations.tax_efficiency) {
        html += `
            <div class="recommendation-section">
                <div class="section-header">
                    <i class="fas fa-file-invoice-dollar"></i>
                    <h3>Tax Efficiency Strategies</h3>
                </div>
                
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1.5rem; border-radius: var(--border-radius); margin-bottom: 1rem; text-align: center;">
                    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">💵 Estimated Annual Tax Savings</div>
                    <div style="font-size: 2.5rem; font-weight: 700;">$${formatNumber(recommendations.tax_efficiency.estimated_annual_savings)}</div>
                </div>
                
                ${recommendations.tax_efficiency.strategies.map(strategy => `
                    <div style="background: var(--bg-primary); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1rem; border-left: 4px solid var(--success-color);">
                        <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary); display: flex; align-items: center; justify-content: space-between;">
                            <span>${strategy.strategy}</span>
                            <span style="color: var(--success-color); font-size: 0.9rem;">Save: $${typeof strategy.tax_savings === 'number' ? formatNumber(strategy.tax_savings) : strategy.tax_savings}</span>
                        </h4>
                        <ul style="list-style: none; padding: 0; margin: 0;">
                            ${strategy.details.map(detail => `
                                <li style="padding: 0.25rem 0; color: var(--text-secondary); display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.9rem;">
                                    <i class="fas fa-check" style="color: var(--success-color); margin-top: 0.25rem;"></i>
                                    <span>${detail}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `).join('')}
                
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                    <h4 style="margin: 0 0 0.75rem 0;">🎯 Priority Order:</h4>
                    <ol style="margin: 0; padding-left: 1.5rem;">
                        ${recommendations.tax_efficiency.priority_order.map(priority => `
                            <li style="padding: 0.25rem 0; color: var(--text-primary);">${priority}</li>
                        `).join('')}
                    </ol>
                </div>
                
                <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: var(--border-radius);">
                    <h4 style="margin: 0 0 0.75rem 0;">📝 Tax Filing Tips:</h4>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${recommendations.tax_efficiency.tax_filing_tips.map(tip => `
                            <li style="padding: 0.25rem 0; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem;">
                                <i class="fas fa-info-circle" style="color: var(--primary-color);"></i>
                                ${tip}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }
    
    // Savings Strategy (Enhanced)
    html += `
        <div class="recommendation-section">
            <div class="section-header">
                <i class="fas fa-piggy-bank"></i>
                <h3>Savings Strategy Summary</h3>
            </div>
            <div style="background: var(--bg-primary); padding: 1rem; border-radius: var(--border-radius); margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Current Monthly Savings:</span>
                    <strong>$${formatNumber(recommendations.savings_strategy.current_monthly)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Recommended Monthly:</span>
                    <strong style="color: var(--success-color);">$${formatNumber(recommendations.savings_strategy.recommended_monthly)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>With Expense Optimization:</span>
                    <strong style="color: var(--success-color);">+$${formatNumber(recommendations.savings_strategy.with_expense_optimization)}/year</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>With Tax Efficiency:</span>
                    <strong style="color: var(--success-color);">+$${formatNumber(recommendations.savings_strategy.with_tax_efficiency)}/year</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; border-top: 2px solid var(--border-color); margin-top: 0.5rem;">
                    <span><strong>Total Potential Boost:</strong></span>
                    <strong style="color: var(--primary-color); font-size: 1.25rem;">$${formatNumber(recommendations.savings_strategy.total_potential_boost)}/year</strong>
                </div>
            </div>
            <h4 style="margin: 1rem 0 0.5rem 0;">Recommended Strategies:</h4>
            <ul style="list-style: none; padding: 0; margin: 0;">
                ${recommendations.savings_strategy.strategies.map(strategy => `
                    <li style="padding: 0.5rem 0; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-check" style="color: var(--success-color);"></i>
                        ${strategy}
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
    
    // Action Plan
    if (recommendations.action_plan.length > 0) {
        html += `
            <div class="recommendation-section">
                <div class="section-header">
                    <i class="fas fa-tasks"></i>
                    <h3>Action Plan</h3>
                </div>
                <div class="timeline">
        `;
        
        recommendations.action_plan.forEach(phase => {
            html += `
                <div class="timeline-item">
                    <div class="timeline-header">${phase.timeline}</div>
                    <div class="timeline-content">
                        <ul>
                            ${phase.actions.map(action => `<li>${action}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // Set content
    content.innerHTML = html;
    
    // Show action buttons
    document.getElementById('panelActions').classList.remove('hidden');
    
    // Scroll to top of recommendations
    document.getElementById('recommendationsPanel').scrollIntoView({ behavior: 'smooth' });
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(num);
}

function exportRecommendations() {
    alert('PDF export feature coming soon! This will export your personalized recommendations as a PDF document.');
}

function saveRecommendations() {
    const recommendations = document.getElementById('recommendationsContent').innerHTML;
    
    if (recommendations && !recommendations.includes('empty-state')) {
        localStorage.setItem('ai_recommendations', recommendations);
        localStorage.setItem('ai_recommendations_date', new Date().toISOString());
        alert('Recommendations saved successfully!');
    } else {
        alert('No recommendations to save. Please generate recommendations first.');
    }
}

function resetForm() {
    if (confirm('Are you sure you want to start over? This will clear the form and recommendations.')) {
        document.getElementById('aiAdvisorForm').reset();
        document.getElementById('savingsRate').innerHTML = '<i class="fas fa-info-circle"></i> Savings Rate: --';
        
        const content = document.getElementById('recommendationsContent');
        content.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-robot"></i>
                <h3>Ready to Help!</h3>
                <p>Fill out the questionnaire on the left, and I'll analyze your financial situation to provide personalized recommendations.</p>
                <div class="features-preview">
                    <div class="feature-item">
                        <i class="fas fa-chart-pie"></i>
                        <span>Portfolio Analysis</span>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-bullseye"></i>
                        <span>Goal Planning</span>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-shield-alt"></i>
                        <span>Risk Assessment</span>
                    </div>
                    <div class="feature-item">
                        <i class="fas fa-route"></i>
                        <span>Action Plan</span>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('panelActions').classList.add('hidden');
    }
}
