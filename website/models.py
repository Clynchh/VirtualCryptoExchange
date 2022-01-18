from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))
    #relationship_name = db.relationship('')


class Portfolio(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    
#todo:
#add rankings page comparing all users' scores (ROI) - will make it from a sim to a multiplayer game - access higher marks
#efficiency is not as important - can be used in evaluations
#easy to refresh a webpage contantly display real time data contantly
#make portfolio page with asset distribution and ROI from different 
#add feature where all users can play on an even playing field for ~2 weeks or so - compare player ROI throughtout the same time scale
#scrap bot?
#migrate database to sqlite not sqlalchemy - to show understanding of sql