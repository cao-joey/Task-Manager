from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Task

app = Flask(__name__)

# Config 
app.config['SECRET_KEY'] = 'some key here' # Encrypt cookie session
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db' # Stores db in tasks.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirects users if not logged in

# Load user by ID -- used to remember which user is logged in
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database when first run
with app.app_context():
    db.create_all()

# ==================== AUTHENTICATION ====================
# Registration 
@app.route('/register', methods=['GET','POST'])
def register():
    # If user is already logged in, just jump to index page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Get data from registration form
    if request.method == 'POST':
        user = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        # Check if all text fields have been filled
        if not user or not email or not password or not name:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))
        
        # Check if user already exists
        if User.query.filter_by(username=user).first(): 
            flash('Username in use.', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        # Otherwise: new user can be created
        user = User(username=user, email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit() # Save to DB

        flash('Registration sucessful! Please log in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html')


# Login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, just jump to index page
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Get info from login form
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first() 
        if user and user.check_password(password): # If user exists and password matches
            login_user(user)
            flash(f'Welcome {user.name}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful', 'success')
    return redirect(url_for('login'))

# ==================== APPLICATION ====================
@app.route('/')
@login_required
def index():
    # Display user's tasks -- display in descending order (newest displayed first)
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
@login_required
def add():
    task_text = request.form.get('task')
    # Create new task
    if task_text:
        new_task = Task(text=task_text, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
@login_required
def toggle(task_id): # Change task completion status
    task = Task.query.get_or_404(task_id)

    # Check permissions
    if task.user_id != current_user.id: 
        flash('Unauthorized action', 'error')
        return redirect(url_for('index'))
    
    # Proceed to change
    task.done = not task.done # Switch status 
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
@login_required
def delete(task_id):
    task = Task.query.get_or_404(task_id)

    # Check permissions
    if task.user_id != current_user.id: 
        flash('Unauthorized action', 'error')
        return redirect(url_for('index'))

    # Proceed to delete
    db.session.delete(task)
    db.session.commit()
    flash('Task removed', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
