from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from .models import db, Produits, Factures, Ventes, Benefices, Panier, TransactionsProduit, Clients, Depenses,TransactionDepot
from datetime import datetime
import uuid

# Création du Blueprint
bp = Blueprint('routes', __name__)

# Route pour la page d'accueil
@bp.route('/')
def index():
    total_produits = Produits.query.count()
    total_clients = Clients.query.count()
    transactions = TransactionsProduit.query.order_by(TransactionsProduit.date_transaction.desc()).limit(5).all()
    return render_template('index.html', total_produits=total_produits, total_clients=total_clients, transactions=transactions)

# Route pour gérer les produits
@bp.route('/gestion_produits')
def gestion_produits():
    produits = Produits.query.all()
    return render_template('gestion_produits.html', produits=produits)

# Route pour ajouter un produit
@bp.route('/ajouter_produit', methods=['POST'])
def ajouter_produit():
    try:
        nom = request.form['nom']
        description = request.form['description']
        prix = float(request.form['prix'])
        prix_achat = float(request.form['prix_achat'])
        quantite = int(request.form['quantite'])

        produit_existant = Produits.query.filter_by(nom=nom).first()
        if produit_existant:
            flash("Le produit existe déjà!", "danger")
            return redirect(url_for('routes.gestion_produits'))

        nouveau_produit = Produits(
            nom=nom,
            description=description,
            prix=prix,
            prix_achat=prix_achat,
            quantite=quantite
        )
        db.session.add(nouveau_produit)
        db.session.commit()
        flash("Produit ajouté avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'ajout du produit: {e}", "danger")
    return redirect(url_for('routes.gestion_produits'))

# Route pour modifier un produit
@bp.route('/modifier_produit/<int:id>', methods=['POST'])
def modifier_produit(id):
    produit = Produits.query.get_or_404(id)
    try:
        produit.nom = request.form['nom']
        produit.description = request.form['description']
        produit.prix = float(request.form['prix'])
        produit.prix_achat = float(request.form['prix_achat'])
        produit.quantite = int(request.form['quantite'])
        db.session.commit()
        flash("Produit modifié avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la modification du produit: {e}", "danger")
    return redirect(url_for('routes.gestion_produits'))

# Route pour supprimer un produit
@bp.route('/supprimer_produit', methods=['POST'])
def supprimer_produit():
    id = request.form['idDel']
    produit = Produits.query.get_or_404(id)
    try:
        db.session.delete(produit)
        db.session.commit()
        flash("Produit supprimé avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression du produit: {e}", "danger")
    return redirect(url_for('routes.gestion_produits'))

# Route pour afficher les entrées et sorties des produits
@bp.route('/entrees_sorties')
def entrees_sorties():
    transactions = TransactionsProduit.query.order_by(TransactionsProduit.date_transaction.desc()).all()
    produits = Produits.query.all()
    return render_template('entrees_sorties.html', transactions=transactions, produits=produits)

# Route pour ajouter une transaction (entrée ou sortie)
@bp.route('/ajouter_transaction', methods=['POST'])
def ajouter_transaction():
    try:
        produit_id = int(request.form['produit_id'])
        type_transaction = request.form['type']
        quantite = int(request.form['quantite'])
        description = request.form.get('description', '')

        produit = Produits.query.get_or_404(produit_id)

        if type_transaction == 'entree':
            produit.quantite += quantite
        elif type_transaction == 'sortie':
            if produit.quantite < quantite:
                flash("Quantité insuffisante en stock!", "danger")
                return redirect(url_for('routes.entrees_sorties'))
            produit.quantite -= quantite
        else:
            flash("Type de transaction invalide!", "danger")
            return redirect(url_for('routes.entrees_sorties'))

        nouvelle_transaction = TransactionsProduit(
            produit_id=produit_id,
            type=type_transaction,
            quantite=quantite,
            description=description
        )
        db.session.add(nouvelle_transaction)
        db.session.commit()
        flash("Transaction ajoutée avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'ajout de la transaction: {e}", "danger")
    return redirect(url_for('routes.entrees_sorties'))

# Route pour afficher et rechercher les factures
@bp.route('/factures', methods=['GET'])
def factures():
    search_term = request.args.get('search', '')
    if search_term:
        factures = Factures.query.filter(Factures.nom_client.ilike(f'%{search_term}%')).order_by(Factures.date_facture.desc()).all()
    else:
        factures = Factures.query.order_by(Factures.date_facture.desc()).all()
    return render_template('factures.html', factures=factures, search_term=search_term)

# Route pour afficher les détails d'une facture
@bp.route('/factures/<int:id>', methods=['GET'])
def details_facture(id):
    facture = Factures.query.get_or_404(id)
    ventes = Ventes.query.filter_by(facture_id=id).all()
    return render_template('details_facture.html', facture=facture, ventes=ventes)

# Route pour gérer les ventes
@bp.route('/ventes', methods=['GET', 'POST'])
def ventes():
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        response = make_response(redirect(url_for('routes.ventes')))
        response.set_cookie('session_id', session_id)
        return response

    if request.method == 'POST':
        if 'ajouter_au_panier' in request.form:
            try:
                produit_id = int(request.form['produit_id'])
                quantite = int(request.form['quantite'])
                prix = float(request.form['prix'])

                if quantite <= 0 or prix <= 0:
                    flash("La quantité et le prix doivent être des nombres positifs.", "danger")
                    return redirect(url_for('routes.ventes'))

                produit = Produits.query.get_or_404(produit_id)

                if produit.quantite < quantite:
                    flash("Quantité insuffisante en stock!", "danger")
                    return redirect(url_for('routes.ventes'))

                item_panier = Panier.query.filter_by(produit_id=produit_id, session_id=session_id).first()
                if item_panier:
                    flash("Ce produit est déjà dans le panier. Supprimez-le avant de l'ajouter à nouveau.", "warning")
                    return redirect(url_for('routes.ventes'))
                else:
                    nouveau_panier = Panier(
                        produit_id=produit_id,
                        quantite=quantite,
                        prix=prix,
                        session_id=session_id
                    )
                    db.session.add(nouveau_panier)

                db.session.commit()
                flash("Produit ajouté au panier avec succès!", "success")
                return redirect(url_for('routes.ventes'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erreur lors de l'ajout au panier: {e}", "danger")
                return redirect(url_for('routes.ventes'))

        elif 'supprimer_du_panier' in request.form:
            try:
                panier_id = int(request.form['panier_id'])
                item_panier = Panier.query.get_or_404(panier_id)
                db.session.delete(item_panier)
                db.session.commit()
                flash("Produit supprimé du panier avec succès!", "success")
                return redirect(url_for('routes.ventes'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erreur lors de la suppression du produit: {e}", "danger")
                return redirect(url_for('routes.ventes'))

        elif 'vider_panier' in request.form:
            try:
                Panier.query.filter_by(session_id=session_id).delete()
                db.session.commit()
                flash("Panier vidé avec succès!", "success")
                return redirect(url_for('routes.ventes'))
            except Exception as e:
                db.session.rollback()
                flash(f"Erreur lors du vidage du panier: {e}", "danger")
                return redirect(url_for('routes.ventes'))

        elif 'finaliser_vente' in request.form:
            try:
                nom_client = request.form['nom_client']

                if not nom_client.strip():
                    flash("Le nom du client ne peut pas être vide.", "danger")
                    return redirect(url_for('routes.ventes'))

                panier = Panier.query.filter_by(session_id=session_id).all()

                if not panier:
                    flash("Votre panier est vide!", "danger")
                    return redirect(url_for('routes.ventes'))

                montant_total = sum(item.prix * item.quantite for item in panier)

                nouvelle_facture = Factures(
                    nom_client=nom_client,
                    montant_total=montant_total
                )
                db.session.add(nouvelle_facture)
                db.session.flush()

                ventes = []
                for item in panier:
                    produit = item.produit

                    if produit.quantite < item.quantite:
                        flash(f"Quantité insuffisante pour le produit {produit.nom}!", "danger")
                        return redirect(url_for('routes.ventes'))

                    nouvelle_vente = Ventes(
                        produit_id=produit.id,
                        facture_id=nouvelle_facture.id,
                        quantite=item.quantite,
                        montant_total=item.prix * item.quantite
                    )
                    db.session.add(nouvelle_vente)
                    db.session.flush()

                    benefice = (item.prix - produit.prix_achat) * item.quantite
                    nouveau_benefice = Benefices(
                        vente_id=nouvelle_vente.id,
                        montant_benefice=benefice
                    )
                    db.session.add(nouveau_benefice)

                    produit.quantite -= item.quantite
                    ventes.append(nouvelle_vente)

                Panier.query.filter_by(session_id=session_id).delete()
                db.session.commit()

                flash("Vente finalisée avec succès!", "success")
                return render_template('ventes.html', produits=Produits.query.all(), panier=[], total=0, facture=nouvelle_facture, ventes=ventes)
            except Exception as e:
                db.session.rollback()
                Panier.query.filter_by(session_id=session_id).delete()
                db.session.commit()
                flash(f"Erreur lors de la finalisation de la vente: {e}", "danger")
                return redirect(url_for('routes.ventes'))

    produits = Produits.query.all()
    panier = Panier.query.filter_by(session_id=session_id).all()
    total = sum(item.prix * item.quantite for item in panier)

    return render_template('ventes.html', produits=produits, panier=panier, total=total, facture=None, ventes=[])

# Route pour imprimer une facture
@bp.route('/factures/<int:id>/imprimer', methods=['GET'])
def imprimer_facture(id):
    facture = Factures.query.get_or_404(id)
    ventes = Ventes.query.filter_by(facture_id=id).all()
    return render_template('imprimer_facture.html', facture=facture, ventes=ventes)

# Route pour afficher l'historique des ventes
@bp.route('/historique_ventes')
def historique_ventes():
    ventes = Ventes.query.join(Factures).order_by(Factures.date_facture.asc()).all()
    return render_template('historique_ventes.html', ventes=ventes)

# Route pour afficher la liste des dépenses ordinaires
@bp.route('/depenses_ordinaires')
def gestion_depenses_ordinaires():
    depenses_ordinaires = Depenses.query.filter_by(est_recurrente=False).order_by(Depenses.date_depense.desc()).all()
    return render_template('gestion_depenses_ordinaires.html', depenses=depenses_ordinaires)

# Route pour afficher la liste des dépenses récurrentes
@bp.route('/depenses_recurrentes')
def gestion_depenses_recurrentes():
    depenses_recurrentes = Depenses.query.filter_by(est_recurrente=True).order_by(Depenses.date_depense.desc()).all()
    return render_template('gestion_depenses_recurrentes.html', depenses=depenses_recurrentes)

# Route pour ajouter une dépense
@bp.route('/ajouter_depense', methods=['POST'])
def ajouter_depense():
    try:
        description = request.form['description']
        montant = float(request.form['montant'])
        categorie = request.form.get('categorie', '')
        est_recurrente = 'est_recurrente' in request.form  # Vérifie si la case est cochée
        frequence_recurrence = request.form.get('frequence_recurrence', None) if est_recurrente else None

        nouvelle_depense = Depenses(
            description=description,
            montant=montant,
            categorie=categorie,
            est_recurrente=est_recurrente,
            frequence_recurrence=frequence_recurrence
        )
        db.session.add(nouvelle_depense)
        db.session.commit()
        flash("Dépense ajoutée avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'ajout de la dépense: {e}", "danger")
    return redirect(url_for('routes.gestion_depenses_ordinaires'))

# Route pour modifier une dépense
@bp.route('/modifier_depense/<int:id>', methods=['POST'])
def modifier_depense(id):
    depense = Depenses.query.get_or_404(id)
    try:
        depense.description = request.form['description']
        depense.montant = float(request.form['montant'])
        depense.categorie = request.form.get('categorie', '')
        depense.est_recurrente = 'est_recurrente' in request.form
        depense.frequence_recurrence = request.form.get('frequence_recurrence', None) if depense.est_recurrente else None
        db.session.commit()
        flash("Dépense modifiée avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la modification de la dépense: {e}", "danger")
    return redirect(url_for('routes.gestion_depenses_ordinaires'))

# Route pour supprimer une dépense
@bp.route('/supprimer_depense', methods=['POST'])
def supprimer_depense():
    id = request.form['idDel']
    depense = Depenses.query.get_or_404(id)
    try:
        db.session.delete(depense)
        db.session.commit()
        flash("Dépense supprimée avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression de la dépense: {e}", "danger")
    return redirect(url_for('routes.gestion_depenses_ordinaires'))

# Route pour ajouter une dépense récurrente
@bp.route('/ajouter_depense_recurrente', methods=['POST'])
def ajouter_depense_recurrente():
    try:
        description = request.form['description']
        montant = float(request.form['montant'])
        categorie = request.form.get('categorie', '')
        frequence_recurrence = request.form.get('frequence_recurrence', None)

        nouvelle_depense = Depenses(
            description=description,
            montant=montant,
            categorie=categorie,
            est_recurrente=True,  # Toujours récurrente pour cette route
            frequence_recurrence=frequence_recurrence
        )
        db.session.add(nouvelle_depense)
        db.session.commit()
        flash("Dépense récurrente ajoutée avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'ajout de la dépense récurrente: {e}", "danger")
    return redirect(url_for('routes.gestion_depenses_recurrentes'))

# Route pour modifier une dépense récurrente
@bp.route('/modifier_depense_recurrente/<int:id>', methods=['POST'])
def modifier_depense_recurrente(id):
    depense = Depenses.query.get_or_404(id)
    try:
        depense.description = request.form['description']
        depense.montant = float(request.form['montant'])
        depense.categorie = request.form.get('categorie', '')
        depense.frequence_recurrence = request.form.get('frequence_recurrence', None)
        db.session.commit()
        flash("Dépense récurrente modifiée avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la modification de la dépense récurrente: {e}", "danger")
    return redirect(url_for('routes.gestion_depenses_recurrentes'))

# Route pour supprimer une dépense récurrente
@bp.route('/supprimer_depense_recurrente', methods=['POST'])
def supprimer_depense_recurrente():
    id = request.form['idDel']
    depense = Depenses.query.get_or_404(id)
    try:
        db.session.delete(depense)
        db.session.commit()
        flash("Dépense récurrente supprimée avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de la suppression de la dépense récurrente: {e}", "danger")
    return redirect(url_for('routes.gestion_depenses_recurrentes'))

from datetime import datetime


from datetime import datetime, timedelta

@bp.route('/benefices')
def gestion_benefices():
    # Récupérer les dates de filtrage (si elles sont fournies)
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    # Si les dates ne sont pas fournies, utiliser la date du jour
    if not date_debut or not date_fin:
        aujourd_hui = datetime.now().strftime('%Y-%m-%d')
        date_debut = aujourd_hui
        date_fin = aujourd_hui

    # Convertir les dates en objets datetime pour le filtrage
    date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
    date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d') + timedelta(days=1)  # Ajouter 1 jour pour inclure toute la journée

    # Base de la requête pour les ventes
    query_ventes = db.session.query(
        Produits.nom,
        Factures.date_facture.label('date_facture'),  # Ajouter la date de la facture
        db.func.sum(Ventes.quantite).label('quantite_vendue'),
        db.func.sum(Ventes.montant_total).label('montant_ventes'),
        db.func.sum(Ventes.quantite * Produits.prix_achat).label('cout_achat'),
        db.func.sum(Ventes.montant_total - (Ventes.quantite * Produits.prix_achat)).label('benefice')
    ).join(Produits, Ventes.produit_id == Produits.id) \
    .join(Factures, Ventes.facture_id == Factures.id)  # Jointure avec Factures

    # Appliquer le filtrage par date
    query_ventes = query_ventes.filter(Factures.date_facture >= date_debut_obj) \
                               .filter(Factures.date_facture < date_fin_obj)  # Utiliser < pour exclure la date de fin

    # Calculer les bénéfices par produit
    benefices_par_produit = query_ventes.group_by(Produits.nom, Factures.date_facture).all()

    # Calculer le total des ventes
    total_ventes = db.session.query(db.func.sum(Ventes.montant_total)) \
        .join(Factures, Ventes.facture_id == Factures.id) \
        .filter(Factures.date_facture >= date_debut_obj) \
        .filter(Factures.date_facture < date_fin_obj) \
        .scalar() or 0

    # Calculer le total des coûts des marchandises vendues (corrigé)
    total_couts = db.session.query(
        db.func.sum(Ventes.quantite * Produits.prix_achat)
    ).join(Produits, Ventes.produit_id == Produits.id) \
        .join(Factures, Ventes.facture_id == Factures.id) \
        .filter(Factures.date_facture >= date_debut_obj) \
        .filter(Factures.date_facture < date_fin_obj) \
        .scalar() or 0

    # Calculer le bénéfice brut (total des ventes - total des coûts)
    benefice_brut = total_ventes - total_couts

    # Calculer le total des dépenses (ordinaires et récurrentes)
    total_depenses = db.session.query(db.func.sum(Depenses.montant)) \
        .filter(Depenses.date_depense >= date_debut_obj) \
        .filter(Depenses.date_depense < date_fin_obj) \
        .scalar() or 0

    # Calculer le bénéfice net (bénéfice brut - total des dépenses)
    benefice_net = benefice_brut - total_depenses

    return render_template(
        'gestion_benefices.html',
        total_ventes=total_ventes,
        total_couts=total_couts,
        benefice_brut=benefice_brut,
        total_depenses=total_depenses,
        benefice_net=benefice_net,
        benefices_par_produit=benefices_par_produit,
        date_debut=date_debut,
        date_fin=date_fin
    )

# Route pour afficher les transactions de dépôt
@bp.route('/gestion_transactions_depot')
def gestion_transactions_depot():
    transactions_depot = TransactionDepot.query.order_by(TransactionDepot.date_transaction.desc()).all()
    produits = Produits.query.all()
    return render_template('gestion_transactions_depot.html', transactions_depot=transactions_depot, produits=produits)

# Route pour ajouter une transaction de dépôt
@bp.route('/ajouter_transaction_depot', methods=['POST'])
def ajouter_transaction_depot():
    try:
        produit_id = int(request.form['produit_id'])
        quantite = int(request.form['quantite'])
        type_transaction = request.form['type_transaction']
        description = request.form.get('description', '')  # Récupérer la description

        produit = Produits.query.get_or_404(produit_id)

        if type_transaction == 'entree':
            produit.quantite_depot += quantite
        elif type_transaction == 'sortie':
            if produit.quantite_depot < quantite:
                flash("Quantité insuffisante en stock!", "danger")
                return redirect(url_for('routes.gestion_transactions_depot'))
            produit.quantite_depot -= quantite
        else:
            flash("Type de transaction invalide!", "danger")
            return redirect(url_for('routes.gestion_transactions_depot'))

        nouvelle_transaction = TransactionDepot(
            produit_id=produit_id,
            quantite=quantite,
            type_transaction=type_transaction,
            description=description  # Ajouter la description
        )
        db.session.add(nouvelle_transaction)
        db.session.commit()
        flash("Transaction de dépôt ajoutée avec succès!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'ajout de la transaction de dépôt: {e}", "danger")
    return redirect(url_for('routes.gestion_transactions_depot'))

# Récupérer tous les produits avec leur quantité en dépôt
@bp.route('/stock_depot')
def stock_depot():
    # Récupérer tous les produits avec leur quantité en dépôt
    produits = Produits.query.filter(Produits.quantite_depot > 0).all()
    return render_template('stock_depot.html', produits=produits)

@bp.route('/stock_boutique')
def stock_boutique():
    # Récupérer tous les produits avec leur quantité en boutique
    produits = Produits.query.filter(Produits.quantite > 0).all()
    return render_template('stock_boutique.html', produits=produits)

@bp.route('/stock_global')
def stock_global():
    # Récupérer tous les produits avec leur quantité en magasin et en dépôt
    produits = Produits.query.all()
    
    # Calculer le coût total pour chaque produit et le coût total global
    cout_total_global = 0
    produits_avec_cout = []
    
    for produit in produits:
        cout_total_produit = (produit.quantite + produit.quantite_depot) * produit.prix_achat
        cout_total_global += cout_total_produit
        produits_avec_cout.append({
            'produit': {
                'id': produit.id,
                'nom': produit.nom,
                'quantite': produit.quantite,
                'quantite_depot': produit.quantite_depot,
                'prix_achat': produit.prix_achat,
                'description': produit.description,
                # Ajoutez d'autres champs si nécessaire
            },
            'cout_total': cout_total_produit
        })
    
    return render_template('stock_global.html', produits_avec_cout=produits_avec_cout, cout_total_global=cout_total_global)