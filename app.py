from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import string
import random

app = Flask(__name__)




# Database Path Setup

base_dir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(base_dir, "instance")



# If the instance folder does not exist create it
os.makedirs(instance_dir, exist_ok=True)

db_path = os.path.join(instance_dir, "database.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



# Database Models

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), nullable=False, unique=True)
    clicks = db.Column(db.Integer, default=0)

class ClickDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

with app.app_context():
    db.create_all()




# Short Code Generator

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))






@app.route('/api/click/<short_code>', methods=['POST'])
def click_update(short_code):
    link = Link.query.filter_by(short_url=short_code).first()
    if not link:
        return jsonify({"error": "Short URL not found"}), 404

    # Click sayısını arttır
    link.clicks += 1
    db.session.commit()
    return jsonify({"clicks": link.clicks})







# API – Analytics

@app.route('/api/analytics', methods=['GET'])
def analytics():
    links = Link.query.all()
    data = [
        {
            "short_url": l.short_url,
            "original_url": l.original_url,
            "clicks": l.clicks
        } for l in links
    ]
    return jsonify(data)




# API – Create Short URL

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get("original_url")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    # check if already exists
    existing = Link.query.filter_by(original_url=original_url).first()
    if existing:
        return jsonify({"short_url": existing.short_url})

    # create unique short code
    short_code = generate_short_code()

    new_link = Link(original_url=original_url, short_url=short_code)
    db.session.add(new_link)
    db.session.commit()

    return jsonify({"short_url": short_code})




# Redirect Short URL

@app.route('/<short_code>')
def redirect_to_original(short_code):
    link = Link.query.filter_by(short_url=short_code).first()
    if not link:
        return "Short URL not found", 404

    # count click
    link.clicks += 1
    db.session.commit()

    # store click details
    click = ClickDetail(
        link_id=link.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(click)
    db.session.commit()

    return redirect(link.original_url)





# Frontend Route

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
