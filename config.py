import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une_cle_secrete_tres_securisee'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'boutique_db'