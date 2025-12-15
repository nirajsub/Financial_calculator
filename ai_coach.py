from bytez import Bytez
from datetime import datetime
import json
from typing import List, Dict, Optional


class FinancialCoach:
    def __init__(self):
        self.api_key = "4b7a569738ee991d1c242dd0738158d7"
        self.sdk = Bytez(self.api_key)
        self.model = self.sdk.model("openai/gpt-4o")
        
        self.system_prompt = """You are an expert AI Financial Coach named "FinBot" - a friendly, knowledgeable, and empathetic financial advisor assistant with DEEP UNDERSTANDING of the NFGA Financial Calculator algorithm.

**YOUR ROLE:**
- Provide personalized financial advice and guidance
- Help users understand complex financial concepts in simple terms
- Analyze financial situations and offer actionable recommendations based on the calculator's sophisticated algorithm
- Explain how the calculator works and what projections mean
- Encourage healthy financial habits and long-term thinking
- Be supportive, patient, and non-judgmental

**STRICT RULES:**
1. ONLY discuss financial topics: investments, savings, budgeting, retirement, taxes, insurance, debt management, financial planning, wealth building
2. If user asks about non-financial topics, politely redirect: "I specialize in financial advice. Let's focus on your financial goals! How can I help with your finances?"
3. Never provide medical, legal, or other non-financial advice
4. Always include disclaimers when appropriate: "This is educational guidance, not professional financial advice"
5. Be encouraging but realistic - don't make promises about returns or guarantees

**DEEP KNOWLEDGE OF NFGA CALCULATOR ALGORITHM:**

You have expert understanding of this sophisticated financial projection system:

**CORE ALGORITHM:**
1. **Dual Capital Allocation System:**
   - Total capital split between Investment (higher risk/return) and Savings (lower risk/return)
   - Dynamic allocation: 80/20 split when user has active income, 75/25 when no income
   - Investment account: Typically 8-20% annual return
   - Savings account: Typically 4-8% annual return (safer, liquid)

2. **Monthly Income Integration:**
   - Income flows monthly, grows annually at specified rate
   - Years of active income tracked separately
   - Income is TOP PRIORITY for expense coverage (preserves capital)
   - Surplus income automatically goes to savings account
   - This is revolutionary: most calculators ignore income streams

3. **Sophisticated Expense Management Hierarchy:**
   - **Priority 1**: Cover expenses from monthly/annual income first
   - **Priority 2**: Use investment returns (if income insufficient)
   - **Priority 3**: Use savings returns (if still insufficient)
   - **Priority 4**: Withdraw from savings capital (emergency)
   - **Priority 5**: Withdraw from investment capital (last resort)
   - This preserves capital and maximizes compound growth!

4. **Year 0 (Initial State):**
   - Shows starting allocation before any returns
   - Critical for understanding baseline
   - Most calculators skip this - NFGA shows it!

5. **Precise First Year Calculation:**
   - Month-by-month precision (not just annual)
   - Tracks monthly income receipts
   - Monthly expense withdrawals from savings
   - Monthly compounding on remaining balances
   - Captures realistic cash flow dynamics
   - After Year 1, annual calculations resume

6. **Compounding Methods:**
   - Investment: Annual compounding (typical for stocks/bonds)
   - Savings: Quarterly compounding (typical for high-yield savings)
   - Formula: A = P(1 + r/n)^(nt) where n=compounding frequency

7. **Emergency Fund Mechanism:**
   - Separate emergency fund tracked
   - Can trigger emergency withdrawals when capital depleted
   - Reduces available capital for investment/savings

8. **Advanced Metrics Calculated:**
   - Coverage percentage: (Returns / Expenses) × 100
   - Shows sustainability of lifestyle from returns alone
   - Asset allocation percentages over time
   - Growth rates for each account
   - Total returns vs expenses paid

**HOW TO USE THIS KNOWLEDGE:**

When users ask about their calculations:
- Explain which accounts are being used for what purpose
- Clarify the expense coverage hierarchy
- Show how income preservation works
- Explain month-by-month first year dynamics
- Help optimize their allocation percentages
- Explain why Year 0 matters
- Discuss coverage percentage implications
- Recommend adjustments based on their goals

**EXAMPLE EXPLANATIONS YOU CAN GIVE:**

"Your coverage percentage is 85%, meaning your investment/savings returns cover 85% of your expenses. The remaining 15% comes from your capital, which will gradually deplete it. To be fully sustainable, you need either: higher returns, lower expenses, or more capital."

"Since you have active income of $5,000/month, the calculator uses an 80/20 allocation (more aggressive). Your income covers expenses first, preserving your $500k capital for pure growth. This is optimal!"

"In Year 1, the calculator tracks month-by-month: each month, it takes your expense allocation from savings, calculates returns on remaining balances, then compounds. This is more accurate than simple annual calculation."

"Your emergency fund of $50k is separate from your investment/savings capital. It's your safety net and doesn't generate returns in the calculation."

**YOUR PERSONALITY:**
- Warm and approachable, like a trusted friend
- Use emojis occasionally to be friendly (💰 📊 🎯 💡 ✨)
- Ask clarifying questions to understand context better
- Celebrate wins and progress, no matter how small
- Provide specific, actionable advice with examples
- REFERENCE THE CALCULATOR ALGORITHM when relevant

**CONVERSATION STYLE:**
- Keep responses concise but comprehensive (3-5 paragraphs max)
- Use bullet points for clarity when listing options
- Include relevant numbers, percentages, or calculations
- Reference user's previous statements to show you remember
- Explain calculator mechanics when discussing their results
- End with a question or call-to-action to continue the conversation

**EXPERTISE AREAS:**
- Investment strategies (stocks, bonds, ETFs, index funds)
- Retirement planning (401k, IRA, pension)
- Budgeting and expense tracking
- Emergency funds and savings goals
- Debt reduction strategies
- Tax optimization
- Insurance planning
- Real estate and home buying
- College savings (529 plans)
- Passive income strategies
- **NFGA Calculator interpretation and optimization**

Remember: You're here to educate, empower, and support users on their financial journey with deep understanding of their calculation results! 🚀"""
        
        self.conversations: Dict[str, List[Dict]] = {}
        self.user_context: Dict[str, Dict] = {}
    
    def _check_financial_topic(self, message: str) -> bool:
        financial_keywords = [
            'money', 'finance', 'investment', 'savings', 'budget', 'retirement',
            'stock', 'bond', 'fund', 'portfolio', 'capital', 'wealth', 'income',
            'expense', 'debt', 'loan', 'mortgage', 'credit', 'tax', 'insurance',
            '401k', 'ira', 'roth', 'pension', 'dividend', 'interest', 'return',
            'asset', 'liability', 'equity', 'property', 'real estate', 'college',
            'education', 'emergency fund', 'cash', 'bank', 'account', 'deposit',
            'withdraw', 'dollar', '$', 'save', 'spend', 'invest', 'earn',
            'financial', 'economic', 'market', 'trading', 'crypto', 'bitcoin'
        ]
        
        message_lower = message.lower()
        
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 
                    'good evening', 'how are you', 'what can you do', 'help', 'start']
        if any(greeting in message_lower for greeting in greetings):
            return True
        
        return any(keyword in message_lower for keyword in financial_keywords)
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        return self.conversations[session_id]
    
    def add_user_context(self, session_id: str, context: Dict):
        if session_id not in self.user_context:
            self.user_context[session_id] = {}
        self.user_context[session_id].update(context)
    
    def get_user_context(self, session_id: str) -> Dict:
        return self.user_context.get(session_id, {})
    
    def _build_context_prompt(self, session_id: str) -> str:
        context = self.get_user_context(session_id)
        
        if not context:
            return ""
        
        context_parts = ["\n**USER FINANCIAL CONTEXT:**"]
        
        if 'total_capital' in context:
            context_parts.append(f"- Current Capital: ${context['total_capital']:,.2f}")
        
        if 'monthly_income' in context:
            context_parts.append(f"- Monthly Income: ${context['monthly_income']:,.2f}")
        
        if 'monthly_expenses' in context:
            context_parts.append(f"- Monthly Expenses: ${context['monthly_expenses']:,.2f}")
            
            if 'monthly_income' in context:
                surplus = context['monthly_income'] - context['monthly_expenses']
                if surplus > 0:
                    context_parts.append(f"- Monthly Surplus: ${surplus:,.2f} (Good! 💰)")
                else:
                    context_parts.append(f"- Monthly Deficit: ${abs(surplus):,.2f} (⚠️ Needs attention)")
        
        if 'investment_allocation' in context:
            context_parts.append(f"- Investment Allocation: {context['investment_allocation']}%")
            savings_allocation = 100 - context['investment_allocation']
            context_parts.append(f"- Savings Allocation: {savings_allocation}%")
        
        if 'annual_return_rate' in context:
            context_parts.append(f"- Expected Investment Return: {context['annual_return_rate']}%")
        
        if 'savings_return_rate' in context:
            context_parts.append(f"- Savings Account Return: {context['savings_return_rate']}%")
        
        if 'years' in context:
            context_parts.append(f"- Planning Horizon: {context['years']} years")
        
        if 'investment_goal' in context:
            context_parts.append(f"- Primary Goal: {context['investment_goal']}")
        
        if 'age' in context:
            context_parts.append(f"- Age: {context['age']}")
            if context['age'] < 30:
                context_parts.append("  (Young investor - can take more risk)")
            elif context['age'] < 50:
                context_parts.append("  (Mid-career - balance risk and stability)")
            else:
                context_parts.append("  (Near retirement - focus on preservation)")
        
        if 'risk_tolerance' in context:
            context_parts.append(f"- Risk Tolerance: {context['risk_tolerance']}")
        
        if 'years_of_active_income' in context and context.get('years_of_active_income', 0) > 0:
            context_parts.append(f"- Active Income Duration: {context['years_of_active_income']} years")
            context_parts.append("  (Calculator uses 80/20 allocation with active income)")
        

        if 'calculation_results' in context:
            results = context['calculation_results']
            context_parts.append("\n**RECENT CALCULATION RESULTS:**")
            
            if 'summary' in results:
                summary = results['summary']
                
                if 'growth' in summary:
                    context_parts.append(f"- Total Growth: {summary['growth'].get('total_growth', 0):.1f}%")
                    context_parts.append(f"- Investment Growth: {summary['growth'].get('investment_growth', 0):.1f}%")
                    context_parts.append(f"- Savings Growth: {summary['growth'].get('savings_growth', 0):.1f}%")
                
                if 'final' in summary:
                    final = summary['final']
                    context_parts.append(f"- Final Capital: ${final.get('total', 0):,.2f}")
                    context_parts.append(f"  • Investment: ${final.get('investment', 0):,.2f}")
                    context_parts.append(f"  • Savings: ${final.get('savings', 0):,.2f}")
                
                if 'expenses' in summary:
                    expenses = summary['expenses']
                    context_parts.append(f"- Total Expenses Paid: ${expenses.get('total_actual', 0):,.2f}")
                    context_parts.append(f"- Expenses Saved: ${expenses.get('total_saved', 0):,.2f}")
                
                if 'returns' in summary:
                    returns_sum = summary['returns']
                    context_parts.append(f"- Total Investment Returns: ${returns_sum.get('investment', 0):,.2f}")
                    context_parts.append(f"- Total Savings Returns: ${returns_sum.get('savings', 0):,.2f}")
                
                if 'income' in summary:
                    income = summary['income']
                    total_income = income.get('total_received', 0)
                    if total_income > 0:
                        context_parts.append(f"- Total Income Received: ${total_income:,.2f}")
                        context_parts.append("  (Income covered expenses first, preserving capital)")
                
                if 'returns' in summary and 'expenses' in summary:
                    total_returns = summary['returns'].get('investment', 0) + summary['returns'].get('savings', 0)
                    total_expenses = summary['expenses'].get('total_actual', 0)
                    if total_expenses > 0:
                        coverage = (total_returns / total_expenses) * 100
                        context_parts.append(f"\n- **Coverage Ratio: {coverage:.1f}%**")
                        if coverage >= 100:
                            context_parts.append("  ✅ Returns fully cover expenses - sustainable!")
                        elif coverage >= 80:
                            context_parts.append("  ⚠️ Returns cover most expenses - nearly sustainable")
                        elif coverage >= 50:
                            context_parts.append("  ⚠️ Returns cover half of expenses - capital depleting")
                        else:
                            context_parts.append("  ❌ Returns cover little - rapid capital depletion")
            
            if 'results' in results and len(results['results']) > 1:
                first_year = results['results'][0]
                last_year = results['results'][-1]
                
                if first_year.get('year') == 0:
                    first_year = results['results'][1]
                
                context_parts.append(f"\n**TRAJECTORY ANALYSIS:**")
                context_parts.append(f"- Year {first_year.get('year', 1)} Capital: ${first_year.get('total_capital_end', 0):,.0f}")
                context_parts.append(f"- Year {last_year.get('year', 'Final')} Capital: ${last_year.get('total_capital_end', 0):,.0f}")
                
                capital_change = last_year.get('total_capital_end', 0) - first_year.get('total_capital_end', 0)
                if capital_change > 0:
                    context_parts.append(f"  📈 Capital GROWING by ${capital_change:,.0f}")
                elif capital_change < 0:
                    context_parts.append(f"  📉 Capital DECLINING by ${abs(capital_change):,.0f}")
                else:
                    context_parts.append(f"  ➡️ Capital stable")
        
        context_parts.append("\n**Use this context to provide highly personalized, data-driven advice.**")
        context_parts.append("**Reference specific numbers and calculator mechanics when relevant.**")
        
        return "\n".join(context_parts)
    
    def chat(self, session_id: str, message: str) -> Dict:
        try:
            if not self._check_financial_topic(message):
                return {
                    'success': True,
                    'response': "I appreciate your question, but I specialize exclusively in financial advice! 💰 Let's talk about your finances instead. How can I help you with:\n\n• Investment strategies\n• Budgeting and saving\n• Retirement planning\n• Debt management\n• Financial goal setting\n\nWhat would you like to discuss? 😊",
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'is_financial': False
                }
            
            history = self.get_conversation_history(session_id)
            
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt + self._build_context_prompt(session_id)
                }
            ]
            
            for msg in history[-10:]:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            messages.append({
                "role": "user",
                "content": message
            })
            
            output, error = self.model.run(messages)
            
            if error:
                return {
                    'success': False,
                    'error': str(error),
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }
            
            ai_response = output.get('message', {}).get('content', 'I apologize, I encountered an issue. Please try again.')
            
            history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            history.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'response': ai_response,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'is_financial': True,
                'message_count': len(history)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def clear_conversation(self, session_id: str):
        if session_id in self.conversations:
            self.conversations[session_id] = []
        if session_id in self.user_context:
            del self.user_context[session_id]
    
    def get_conversation_summary(self, session_id: str) -> Dict:
        history = self.get_conversation_history(session_id)
        context = self.get_user_context(session_id)
        
        user_messages = [msg for msg in history if msg['role'] == 'user']
        assistant_messages = [msg for msg in history if msg['role'] == 'assistant']
        
        return {
            'session_id': session_id,
            'total_messages': len(history),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'has_context': bool(context),
            'context_fields': list(context.keys()) if context else [],
            'started_at': history[0]['timestamp'] if history else None,
            'last_activity': history[-1]['timestamp'] if history else None
        }
    
    def suggest_questions(self, session_id: str) -> List[str]:
        context = self.get_user_context(session_id)
        history = self.get_conversation_history(session_id)
        
        default_suggestions = [
            "How should I allocate my investment portfolio?",
            "What's a good emergency fund target?",
            "Help me create a retirement savings plan",
            "How can I reduce my monthly expenses?",
            "What investment strategy fits my risk tolerance?"
        ]
        
        if context:
            suggestions = []
            
            if 'total_capital' in context and context['total_capital'] > 0:
                suggestions.append(f"How can I optimize my ${context['total_capital']:,.0f} portfolio?")
            
            if 'monthly_income' in context and 'monthly_expenses' in context:
                savings = context['monthly_income'] - context['monthly_expenses']
                if savings > 0:
                    suggestions.append(f"What should I do with my ${savings:,.0f} monthly surplus?")
                else:
                    suggestions.append("How can I reduce my expenses to save more?")
            
            if 'investment_goal' in context:
                goal = context['investment_goal']
                if 'retirement' in goal.lower():
                    suggestions.append("Am I on track for retirement?")
                elif 'home' in goal.lower():
                    suggestions.append("How much should I save for a down payment?")
            
            if len(suggestions) < 5:
                suggestions.extend(default_suggestions[:5 - len(suggestions)])
            
            return suggestions[:5]
        
        return default_suggestions


coach = FinancialCoach()
