from flask import Flask, jsonify, request, render_template, redirect, url_for, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'root'

# Função para obter uma conexão com o banco de dados
def get_db_connection():
    conn = sqlite3.connect('pi.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def nutricao():
    return 'Nutrição saudável'

# Login do usuário
@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg = 'SYSTEM WITH ERROR'
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        name = request.form['name']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE name = ? AND password = ?', (name, password,))
        account = cursor.fetchone()
        conn.close()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

# Logout do usuário
@app.route('/login/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

# Registro de usuário
@app.route('/login/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO users (name, password, email) VALUES (?, ?, ?)', (name, password, email,))
            conn.commit()
            msg = 'You have successfully registered!'
        conn.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

# Tela inicial do usuário logado
@app.route('/login/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', name=session['name'])
    return redirect(url_for('login'))

# Perfil
@app.route('/login/profile')
def profile():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['id'],))
        account = cursor.fetchone()
        conn.close()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

# Diário alimentar
@app.route('/diary', methods=['GET'])
def get_diary():
    conn = get_db_connection()
    diary = conn.execute('SELECT * FROM diary').fetchall()
    conn.close()
    return jsonify([dict(row) for row in diary])

@app.route('/diary/<int:id>', methods=['GET'])
def get_diary_by_id(id):
    conn = get_db_connection()
    diary = conn.execute('SELECT * FROM diary WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(diary))

@app.route('/diary_new_meal', methods=['POST'])
def add_diary():
    title = request.json['title']
    description = request.json['description']
    date = request.json['date']
    time = request.json['time']
    is_in_diet = request.json['is_in_diet']
    conn = get_db_connection()
    conn.execute('INSERT INTO diary (title, description, date, time, is_in_diet) VALUES (?, ?, ?, ?, ?)', 
                 (title, description, date, time, is_in_diet))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Diary added successfully'})

@app.route('/diary/<int:id>', methods=['PUT'])
def update_diary(id):
    title = request.json['title']
    description = request.json['description']
    date = request.json['date']
    time = request.json['time']
    is_in_diet = request.json['is_in_diet']
    conn = get_db_connection()
    conn.execute('UPDATE diary SET title = ?, description = ?, date = ?, time = ?, is_in_diet = ? WHERE id = ?', 
                 (title, description, date, time, is_in_diet, id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Diary updated successfully'})

@app.route('/diary/<int:id>', methods=['DELETE'])
def delete_diary(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM diary WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Diary deleted successfully'})

# Plano alimentar
@app.route('/meal_plan', methods=['GET'])
def get_meal_plan():
    conn = get_db_connection()
    meal_plan = conn.execute('SELECT * FROM meal_plan').fetchall()
    conn.close()
    return jsonify([dict(row) for row in meal_plan])

@app.route('/meal_plan/<int:id>', methods=['GET'])
def get_meal_plan_by_id(id):
    conn = get_db_connection()
    meal_plan = conn.execute('SELECT * FROM meal_plan WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(meal_plan))

@app.route('/meal_plan', methods=['POST'])
def add_meal_plan():
    title = request.json['title']
    quantity = request.json['quantity']
    meal = request.json['meal']
    conn = get_db_connection()
    conn.execute('INSERT INTO meal_plan (title, quantity, meal) VALUES (?, ?, ?)', 
                 (title, quantity, meal))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Meal added successfully'})

@app.route('/meal_plan/<int:id>', methods=['PUT'])
def update_meal_plan(id):
    title = request.json['title']
    quantity = request.json['quantity']
    meal = request.json['meal']
    conn = get_db_connection()
    conn.execute('UPDATE meal_plan SET title = ?, quantity = ?, meal = ? WHERE id = ?', 
                 (title, quantity, meal, id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Meal plan updated successfully'})

@app.route('/meal_plan/<int:id>', methods=['DELETE'])
def delete_meal_plan(id):
    conn = get_db_connection()
