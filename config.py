import os

class Config:
    SECRET_KEY = '**************************************'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///moonphase.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False