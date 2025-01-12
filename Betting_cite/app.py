from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///betting.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=100.0)
    last_bonus = db.Column(db.DateTime, default=datetime.utcnow)

class BettingLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    over_under_value = db.Column(db.Float, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    result = db.Column(db.String(10), nullable=True)  # 'over' or 'under' when resolved

class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    line_id = db.Column(db.Integer, db.ForeignKey('betting_line.id'))
    amount = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.String(10), nullable=False)  # 'over' or 'under'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_won = db.Column(db.Boolean, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('current_bets'))

@app.route('/current_bets')
def current_bets():
    betting_lines = BettingLine.query.filter_by(is_active=True).all()
    return render_template('current_bets.html', betting_lines=betting_lines)

@app.route("/api/close_betting_line/<int:line_id>", methods=['POST'])
@login_required
def close_betting_line(line_id):
    line = BettingLine.query.get_or_404(line_id)
    
    # Verify user owns this betting line
    if line.created_by != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    result = request.json.get('result')
    if result not in ['over', 'under']:
        return jsonify({"error": "Invalid result"}), 400
    
    line.is_active = False
    line.result = result
    
    # Get all bets for this line
    bets = Bet.query.filter_by(line_id=line_id).all()
    
    # Calculate total pot and winning pot
    total_pot = sum(bet.amount for bet in bets)
    winning_pot = sum(bet.amount for bet in bets if bet.prediction == result)
    
    # Process all bets
    for bet in bets:
        bet.is_won = (bet.prediction == result)
        if bet.is_won and winning_pot > 0:  # Prevent division by zero
            # Calculate proportional winnings
            win_ratio = bet.amount / winning_pot
            winnings = total_pot * win_ratio
            
            # Update user balance
            user = User.query.get(bet.user_id)
            user.balance += winnings
    
    db.session.commit()
    return jsonify({"message": "Betting line closed successfully"}), 200

@app.route('/create_betting_line', methods=['POST'])
@login_required
def create_betting_line():
    description = request.form.get('description')
    value = float(request.form.get('value'))
    
    new_line = BettingLine(
        description=description,
        over_under_value=value,
        created_by=current_user.id
    )
    db.session.add(new_line)
    db.session.commit()
    
    flash('Betting line created successfully!', 'success')
    return redirect(url_for('current_bets'))

@app.route('/place_bet/<int:line_id>', methods=['POST'])
@login_required
def place_bet(line_id):
    amount = float(request.form.get('amount'))
    prediction = request.form.get('prediction')
    
    if amount <= 0 or amount > current_user.balance:
        flash('Invalid bet amount!', 'danger')
        return redirect(url_for('current_bets'))
    
    new_bet = Bet(
        user_id=current_user.id,
        line_id=line_id,
        amount=amount,
        prediction=prediction
    )
    
    current_user.balance -= amount
    db.session.add(new_bet)
    db.session.commit()
    
    flash('Bet placed successfully!', 'success')
    return redirect(url_for('current_bets'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('current_bets'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Weekly bonus function
def add_weekly_bonus():
    with app.app_context():
        users = User.query.all()
        for user in users:
            if datetime.utcnow() - user.last_bonus >= timedelta(days=7):
                user.balance += 100
                user.last_bonus = datetime.utcnow()
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
