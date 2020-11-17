from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from GMD_PS5 import scrape

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class GMD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = GMD(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        
        except:
            return 'HOUSTON WE HAVE A PROB'
    else:
        tasks = GMD.query.order_by(GMD.date_created).limit(30).all()
        return render_template('index.html', tasks=tasks)

@app.route('/gmd', methods=['GET'])
def getAvailability():
    data = scrape('https://www.amazon.com/PlayStation-5-Console/dp/B08FC5L3RG?ref_=ast_sto_dp')
    dbLength = len(GMD.query.all())

    if dbLength > 120:
        oldestEntry = GMD.query.order_by(GMD.date_created).first()
        try:
            db.session.delete(oldestEntry)
            db.session.commit()
        except:
            return 'There was a problem deleting that task'

    newEntry = GMD(content= data["price"] if data["price"] else "Unavailable")

    try:
        db.session.add(newEntry)
        db.session.commit()
        return redirect('/')
        
    except:
        return 'HOUSTON WE HAVE A PROB'

   

if __name__ == "__ main__":
    app.run(debug=True)