from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import math
from werkzeug.utils import secure_filename

with open('config-youtube.json', 'r') as c:
    params = json.load(c)["params"]
local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Videos(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    category = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=False)
    duration = db.Column(db.String(12), unique=False, nullable=False)
    slug = db.Column(db.String(21), unique=True, nullable=False)
    img_file = db.Column(db.String(12), unique=True, nullable=False)
    video_file = db.Column(db.String(1000), unique=True, nullable=False)
    description = db.Column(db.String(80), unique=False, nullable=False)


@app.route('/')
def home():
    videos = Videos.query.filter_by().all()
    last = math.ceil(len(videos)/int(params['no-of-videos']))
    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    videos = videos[(page-1)*int(params['no-of-videos']): (page-1)*int(params['no-of-videos'])+int(params['no-of-videos'])]

    if page == 1:
        prev = "#"
        next = "/?page="+str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', params=params, videos=videos, prev=prev, next=next)


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if 'user' in session and session['user'] == params['admin-user']:
        videos = Videos.query.all()
        return render_template('dashboard.html', params=params, videos=videos, video=video)

    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pass')
        if username == params['admin-user'] and password == params['admin-password']:
            session['user'] = username
            videos = Videos.query.all()
            return render_template('dashboard.html', params=params, videos=videos)

    return render_template('login.html', params=params)


@app.route('/edit/<string:sno>', methods=["GET", "POST"])
def edit(sno):
    if 'user' in session and session['user'] == params['admin-user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            category = request.form.get('category')
            date = datetime.now()
            duration = request.form.get('duration')
            slug = request.form.get('slug')
            img_file = request.form.get('img_file')
            video_file = request.form.get('video_file')
            description = request.form.get('description')

            if sno == '0':
                video = Videos(title=box_title, category=category, date=date, duration=duration, slug=slug, img_file=img_file, video_file=video_file, description=description)
                db.session.add(video)
                db.session.commit()
            else:
                video = Videos.query.filter_by(sno=sno).first()
                video.title = box_title
                video.category = category
                video.date = date
                video.duration = duration
                video.slug = slug
                video.img_file = img_file
                video.video_file = video_file
                video.description = description
                db.session.commit()
                return redirect('/edit/' + sno)
        video = Videos.query.filter_by(sno=sno).first()

        return render_template('edit.html', params=params, video=video, sno=sno)


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/delete/<string:sno>', methods=["GET", "POST"])
def delete(sno):
    if 'user' in session and session['user'] == params['admin-user']:
        video = Videos.query.filter_by(sno=sno).first()
        db.session.delete(video)
        db.session.commit()

    return redirect('/dashboard')


@app.route('/video/<string:video_slug>', methods=["GET", "POST"])
def video(video_slug):
    video = Videos.query.filter_by(slug=video_slug).first()
    videos = Videos.query.filter_by()[0:params['no-of-videos2']]

    return render_template('video-page.html', params=params, video=video, videos=videos)


app.run(debug=True)