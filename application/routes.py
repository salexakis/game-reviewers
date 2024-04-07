from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, current_user, logout_user, login_required
from application.forms import SignupForm, LoginForm, NewGameForm, AccountUpdateForm
from application.models import User, Game
from application import app, db, bcrypt
from werkzeug.utils import secure_filename
from datetime import datetime as dt
from PIL import Image
import secrets
import os

current_year = dt.now().year

# Function for renaming and saving user profile pictures
def image_save(image, where, size):
  random_filename = secrets.token_hex(8)
  file_name, file_extension = os.path.splitext(image.filename)
  image_filename = random_filename + file_extension
  image_path = os.path.join(app.root_path, 'static/images/'+ where, image_filename)
  image_size = size
  img = Image.open(image)
  img.thumbnail(image_size)
  img.save(image_path)
  return image_filename


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html"), 404


@app.errorhandler(415)
def unsupported_media_type(e):
  return render_template("415.html"), 415


@app.errorhandler(500)
def internal_server_error(e):
  return render_template("500.html"), 500



@app.route("/")
def home():

  ## Pagination: page value from 'page' parameter from url
  page = request.args.get('page', 1, type=int)

  if request.args.get('ordering_by') == 'rating':
      games = Game.query.order_by(Game.rating.desc()).paginate(per_page=5, page=page)
  else:
      games = Game.query.order_by(Game.review_date.desc()).paginate(per_page=5, page=page)
  return render_template("index.html", games=games)



@app.route("/signup/", methods=['GET','POST'])
def signup():

  if current_user.is_authenticated:
    return redirect(url_for("home"))

  form = SignupForm()

  if request.method == 'POST' and form.validate_on_submit():
    username = form.username.data
    email = form.email.data
    password = form.password.data
    password2 = form.password2.data

    encrypted_password = bcrypt.generate_password_hash(password).decode('UTF-8')

    user = User(username=username, email=email, password=encrypted_password)
    db.session.add(user)
    db.session.commit()

    flash(f'The account for user: <b>{username}</b> created successfully', 'success')

    return redirect(url_for('login_page'))

  return render_template("signup.html", form=form)



@app.route("/account/", methods=['GET','POST'])
@login_required
def account():

  # Initializing form with prefilled user data
  form = AccountUpdateForm(username=current_user.username, email=current_user.email)

  if request.method == 'POST' and form.validate_on_submit():

    # Check if new profile image has been added
    if form.profile_image.data:
        # Change image resolution
        try:
            image_file = image_save(form.profile_image.data, 'profiles_images', (150, 150))
        except:
            abort(415)
        # Saving new image in to database
        current_user.profile_image = image_file

    db.session.commit()

    # Save the rest data of user
    current_user.username = form.username.data
    current_user.email = form.email.data

    flash(f'The account of user: <b>{current_user.username}</b> has been successfully updated', 'success')

    return redirect(url_for('home'))
  else:
      return render_template("account_update.html", form=form)



@app.route("/login/", methods=['GET','POST'])
def login_page():

  if current_user.is_authenticated:
    return redirect(url_for("home"))

  form = LoginForm()

  if request.method == 'POST' and form.validate_on_submit():
    email = form.email.data
    password = form.password.data
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
      flash(f"The user with email: {email} has successfully logged in.", "success")
      login_user(user, remember=form.remember_me.data)
      next_link = request.args.get("next")
      return redirect(next_link) if next_link else redirect(url_for("home")) #Check again
    else:
      flash("Sign in was unsuccessfull, please check your username/password and try again.", "warning")
  return render_template("login.html", form=form)


@app.route("/logout/")
def logout_page():
  logout_user()
  flash('User sign out successfully.', 'success')
  return redirect(url_for("home"))


@app.route("/new_game/", methods=["GET", "POST"])
@login_required
def new_game():
  form = NewGameForm()
  if request.method == 'POST' and form.validate_on_submit():
    title = form.title.data
    review = form.review.data
    image = form.image.data
    rating = form.rating.data

    if form.image.data:
        try:
            image = image_save(form.image.data, 'games_images', (640, 640))
        except:
            abort(415)

        game = Game(title=title,
                    review=review,
                    image=image,
                    rating=rating,
                    user_id=current_user.id)
    else:
      game = Game(title=title, review=review, rating=rating, user_id=current_user.id)

    db.session.add(game)
    db.session.commit()
    flash(f'Review for game: "{title}" has been successfully created', 'success')
    return redirect(url_for('home'))
  return render_template("new_game.html", form=form, page_title="Add Game Review")



@app.route("/game/<int:game_id>", methods=["GET"])
def game(game_id):
  game = Game.query.get_or_404(game_id)
  return render_template("game.html", game=game)



@app.route("/games_by_reviewer/<int:reviewer_id>")
def games_by_reviewer(reviewer_id):
  ## Pagination: page value from 'page' parameter from url
  page = request.args.get('page', 1, type=int)

  # Query user from database using user id('reviewer_id'), ή or show 404 page if not found
  user = User.query.get_or_404(reviewer_id)

  ## Query games from database based on user with the correct pagination and sorting
  if request.args.get('ordering_by') == 'rating':
      games = Game.query.filter_by(reviewer=user).order_by(Game.rating.desc()).paginate(per_page=5, page=page)
  else:
      games = Game.query.filter_by(reviewer=user).order_by(Game.review_date.desc()).paginate(per_page=5, page=page)
  return render_template("games_by_reviewer.html", games=games, reviewer=user)


@app.route("/edit_game/<int:game_id>", methods=["GET", "POST"])
@login_required
def edit_game(game_id):
  game = Game.query.filter_by(id=game_id, reviewer=current_user).first_or_404()
  if game:
    form = NewGameForm(title=game.title, review=game.review)    

    if request.method == 'POST' and form.validate_on_submit():
      game.title = form.title.data
      game.review = form.review.data
      game.rating = form.rating.data

      if form.image.data:
        try:
          image_file = image_save(form.image.data, 'games_images', (640, 640))
        except:
          abort(415)
        games.image = image_file

      db.session.commit()
      flash(f'Game review has been successfully updated', 'success')
      return redirect(url_for('game', game_id=game.id))
    return render_template("new_game.html", form=form, game=game, page_title="Edit Review")
  else:
    flash(f'No review found', 'info')
    return redirect(url_for("home"))


@app.route("/delete_game/<int:game_id>", methods=["GET", "POST"])
@login_required
def delete_game(game_id):
  game = Game.query.filter_by(id=game_id, reviewer=current_user).first_or_404()
  if game:
    db.session.delete(game)
    db.session.commit()
    flash("Review has been successfully deleted.", "success")
    return redirect(url_for("home"))

  flash("Review not found.", "warning")
  return redirect(url_for("home"))