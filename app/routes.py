
# app/routes.py

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import Voter, Nominee, Votes, Admin
from . import db, bcrypt

def init_routes(app):
    @app.route('/')
    def welcome():
        return render_template('welcome.html')

    @app.route('/instruction')
    def instruction():
        return render_template('instruction.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = Voter.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('voter_dashboard'))
            else:
                flash('Invalid login credentials', 'danger')
        return render_template('login.html')

    @app.route('/admin_login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            admin = Admin.query.filter_by(username=username).first()  # Ensure you use 'Admin' not 'admin'
            if admin and check_password_hash(admin.password, password):
                login_user(admin)
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        return render_template('admin_login.html')

    @app.route('/admin_dashboard')
    @login_required
    def admin_dashboard():
        return render_template('admin_dashboard.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            mobile = request.form['mobile']
            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            new_voter = Voter(name=name, email=email, mobile=mobile, password=password)
            db.session.add(new_voter)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/vote', methods=['GET', 'POST'])
    @login_required
    def vote():
        if request.method == 'POST':
            nominee_id = request.form['nominee_id']
            existing_vote = Votes.query.filter_by(voter_id=current_user.id).first()
            if existing_vote:
                flash('You have already voted!', 'danger')
                return redirect(url_for('voter_dashboard'))
            new_vote = Votes(voter_id=current_user.id, nominee_id=nominee_id)
            db.session.add(new_vote)
            db.session.commit()
            flash('Your vote has been cast successfully!', 'success')
            return redirect(url_for('voter_dashboard'))
        nominees = Nominee.query.all()
        return render_template('vote.html', nominees=nominees)

    @app.route('/results')
    def results():
        from sqlalchemy.sql import func
        vote_counts = (
            db.session.query(
                Nominee.id, Nominee.name, Nominee.party, Nominee.symbol,
                func.count(Votes.id).label("vote_count")
            )
            .outerjoin(Votes, Nominee.id == Votes.nominee_id)
            .group_by(Nominee.id)
            .all()
        )
        if not vote_counts:
            return render_template("results.html", message="Results will be declared after elections.")
        winner = max(vote_counts, key=lambda x: x.vote_count)
        return render_template("results.html", vote_counts=vote_counts, winner=winner)

    @app.route('/candidate')
    def candidate():
        nominees = Nominee.query.all()
        if not nominees:
            return render_template("candidate.html", message="No nominees registered yet.")
        return render_template("candidate.html", nominees=nominees)

    @app.route('/nominee', methods=['GET', 'POST'])
    @login_required
    def nominee():
        if request.method == 'POST':
            name = request.form['name']
            party = request.form['party']
            symbol = request.form['symbol']
            new_nominee = Nominee(name=name, party=party, symbol=symbol)
            db.session.add(new_nominee)
            db.session.commit()
            flash('Nominee registered successfully!', 'success')
            return redirect(url_for('candidate'))
        return render_template('nominee.html')

    @app.route('/voter_dashboard')
    @login_required
    def voter_dashboard():
        return render_template("voter_dashboard.html", user=current_user)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
