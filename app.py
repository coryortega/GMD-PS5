from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from GMD_PS5 import scrape
from SMS import send

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///GMD.db'
db = SQLAlchemy(app)

text_alert = "GO GET DAT PLAYSTATION 5 \n\nhttps://www.amazon.com/PlayStation-5-Console/dp/B08FC5L3RG?ref_=ast_sto_dp"

class GMD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Entry %r>' % self.id


@app.route('/', methods=['GET'])
def index():
    entries = GMD.query.order_by(GMD.date_created).limit(30).all()
    return render_template('index.html', entries=entries)


@app.route('/gmd', methods=['GET'])
def getAvailability():
    data = scrape('https://www.amazon.com/PlayStation-5-Console/dp/B08FC5L3RG?ref_=ast_sto_dp')
    dbLength = len(GMD.query.all())

    if dbLength == 0:
        newEntry = GMD(content= data["price"] if data["price"] else "Unavailable")
        try:
            db.session.add(newEntry)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem adding that entry'

    else:
        if dbLength > 120:
            oldestEntry = GMD.query.order_by(GMD.date_created).first()
            try:
                db.session.delete(oldestEntry)
                db.session.commit()
            except:
                return 'There was a problem deleting that entry'

        lastEntry = GMD.query.order_by(GMD.date_created.desc()).first()
        if lastEntry.content == 'Unavailable' and data["price"]:
            send(text_alert)

        newEntry = GMD(content= data["price"] if data["price"] else "Unavailable")
        try:
            db.session.add(newEntry)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem adding that entry'


if __name__ == "__ main__":
    app.run(debug=True)