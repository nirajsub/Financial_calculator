from flask import Flask, render_template
from decouple import config
from routes.calculator_routes import calculator_bp
from routes.ai_advisor_routes import ai_advisor_bp
from routes.coach_routes import coach_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY')

app.register_blueprint(calculator_bp)
app.register_blueprint(ai_advisor_bp)
app.register_blueprint(coach_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
