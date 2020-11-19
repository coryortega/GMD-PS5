from flask import Flask, render_template, url_for, request, redirect
import os
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from GMD_PS5 import scrape
from SMS import send
from dotenv import load_dotenv, find_dotenv
from enum import Enum

load_dotenv(find_dotenv())

DATABASE_URL = os.environ.get("DATABASE_URL")

# conn = psycopg2.connect(DATABASE_URL, sslmode='require')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ekkuyeeowmyaib' \
                                        ':495d4077d510e88a1cadaedd6aec945989aa928bbb379662fd8fa2b130c55976@ec2-75-101' \
                                        '-232-85.compute-1.amazonaws.com:5432/dcjiuhl8ok8e14 '
db = SQLAlchemy(app)


# Edit enum
class Edit(Enum):
    initialize = 0
    delete = 1
    add = 2


# DB Model Setup
class GMD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Entry %r>' % self.id


from model import GMD


# Flask Routes
@app.route('/', methods=['GET'])
def index():
    entries = GMD.query.order_by(GMD.date_created).limit(30).all()
    return render_template('index.html', entries=entries)


@app.route('/gmd', methods=['GET'])
def get_availability():
    data = scrape('https://www.amazon.com/PlayStation-5-Console/dp/B08FC5L3RG?ref_=ast_sto_dp')
    dbLength = len(GMD.query.all())

    if dbLength == 0:
        return edit_db(Edit.initialize, data)

    else:
        if dbLength > 120:
            error_message = edit_db(Edit.delete, data)
            if error_message is not None:
                return error_message

        return edit_db(Edit.add, data)


# DB Helper Function 
def edit_db(type_of_edit, scrape_data):
    # Initializing DB
    if type_of_edit == Edit.initialize:
        newEntry = GMD(content=scrape_data["price"] if scrape_data["price"] else "Unavailable")
        try:
            db.session.add(newEntry)
            db.session.commit()
            return redirect('/')
        finally:
            return 'There was a problem adding that entry'

    # Deleting if size of DB exceeds 120
    if type_of_edit == Edit.delete:
        oldestEntry = GMD.query.order_by(GMD.date_created).first()
        try:
            db.session.delete(oldestEntry)
            db.session.commit()
        finally:
            return 'There was a problem deleting that entry'
    
    # Adding to DB
    if type_of_edit == Edit.add:
        lastEntry = GMD.query.order_by(GMD.date_created.desc()).first()
        if lastEntry.content == 'Unavailable' and scrape_data["price"]:
            text_alert = "GO GET DAT PLAYSTATION 5 \n\nhttps://www.amazon.com/" \
                         "PlayStation-5-Console/dp/B08FC5L3RG?ref_=ast_sto_dp"
            send(text_alert)

        newEntry = GMD(content=scrape_data["price"] if scrape_data["price"] else "Unavailable")
        try:
            db.session.add(newEntry)
            db.session.commit()
            return redirect('/')
        finally:
            return 'There was a problem adding that entry'


if __name__ == "__ main__":
    app.run()
