import os
import sys
from werkzeug.security import generate_password_hash

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Utilisateur, Role

# Créer l'application Flask
app = create_app()

# Créer un contexte d'application pour accéder à la base de données
with app.app_context():
    # Vérifier si le rôle "admin" existe déjà
    admin_role = Role.query.filter_by(nom='admin').first()
    if not admin_role:
        # Créer le rôle "admin" s'il n'existe pas
        admin_role = Role(nom='admin')
        db.session.add(admin_role)
        db.session.commit()

    # Vérifier si l'utilisateur administrateur existe déjà
    admin_user = Utilisateur.query.filter_by(nom_utilisateur='admin').first()
    if not admin_user:
        # Créer un nouvel utilisateur administrateur
        admin_user = Utilisateur(
            nom_utilisateur='admin',
            email='admin@example.com',
            role_id=admin_role.id
        )
        admin_user.set_mot_de_passe('1234')  # Définir un mot de passe sécurisé
        db.session.add(admin_user)
        db.session.commit()
        print("Utilisateur administrateur créé avec succès.")
    else:
        print("L'utilisateur administrateur existe déjà.")