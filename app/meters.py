import os

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
db_file = 'sqlite:///{}'.format(os.path.join(project_dir, 'meters.db'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_file

db = SQLAlchemy(app)


class Meter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(140), nullable=False)
    data = db.relationship('MeterData', backref='meter', lazy=True)


def serialize_datetime(date):
    if date is None:
        return None
    return [date.strftime('%Y-%m-%d'), date.strftime('%H:%M:%S')]


class MeterData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.Integer, db.ForeignKey('meter.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=True)
    value = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'meter_id': self.meter_id,
            'timestamp': serialize_datetime(self.timestamp),
            'value': self.value
        }


@app.route('/')
def render_homepage():
    return render_template('index.html')


@app.route('/meters')
def render_meters_list():
    meters = Meter.query.all()
    return render_template('meters_list.html', meters=meters)


@app.route('/meters/<int:meter_id>', methods=['GET'])
def render_meter_data(meter_id):
    query_results = MeterData.query.filter_by(
        meter_id=meter_id).order_by(MeterData.timestamp.desc()).all()
    result_list = [i.serialize() for i in query_results]
    return jsonify(result_list)


app.run(debug=True)
