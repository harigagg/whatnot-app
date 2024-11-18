from . import db


class UserState(db.Model):
    __tablename__ = 'user_state'
    user_id = db.Column(db.String, primary_key=True)
    scam_flags = db.Column(db.Integer, default=0)
    chargeback_cnt = db.Column(db.Integer, default=0)
    chargeback_total = db.Column(db.Float, default=0.0)
    can_message = db.Column(db.Boolean, default=True)
    can_purchase = db.Column(db.Boolean, default=True)

