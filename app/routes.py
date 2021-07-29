from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EpisodeForm, EditEpisodeForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Episode
from datetime import datetime

# With every request, update the current user's last seen on app time
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Root Route
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='home')


#########################################################################
#  USER REGISTRATION/LOGIN/LOGOUT amd WRITERS
#########################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # if not authenticated, begin login process
    form = LoginForm()
    # does the form data meet requirements?
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # Did we load a valid username? if so, did password entered match?
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            # if not, return to login again
            return redirect(url_for('login'))
        # if login succeeds, redirect to index
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    # render login form
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    # built in function from flask_login
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # if user is not authenticated, begin registration process 
    form = RegistrationForm()
    # if form is filled and passes validation... process data.
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    # if form is not yet filled out (or an error in its data), render form
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<string:username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    episodes = user.episodes
    return render_template('user.html', user=user, episodes=episodes)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.about_me = form.about_me.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        return render_template('edit_profile.html', title='Edit Profile', form=form)
    return redirect(url_for('index'))

@app.route('/writers')
def writers():
    writers = []
    episodes = Episode.query.all()
    for episode in episodes:
        if episode.writer not in writers:
            writers.append(episode.writer)

    return render_template('writers.html', title='writers', writers=writers)

#########################################################################
#  EPISODES
#########################################################################
@app.route('/episodes/', methods=['GET', 'POST'])
def episodes():
    form = EpisodeForm()
    if form.validate_on_submit():
        episode = Episode(title=form.title.data, plot=form.plot.data, writer=current_user)
        db.session.add(episode)
        db.session.commit()
        flash('Your episode has been added!')
        return redirect(url_for('episodes'))
    episodes = Episode.query.order_by(Episode.timestamp.desc()).all()
    return render_template('episodes.html', title='Episodes', form=form, episodes=episodes)
    
@app.route('/edit_episode/<int:id>/', methods=['GET', 'POST'])
def edit_episode(id):
    episode = Episode.query.get(id)
    form = EditEpisodeForm()
    if form.validate_on_submit():
        episode.title = form.title.data
        episode.plot = form.plot.data
        db.session.commit()  
        return redirect(url_for('episodes'))
    if request.method == 'GET':
        form.title.data = episode.title
        form.plot.data = episode.plot
    return render_template('edit_episode.html', form=form)
  

@app.route('/episodes/<int:id>/delete')
def delete_episode(id):
    episode = Episode.query.filter_by(id=id).first()
    db.session.delete(episode)
    db.session.commit()
    return redirect(url_for('episodes'))
    


