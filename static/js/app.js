// Enhanced Financial Manager - JavaScript Application
// ================================================

// Global variables
let chartInstances = {};
let currentResults = null;
let emergencyWithdrawalCounter = 0;
let utilizationOverrideCounter = 0;
let currentInputs = null;
const STORAGE_KEY = 'financial_calculations';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    const form = document.getElementById('calculatorForm');
    form.addEventListener('submit', handleFormSubmit);
    
    // Add input formatting
    addInputFormatting();
    
    console.log('Financial Manager App Initialized');
}

// Form submission handler
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // Show loading spinner
    showLoading();
    
    // Collect emergency withdrawals
    const emergencyWithdrawals = [];
    const withdrawalRows = document.querySelectorAll('.emergency-withdrawal-row');
    withdrawalRows.forEach(row => {
        const year = parseInt(row.querySelector('.withdrawal-year').value);
        const amount = parseFloat(row.querySelector('.withdrawal-amount').value);
        if (year && amount && amount > 0) {
            emergencyWithdrawals.push({ year, amount });
        }
    });
    
    // Collect expense utilization overrides
    const expenseUtilizationOverrides = [];
    const overrideRows = document.querySelectorAll('.utilization-override-row');
    overrideRows.forEach(row => {
        const startYear = parseInt(row.querySelector('.override-start-year').value);
        const endYear = parseInt(row.querySelector('.override-end-year').value);
        const rate = parseFloat(row.querySelector('.override-rate').value);
        const reason = row.querySelector('.override-reason').value;
        if (startYear && endYear && rate && startYear <= endYear) {
            expenseUtilizationOverrides.push({ 
                start_year: startYear, 
                end_year: endYear, 
                rate: rate,
                reason: reason || 'Custom override'
            });
        }
    });
    
    // Get form data
    const formData = {
        total_capital: parseFloat(document.getElementById('total_capital').value),
        annual_return_rate: parseFloat(document.getElementById('annual_return_rate').value),
        savings_return_rate: parseFloat(document.getElementById('savings_return_rate').value),
        monthly_expense_allocation: parseFloat(document.getElementById('monthly_expense_allocation').value),
        expense_utilization_rate: parseFloat(document.getElementById('expense_utilization_rate').value),
        annual_expense_increase_rate: parseFloat(document.getElementById('annual_expense_increase_rate').value),
        years: parseInt(document.getElementById('years').value),
        emergency_withdrawals: emergencyWithdrawals,
        expense_utilization_overrides: expenseUtilizationOverrides
    };
    
    // Store current inputs for saving
    currentInputs = formData;
    
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentResults = data;
            displayResults(data);
            
            // Smooth scroll to results
            setTimeout(() => {
                document.getElementById('results').scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 300);
        } else {
            showError(data.error || 'Calculation failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to calculate. Please try again.');
    } finally {
        hideLoading();
    }
}

// Display results
function displayResults(data) {
    const resultsSection = document.getElementById('results');
    resultsSection.classList.remove('hidden');
    
    // Display summary cards
    displaySummaryCards(data.summary);
    
    // Create charts
    createCharts(data.results, data.summary);
    
    // Populate table
    populateTable(data.results);
}

// Display summary cards
function displaySummaryCards(summary) {
    const summaryContainer = document.getElementById('summaryCards');
    
    const cards = [
        {
            title: 'Initial Capital',
            value: formatCurrency(summary.initial.total),
            icon: 'fa-wallet',
            change: null,
            type: 'primary'
        },
        {
            title: 'Final Capital',
            value: formatCurrency(summary.final.total),
            icon: 'fa-chart-line',
            change: {
                value: summary.growth.total,
                positive: summary.growth.total > 0
            },
            type: 'success'
        },
        {
            title: 'Total Returns',
            value: formatCurrency(summary.returns.total),
            icon: 'fa-coins',
            change: null,
            type: 'accent'
        },
        {
            title: 'Investment Growth',
            value: formatCurrency(summary.final.investment),
            icon: 'fa-arrow-trend-up',
            change: {
                value: summary.growth.investment,
                positive: summary.growth.investment > 0
            },
            type: 'primary'
        },
        {
            title: 'Savings Growth',
            value: formatCurrency(summary.final.savings),
            icon: 'fa-piggy-bank',
            change: {
                value: summary.growth.savings,
                positive: summary.growth.savings > 0
            },
            type: 'success'
        },
        {
            title: 'Total Expenses',
            value: formatCurrency(summary.expenses.total_actual),
            icon: 'fa-money-bill-wave',
            change: null,
            type: 'warning'
        }
    ];
    
    // Add emergency withdrawal card if there were any
    if (summary.emergency && summary.emergency.total_withdrawals > 0) {
        cards.push({
            title: 'Emergency Withdrawals',
            value: formatCurrency(summary.emergency.total_withdrawals),
            icon: 'fa-hand-holding-medical',
            change: null,
            type: 'warning',
            subtitle: `${summary.emergency.withdrawal_count} event(s)`
        });
    }
    
    summaryContainer.innerHTML = cards.map(card => `
        <div class="summary-card ${card.type}">
            <div class="summary-card-header">
                <span class="summary-card-title">${card.title}</span>
                <div class="summary-card-icon">
                    <i class="fas ${card.icon}"></i>
                </div>
            </div>
            <div class="summary-card-value">${card.value}</div>
            ${card.subtitle ? `<small style="color: var(--text-secondary); font-size: 0.875rem;">${card.subtitle}</small>` : ''}
            ${card.change ? `
                <span class="summary-card-change ${card.change.positive ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${card.change.positive ? 'up' : 'down'}"></i>
                    ${Math.abs(card.change.value).toFixed(2)}%
                </span>
            ` : ''}
        </div>
    `).join('');
}

// Create all charts
function createCharts(results, summary) {
    // Destroy existing charts
    Object.values(chartInstances).forEach(chart => {
        if (chart) chart.destroy();
    });
    chartInstances = {};
    
    createCapitalGrowthChart(results);
    createAssetAllocationChart(results);
    createReturnsChart(results);
    createExpenseCoverageChart(results);
    createExpenseGrowthChart(results);
    createSavingsChart(results);
    createEmergencyWithdrawalChart(results);
    createUtilizationRateChart(results);
}

// Capital Growth Chart
function createCapitalGrowthChart(results) {
    const ctx = document.getElementById('capitalGrowthChart').getContext('2d');
    
    const years = results.map(r => `Year ${r.year}`);
    const investmentData = results.map(r => r.investment_capital_end);
    const savingsData = results.map(r => r.savings_capital_end);
    const totalData = results.map(r => r.total_capital_end);
    
    chartInstances.capitalGrowth = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Total Capital',
                    data: totalData,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Investment Capital',
                    data: investmentData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Savings Capital',
                    data: savingsData,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ₹' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// Asset Allocation Chart
function createAssetAllocationChart(results) {
    const ctx = document.getElementById('assetAllocationChart').getContext('2d');
    
    const years = results.map(r => `Year ${r.year}`);
    const investmentPercentage = results.map(r => 
        (r.investment_capital_end / r.total_capital_end) * 100
    );
    const savingsPercentage = results.map(r => 
        (r.savings_capital_end / r.total_capital_end) * 100
    );
    
    chartInstances.assetAllocation = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Investment %',
                    data: investmentPercentage,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                },
                {
                    label: 'Savings %',
                    data: savingsPercentage,
                    backgroundColor: '#f59e0b',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Returns Chart
function createReturnsChart(results) {
    const ctx = document.getElementById('returnsChart').getContext('2d');
    
    const years = results.map(r => `Year ${r.year}`);
    const investmentReturns = results.map(r => r.investment_return);
    const savingsReturns = results.map(r => r.savings_return);
    
    chartInstances.returns = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Investment Returns',
                    data: investmentReturns,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                },
                {
                    label: 'Savings Returns',
                    data: savingsReturns,
                    backgroundColor: '#f59e0b',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ₹' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// Expense Coverage Chart
function createExpenseCoverageChart(results) {
    const ctx = document.getElementById('expenseCoverageChart').getContext('2d');
    
    const years = results.map(r => `Year ${r.year}`);
    const coverage = results.map(r => r.coverage_percentage);
    const expenses = results.map(r => r.expense_allocation);
    const returns = results.map(r => r.total_returns);
    
    chartInstances.expenseCoverage = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Coverage %',
                    data: coverage,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Total Returns',
                    data: returns,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    yAxisID: 'y1',
                    tension: 0.4
                },
                {
                    label: 'Expense Allocation',
                    data: expenses,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    yAxisID: 'y1',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Coverage %'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Amount (₹)'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// Expense Growth Chart
function createExpenseGrowthChart(results) {
    const ctx = document.getElementById('expenseGrowthChart').getContext('2d');
    
    const years = results.map(r => `Year ${r.year}`);
    const monthlyExpense = results.map(r => r.monthly_expense_allocation);
    const actualExpense = results.map(r => r.actual_expense / 12);
    const savedExpense = results.map(r => r.savings_from_expense / 12);
    
    chartInstances.expenseGrowth = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Monthly Allocation',
                    data: monthlyExpense,
                    backgroundColor: '#3b82f6',
                    borderRadius: 6
                },
                {
                    label: 'Actual Spent (Monthly)',
                    data: actualExpense,
                    backgroundColor: '#ef4444',
                    borderRadius: 6
                },
                {
                    label: 'Saved (Monthly)',
                    data: savedExpense,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ₹' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// Savings Accumulation Chart
function createSavingsChart(results) {
    const ctx = document.getElementById('savingsChart').getContext('2d');
    
    const years = results.map(r => `Year ${r.year}`);
    const savingsFromExpense = results.map(r => r.savings_from_expense);
    const savingsReturns = results.map(r => r.savings_return);
    
    chartInstances.savings = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Savings from Expense',
                    data: savingsFromExpense,
                    backgroundColor: '#10b981',
                    borderRadius: 6
                },
                {
                    label: 'Savings Returns',
                    data: savingsReturns,
                    backgroundColor: '#f59e0b',
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ₹' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// Emergency Withdrawal Chart
function createEmergencyWithdrawalChart(results) {
    // Check if there are any emergency withdrawals
    const hasEmergencies = results.some(r => r.emergency_withdrawal > 0);
    const chartCard = document.getElementById('emergencyWithdrawalChartCard');
    
    if (!hasEmergencies) {
        chartCard.style.display = 'none';
        return;
    }
    
    chartCard.style.display = 'block';
    
    const ctx = document.getElementById('emergencyChart').getContext('2d');
    
    const years = results.map(r => `Year ${r.year}`);
    const emergencyWithdrawals = results.map(r => r.emergency_withdrawal);
    const totalCapital = results.map(r => r.total_capital_end);
    
    chartInstances.emergency = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Emergency Withdrawal',
                    data: emergencyWithdrawals,
                    backgroundColor: '#ef4444',
                    borderRadius: 6,
                    yAxisID: 'y'
                },
                {
                    label: 'Total Capital After Withdrawal',
                    data: totalCapital,
                    type: 'line',
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ₹' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Withdrawal Amount (₹)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Total Capital (₹)'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// Expense Utilization Rate Chart
function createUtilizationRateChart(results) {
    // Check if there are any utilization overrides
    const hasOverrides = results.some(r => r.utilization_reason && r.utilization_reason !== 'Default');
    const chartCard = document.getElementById('utilizationRateChartCard');
    
    if (!hasOverrides) {
        chartCard.style.display = 'none';
        return;
    }
    
    chartCard.style.display = 'block';
    
    const ctx = document.getElementById('utilizationChart').getContext('2d');
    
    const years = results.map(r => `Year ${r.year}`);
    const utilizationRates = results.map(r => r.expense_utilization_rate);
    const actualExpenses = results.map(r => r.actual_expense);
    const savedFromExpense = results.map(r => r.savings_from_expense);
    
    // Color code based on override
    const backgroundColors = results.map(r => 
        r.utilization_reason && r.utilization_reason !== 'Default' ? '#f59e0b' : '#10b981'
    );
    
    chartInstances.utilization = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Utilization Rate %',
                    data: utilizationRates,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y',
                    pointBackgroundColor: backgroundColors,
                    pointBorderColor: backgroundColors,
                    pointRadius: 6,
                    pointHoverRadius: 8
                },
                {
                    label: 'Actual Expense',
                    data: actualExpenses,
                    type: 'bar',
                    backgroundColor: '#ef4444',
                    borderRadius: 6,
                    yAxisID: 'y1'
                },
                {
                    label: 'Saved from Expense',
                    data: savedFromExpense,
                    type: 'bar',
                    backgroundColor: '#10b981',
                    borderRadius: 6,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label === 'Utilization Rate %') {
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                            }
                            return context.dataset.label + ': ₹' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Utilization Rate %'
                    },
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Amount (₹)'
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '₹' + formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// Populate results table
function populateTable(results) {
    const tbody = document.getElementById('resultsTableBody');
    
    tbody.innerHTML = results.map(row => {
        const isOverridden = row.utilization_reason && row.utilization_reason !== 'Default';
        return `
        <tr>
            <td><strong>Year ${row.year}</strong></td>
            <td>${formatCurrency(row.investment_capital_end)}</td>
            <td>${formatCurrency(row.savings_capital_end)}</td>
            <td><strong>${formatCurrency(row.total_capital_end)}</strong></td>
            <td class="text-success">${formatCurrency(row.investment_return)}</td>
            <td class="text-success">${formatCurrency(row.savings_return)}</td>
            <td class="text-success"><strong>${formatCurrency(row.total_returns)}</strong></td>
            <td>
                ${formatCurrency(row.expense_allocation)}
                ${row.expense_frozen ? '<br><small style="color: #f59e0b;">⚠️ Frozen</small>' : ''}
            </td>
            <td>
                <strong>${row.expense_utilization_rate.toFixed(0)}%</strong>
                ${isOverridden ? `<br><small style="color: #3b82f6;" title="${row.utilization_reason}">📌 ${row.utilization_reason}</small>` : ''}
            </td>
            <td class="text-danger">${formatCurrency(row.actual_expense)}</td>
            <td>
                ${row.emergency_withdrawal > 0 ? 
                    `<span class="text-danger"><strong>₹${formatNumber(row.emergency_withdrawal)}</strong></span>` : 
                    '<span style="color: #9ca3af;">-</span>'}
            </td>
            <td>
                <span class="summary-card-change ${row.coverage_percentage >= 100 ? 'positive' : 'negative'}">
                    ${row.coverage_percentage.toFixed(1)}%
                </span>
            </td>
        </tr>
    `}).join('');
}

// Utility Functions
// ================

function formatCurrency(amount) {
    if (amount >= 10000000) {
        return `₹${(amount / 10000000).toFixed(2)} Cr`;
    } else if (amount >= 100000) {
        return `₹${(amount / 100000).toFixed(2)} L`;
    } else if (amount >= 1000) {
        return `₹${(amount / 1000).toFixed(1)} K`;
    } else {
        return `₹${amount.toFixed(0)}`;
    }
}

function formatNumber(num) {
    if (num >= 10000000) {
        return (num / 10000000).toFixed(2) + ' Cr';
    } else if (num >= 100000) {
        return (num / 100000).toFixed(2) + ' L';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toFixed(0);
}

function showLoading() {
    document.getElementById('loadingSpinner').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loadingSpinner').classList.add('hidden');
}

function showError(message) {
    alert('Error: ' + message);
}

function resetForm() {
    document.getElementById('calculatorForm').reset();
    document.getElementById('results').classList.add('hidden');
    document.getElementById('emergencyWithdrawalsContainer').innerHTML = '';
    document.getElementById('utilizationOverridesContainer').innerHTML = '';
    emergencyWithdrawalCounter = 0;
    utilizationOverrideCounter = 0;
    currentResults = null;
}

// Emergency withdrawal functions
function addEmergencyWithdrawal() {
    emergencyWithdrawalCounter++;
    const container = document.getElementById('emergencyWithdrawalsContainer');
    const maxYears = parseInt(document.getElementById('years').value);
    
    const row = document.createElement('div');
    row.className = 'emergency-withdrawal-row';
    row.style.cssText = 'display: grid; grid-template-columns: 1fr 2fr auto; gap: 1rem; margin-bottom: 0.75rem; align-items: end;';
    row.innerHTML = `
        <div class="form-group" style="margin: 0;">
            <label style="font-size: 0.875rem;">Year</label>
            <input type="number" class="withdrawal-year" min="1" max="${maxYears}" placeholder="Year" required 
                   style="padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1rem; background: #f9fafb;">
        </div>
        <div class="form-group" style="margin: 0;">
            <label style="font-size: 0.875rem;">Amount (₹)</label>
            <input type="number" class="withdrawal-amount" min="0" step="10000" placeholder="Amount" required
                   style="padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1rem; background: #f9fafb;">
        </div>
        <button type="button" class="btn-icon" onclick="removeEmergencyWithdrawal(this)" 
                style="background: #fee2e2; color: #ef4444; margin-bottom: 0;" title="Remove">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    container.appendChild(row);
}

function removeEmergencyWithdrawal(button) {
    button.closest('.emergency-withdrawal-row').remove();
}

// Expense utilization override functions
function addUtilizationOverride() {
    utilizationOverrideCounter++;
    const container = document.getElementById('utilizationOverridesContainer');
    const maxYears = parseInt(document.getElementById('years').value);
    
    const row = document.createElement('div');
    row.className = 'utilization-override-row';
    row.style.cssText = 'display: grid; grid-template-columns: 1fr 1fr 1fr 2fr auto; gap: 1rem; margin-bottom: 0.75rem; align-items: end;';
    row.innerHTML = `
        <div class="form-group" style="margin: 0;">
            <label style="font-size: 0.875rem;">Start Year</label>
            <input type="number" class="override-start-year" min="1" max="${maxYears}" placeholder="From" required 
                   style="padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1rem; background: #f9fafb;">
        </div>
        <div class="form-group" style="margin: 0;">
            <label style="font-size: 0.875rem;">End Year</label>
            <input type="number" class="override-end-year" min="1" max="${maxYears}" placeholder="To" required
                   style="padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1rem; background: #f9fafb;">
        </div>
        <div class="form-group" style="margin: 0;">
            <label style="font-size: 0.875rem;">Rate (%)</label>
            <input type="number" class="override-rate" min="0" max="100" step="1" placeholder="95" required
                   style="padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1rem; background: #f9fafb;">
        </div>
        <div class="form-group" style="margin: 0;">
            <label style="font-size: 0.875rem;">Reason</label>
            <input type="text" class="override-reason" placeholder="e.g., Car EMI" 
                   style="padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1rem; background: #f9fafb;">
        </div>
        <button type="button" class="btn-icon" onclick="removeUtilizationOverride(this)" 
                style="background: #fee2e2; color: #ef4444; margin-bottom: 0;" title="Remove">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    container.appendChild(row);
}

function removeUtilizationOverride(button) {
    button.closest('.utilization-override-row').remove();
}

// Save/Load Calculations
// ======================

function saveCurrentCalculation() {
    if (!currentResults || !currentInputs) {
        alert('No calculation to save. Please run a calculation first.');
        return;
    }
    
    document.getElementById('saveModal').classList.remove('hidden');
    document.getElementById('calculationName').value = '';
    document.getElementById('calculationNotes').value = '';
    document.getElementById('calculationName').focus();
}

function closeSaveModal() {
    document.getElementById('saveModal').classList.add('hidden');
}

function confirmSaveCalculation() {
    const name = document.getElementById('calculationName').value.trim();
    const notes = document.getElementById('calculationNotes').value.trim();
    
    if (!name) {
        alert('Please enter a name for this calculation.');
        return;
    }
    
    const calculation = {
        id: Date.now().toString(),
        name: name,
        notes: notes,
        timestamp: new Date().toISOString(),
        inputs: currentInputs,
        results: currentResults.results,
        summary: currentResults.summary
    };
    
    // Get existing calculations
    const saved = getSavedCalculations();
    saved.push(calculation);
    
    // Save to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
    
    closeSaveModal();
    alert(`Calculation "${name}" saved successfully!`);
    
    // Refresh saved calculations display if visible
    if (document.getElementById('savedCalculationsGrid').children.length > 0) {
        displaySavedCalculations();
    }
}

function getSavedCalculations() {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
}

function showSavedCalculations() {
    displaySavedCalculations();
    document.getElementById('savedCalculations').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
    });
}

function displaySavedCalculations() {
    const saved = getSavedCalculations();
    const container = document.getElementById('savedCalculationsGrid');
    
    if (saved.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">
                <i class="fas fa-folder-open" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                <p style="font-size: 1.125rem;">No saved calculations yet</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem;">Run a calculation and click "Save Calculation" to save it for later</p>
            </div>
        `;
        return;
    }
    
    // Sort by timestamp (newest first)
    saved.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    container.innerHTML = saved.map(calc => {
        const date = new Date(calc.timestamp);
        const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        
        return `
            <div class="saved-calculation-card">
                <div class="saved-calc-header">
                    <h4>${calc.name}</h4>
                    <div class="saved-calc-actions">
                        <button class="btn-icon" onclick="loadCalculation('${calc.id}')" title="Load">
                            <i class="fas fa-folder-open"></i>
                        </button>
                        <button class="btn-icon" onclick="exportCalculation('${calc.id}')" title="Export">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn-icon" onclick="deleteCalculation('${calc.id}')" title="Delete" style="color: #ef4444;">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="saved-calc-info">
                    <small><i class="fas fa-clock"></i> ${dateStr}</small>
                    ${calc.notes ? `<p class="saved-calc-notes">${calc.notes}</p>` : ''}
                </div>
                <div class="saved-calc-summary">
                    <div class="saved-calc-stat">
                        <span class="label">Initial Capital</span>
                        <span class="value">${formatCurrency(calc.summary.initial.total)}</span>
                    </div>
                    <div class="saved-calc-stat">
                        <span class="label">Final Capital</span>
                        <span class="value">${formatCurrency(calc.summary.final.total)}</span>
                    </div>
                    <div class="saved-calc-stat">
                        <span class="label">Growth</span>
                        <span class="value text-success">+${calc.summary.growth.total.toFixed(1)}%</span>
                    </div>
                    <div class="saved-calc-stat">
                        <span class="label">Years</span>
                        <span class="value">${calc.results.length}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function loadCalculation(id) {
    const saved = getSavedCalculations();
    const calculation = saved.find(c => c.id === id);
    
    if (!calculation) {
        alert('Calculation not found.');
        return;
    }
    
    // Restore inputs
    const inputs = calculation.inputs;
    document.getElementById('total_capital').value = inputs.total_capital;
    document.getElementById('annual_return_rate').value = inputs.annual_return_rate;
    document.getElementById('savings_return_rate').value = inputs.savings_return_rate;
    document.getElementById('monthly_expense_allocation').value = inputs.monthly_expense_allocation;
    document.getElementById('expense_utilization_rate').value = inputs.expense_utilization_rate;
    document.getElementById('annual_expense_increase_rate').value = inputs.annual_expense_increase_rate;
    document.getElementById('years').value = inputs.years;
    
    // Clear and restore emergency withdrawals
    document.getElementById('emergencyWithdrawalsContainer').innerHTML = '';
    if (inputs.emergency_withdrawals && inputs.emergency_withdrawals.length > 0) {
        inputs.emergency_withdrawals.forEach(withdrawal => {
            addEmergencyWithdrawal();
            const rows = document.querySelectorAll('.emergency-withdrawal-row');
            const lastRow = rows[rows.length - 1];
            lastRow.querySelector('.withdrawal-year').value = withdrawal.year;
            lastRow.querySelector('.withdrawal-amount').value = withdrawal.amount;
        });
    }
    
    // Clear and restore utilization overrides
    document.getElementById('utilizationOverridesContainer').innerHTML = '';
    if (inputs.expense_utilization_overrides && inputs.expense_utilization_overrides.length > 0) {
        inputs.expense_utilization_overrides.forEach(override => {
            addUtilizationOverride();
            const rows = document.querySelectorAll('.utilization-override-row');
            const lastRow = rows[rows.length - 1];
            lastRow.querySelector('.override-start-year').value = override.start_year;
            lastRow.querySelector('.override-end-year').value = override.end_year;
            lastRow.querySelector('.override-rate').value = override.rate;
            lastRow.querySelector('.override-reason').value = override.reason;
        });
    }
    
    // Restore results
    currentInputs = inputs;
    currentResults = {
        results: calculation.results,
        summary: calculation.summary
    };
    
    displayResults(currentResults);
    
    // Scroll to results
    setTimeout(() => {
        document.getElementById('results').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }, 300);
    
    alert(`Calculation "${calculation.name}" loaded successfully!`);
}

function deleteCalculation(id) {
    if (!confirm('Are you sure you want to delete this calculation?')) {
        return;
    }
    
    let saved = getSavedCalculations();
    saved = saved.filter(c => c.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
    
    displaySavedCalculations();
    alert('Calculation deleted successfully.');
}

function exportCalculation(id) {
    const saved = getSavedCalculations();
    const calculation = saved.find(c => c.id === id);
    
    if (!calculation) {
        alert('Calculation not found.');
        return;
    }
    
    const dataStr = JSON.stringify(calculation, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${calculation.name.replace(/[^a-z0-9]/gi, '_')}_${calculation.id}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
}

function exportCurrentCalculation() {
    if (!currentResults || !currentInputs) {
        alert('No calculation to export. Please run a calculation first.');
        return;
    }
    
    const calculation = {
        id: Date.now().toString(),
        name: 'Exported Calculation',
        timestamp: new Date().toISOString(),
        inputs: currentInputs,
        results: currentResults.results,
        summary: currentResults.summary
    };
    
    const dataStr = JSON.stringify(calculation, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `financial_calculation_${calculation.id}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
}

function exportAllCalculations() {
    const saved = getSavedCalculations();
    
    if (saved.length === 0) {
        alert('No saved calculations to export.');
        return;
    }
    
    const dataStr = JSON.stringify(saved, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `all_financial_calculations_${Date.now()}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
}

function importCalculations() {
    document.getElementById('importFileInput').click();
}

function handleImportFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const imported = JSON.parse(e.target.result);
            let saved = getSavedCalculations();
            
            // Check if it's a single calculation or array
            const toImport = Array.isArray(imported) ? imported : [imported];
            
            // Add unique IDs if missing
            toImport.forEach(calc => {
                if (!calc.id) {
                    calc.id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
                }
            });
            
            // Merge with existing
            saved = saved.concat(toImport);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
            
            displaySavedCalculations();
            alert(`Successfully imported ${toImport.length} calculation(s)!`);
        } catch (error) {
            alert('Error importing file: ' + error.message);
        }
    };
    reader.readAsText(file);
    
    // Reset file input
    event.target.value = '';
}

// Add input formatting
function addInputFormatting() {
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.select();
        });
    });
}

// Export table to CSV
function exportTableToCSV() {
    if (!currentResults) return;
    
    const results = currentResults.results;
    
    // CSV headers
    let csv = 'Year,Investment Capital,Savings Capital,Total Capital,Investment Return,Savings Return,Total Returns,Expense Allocation,Actual Expense,Coverage %\n';
    
    // CSV data
    results.forEach(row => {
        csv += `${row.year},`;
        csv += `${row.investment_capital_end},`;
        csv += `${row.savings_capital_end},`;
        csv += `${row.total_capital_end},`;
        csv += `${row.investment_return},`;
        csv += `${row.savings_return},`;
        csv += `${row.total_returns},`;
        csv += `${row.expense_allocation},`;
        csv += `${row.actual_expense},`;
        csv += `${row.coverage_percentage.toFixed(2)}\n`;
    });
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'financial_projections.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Download chart as image
function downloadChart(chartId) {
    const canvas = document.getElementById(chartId);
    const url = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = url;
    a.download = chartId + '.png';
    a.click();
}
