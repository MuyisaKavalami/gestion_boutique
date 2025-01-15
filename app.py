from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from config import Config
import uuid

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'une_cle_secrete_tres_securisee'

# Configuration de MySQL
mysql = MySQL(app)

# Route pour la page d'accueil (index)
@app.route('/')
def index():
    try:
        # Récupérer tous les produits depuis la base de données
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM produits")
        produits = cur.fetchall()
        cur.close()

        # Afficher la page index avec les produits
        return render_template('index.html', produits=produits)
    except Exception as e:
        flash(f"Une erreur s'est produite : {str(e)}", "danger")
        return redirect(url_for('index'))

# Route pour ajouter un produit au panier
@app.route('/ajouter_au_panier/<int:produit_id>', methods=['POST'])
def ajouter_au_panier(produit_id):
    if 'panier_id' not in session:
        session['panier_id'] = str(uuid.uuid4())  # Créer un ID de session unique pour le panier

    quantite = int(request.form['quantite'])

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO panier (produit_id, quantite, session_id) VALUES (%s, %s, %s)", 
                    (produit_id, quantite, session['panier_id']))
        mysql.connection.commit()
        cur.close()
        flash('Produit ajouté au panier avec succès!', 'success')
    except Exception as e:
        flash(f"Erreur lors de l'ajout au panier : {str(e)}", "danger")

    return redirect(url_for('index'))

# Route pour afficher le panier
@app.route('/panier')
def voir_panier():
    if 'panier_id' not in session:
        return redirect(url_for('index'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT p.id, p.nom, p.prix_vente, pan.quantite, (p.prix_vente * pan.quantite) AS total
            FROM panier pan
            JOIN produits p ON pan.produit_id = p.id
            WHERE pan.session_id = %s
        """, (session['panier_id'],))
        panier = cur.fetchall()
        cur.close()

        # Calcul du total du panier
        total_panier = sum(item['total'] for item in panier)

        return render_template('panier.html', panier=panier, total_panier=total_panier)
    except Exception as e:
        flash(f"Erreur lors de la récupération du panier : {str(e)}", "danger")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)