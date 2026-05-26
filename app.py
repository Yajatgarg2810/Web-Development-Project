# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database initialization
def init_db():
    conn = sqlite3.connect('workers.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  mobile TEXT NOT NULL,
                  password TEXT NOT NULL)''')
    
    # Create workers table
    c.execute('''CREATE TABLE IF NOT EXISTS workers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  age INTEGER NOT NULL,
                  gender TEXT NOT NULL,
                  mobile TEXT NOT NULL UNIQUE,
                  address TEXT NOT NULL,
                  job_title TEXT NOT NULL,
                  experience INTEGER NOT NULL,
                  profile_image TEXT,
                  verified INTEGER DEFAULT 0)''')
    
    # Insert some sample maids
    c.execute("SELECT COUNT(*) FROM workers")
    if c.fetchone()[0] == 0:
        sample_workers = [
            ('Emily', 29, 'Female', '123-456-7890', 'Mahaveer Nagar', 'Housekeeper', 5, 'emily.jpg', 1),
            ('Fiona', 32, 'Female', '987-654-3210', 'Saket', 'Nanny', 7, 'fiona.jpg', 1),
            ('Grace', 25, 'Female', '456-789-1230', 'Vasant Vihar', 'Cleaner', 3, 'grace.jpg', 1),
            ('Hannah', 40, 'Female', '321-654-9870', 'Dwarka', 'Cook', 15, 'hannah.jpg', 1),
            ('Olivia', 30, 'Female', '789-123-4560', 'Mahaveer Nagar', 'Housekeeper', 6, 'olivia.jpg', 1),
            ('Sophia', 35, 'Female', '654-321-9870', 'Karol Bagh', 'Cook', 10, 'sophia.jpg', 1)
        ]
        c.executemany('''INSERT INTO workers 
                      (name, age, gender, mobile, address, job_title, experience, profile_image, verified)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_workers)
    
    conn.commit()
    conn.close()

# Home page
@app.route('/')
def home():
    return render_template('home.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Dummy validation (replace with database check)
        if username == "testuser" and password == "password123":
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Account creation
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        # Basic validation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('account_creation.html')
        
        # Save to database (simplified)
        try:
            conn = sqlite3.connect('workers.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, email, mobile, password) VALUES (?, ?, ?, ?)",
                     (username, email, mobile, password))
            conn.commit()
            conn.close()
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'error')
    
    return render_template('account_creation.html')

# Forgot password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']
        
        # Basic validation
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('forgot_password.html')
        
        # Update password in database (simplified)
        try:
            conn = sqlite3.connect('workers.db')
            c = conn.cursor()
            c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
            conn.commit()
            conn.close()
            
            flash('Password reset successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Error resetting password.', 'error')
    
    return render_template('forgot_password.html')

# Join as worker
@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        mobile = request.form['mobile']
        address = request.form['address']
        job_title = request.form['job-title']
        experience = request.form['experience']
        
        # Save to database
        try:
            conn = sqlite3.connect('workers.db')
            c = conn.cursor()
            c.execute('''INSERT INTO workers 
                      (name, age, gender, mobile, address, job_title, experience, verified)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (name, age, gender, mobile, address, job_title, experience, 0))
            conn.commit()
            conn.close()
            
            flash('Registration submitted! Your account will be verified soon.', 'success')
            return redirect(url_for('workers'))
        except sqlite3.IntegrityError:
            flash('Mobile number already registered.', 'error')
    
    return render_template('join.html')

# Workers page
@app.route('/workers')
def workers():
    conn = sqlite3.connect('workers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM workers WHERE verified = 1")
    workers = c.fetchall()
    conn.close()
    
    return render_template('workers.html', workers=workers)

# Maids page
@app.route('/maid')
def maid():
    area = request.args.get('area', '')
    search = request.args.get('search', '')
    
    conn = sqlite3.connect('workers.db')
    c = conn.cursor()
    
    if area and search:
        c.execute("SELECT * FROM workers WHERE verified = 1 AND address = ? AND job_title LIKE ?", 
                 (area, f'%{search}%'))
    elif area:
        c.execute("SELECT * FROM workers WHERE verified = 1 AND address = ?", (area,))
    elif search:
        c.execute("SELECT * FROM workers WHERE verified = 1 AND job_title LIKE ?", (f'%{search}%',))
    else:
        c.execute("SELECT * FROM workers WHERE verified = 1")
    
    maids = c.fetchall()
    conn.close()
    
    return render_template('maid.html', maids=maids)

# Maid profile
@app.route('/maid_profile/<int:maid_id>')
def maid_profile(maid_id):
    conn = sqlite3.connect('workers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM workers WHERE id = ?", (maid_id,))
    maid = c.fetchone()
    conn.close()
    
    if maid:
        return render_template('maid_profile.html', maid=maid)
    else:
        flash('Maid not found.', 'error')
        return redirect(url_for('maid'))

# Logout confirmation
@app.route('/logout_confirmation')
def logout_confirmation():
    return render_template('logout.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)