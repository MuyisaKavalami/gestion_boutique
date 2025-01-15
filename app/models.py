from . import db
from datetime import datetime

# Modèle pour les produits
class Produits(db.Model):
    __tablename__ = 'produits'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    prix = db.Column(db.Float, nullable=False)
    prix_achat = db.Column(db.Float, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f"<Produit {self.nom}>"

# Modèle pour les clients
class Clients(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    adresse = db.Column(db.Text, nullable=True)
    date_ajout = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Client {self.nom}>"

# Modèle pour les transactions de produits
class TransactionsProduit(db.Model):
    __tablename__ = 'transactions_produit'
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    type = db.Column(db.Enum('entree', 'sortie'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    date_transaction = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)

    produit = db.relationship('Produits', backref='transactions')

    def __repr__(self):
        return f"<Transaction {self.type} pour le produit {self.produit_id}>"

# Modèle pour les factures
class Factures(db.Model):
    __tablename__ = 'factures'
    id = db.Column(db.Integer, primary_key=True)
    nom_client = db.Column(db.String(100), nullable=False)
    montant_total = db.Column(db.Float, nullable=False)
    date_facture = db.Column(db.DateTime, default=datetime.utcnow)

    ventes = db.relationship('Ventes', backref='facture', lazy=True)

    def __repr__(self):
        return f"<Facture {self.id} pour {self.nom_client}>"

# Modèle pour les ventes
class Ventes(db.Model):
    __tablename__ = 'ventes'
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    facture_id = db.Column(db.Integer, db.ForeignKey('factures.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    montant_total = db.Column(db.Float, nullable=False)

    produit = db.relationship('Produits', backref='ventes')
    benefice = db.relationship('Benefices', backref='vente', uselist=False)

    def __repr__(self):
        return f"<Vente {self.id} pour le produit {self.produit_id}>"

# Modèle pour les bénéfices
class Benefices(db.Model):
    __tablename__ = 'benefices'
    id = db.Column(db.Integer, primary_key=True)
    vente_id = db.Column(db.Integer, db.ForeignKey('ventes.id'), nullable=False)
    montant_benefice = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Bénéfice {self.id} pour la vente {self.vente_id}>"

# Modèle pour le panier
class Panier(db.Model):
    __tablename__ = 'panier'
    id = db.Column(db.Integer, primary_key=True)
    produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix = db.Column(db.Float, nullable=False)  # Assurez-vous que ce champ est présent
    session_id = db.Column(db.String(100), nullable=False)

    produit = db.relationship('Produits', backref='panier')

    def __repr__(self):
        return f"<Panier {self.id} pour le produit {self.produit_id}>"