from flask import Flask, render_template, request, redirect, url_for, flash, abort
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Changez cela pour la production

def load_clubs():
    """
    Charge les données des clubs à partir d'un fichier JSON.

    Returns:
        list: Une liste de dictionnaires représentant les clubs.
    """
    with open('clubs.json') as c:
        clubs = json.load(c)['clubs']
    return clubs

def load_competitions():
    """
    Charge les données des compétitions à partir d'un fichier JSON.

    Returns:
        list: Une liste de dictionnaires représentant les compétitions.
    """
    with open('competitions.json') as comps:
        competitions = json.load(comps)['competitions']
    return competitions

# Variables globales pour stocker les données des clubs et des compétitions
clubs = load_clubs()
competitions = load_competitions()

@app.errorhandler(404)
def page_not_found(e):
    """
    Gère les erreurs 404 (page non trouvée) en renvoyant une page personnalisée.

    Args:
        e: L'objet d'exception représentant l'erreur.

    Returns:
        tuple: Le template de la page 404 et le code d'état 404.
    """
    return render_template('404.html'), 404

@app.route('/')
def index():
    """
    Route de la page d'accueil.

    Returns:
        str: Le rendu du template de la page d'accueil.
    """
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def show_summary():
    """
    Route pour afficher le résumé des compétitions après la connexion.

    Cette route récupère l'email du formulaire, recherche le club correspondant,
    et affiche la page d'accueil avec les informations du club et des compétitions.
    Si l'email est incorrect, l'utilisateur est redirigé vers la page d'accueil avec un message d'erreur.

    Returns:
        str: Le rendu du template avec les informations du club et des compétitions.
    """
    email = request.form['email']
    # Recherche du club correspondant à l'email fourni
    club = next((club for club in clubs if club['email'] == email), None)
    if club:
        # Affiche la page d'accueil avec les détails du club et des compétitions
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        # Affiche un message d'erreur et redirige vers la page d'accueil
        flash("Email incorrect !")
        return redirect(url_for('index'))

@app.route('/book/<competition>/<club>')
def book(competition, club):
    """
    Route pour accéder à la page de réservation.

    Cette route vérifie si la compétition et le club existent. Si c'est le cas,
    elle affiche la page de réservation. Sinon, elle renvoie une erreur 404.

    Args:
        competition (str): Le nom de la compétition.
        club (str): Le nom du club.

    Returns:
        str: Le rendu du template de réservation si les données sont valides.
        abort: Renvoie une erreur 404 si la compétition ou le club n'existent pas.
    """
    # Recherche de la compétition et du club
    found_competition = next((c for c in competitions if c['name'] == competition), None)
    found_club = next((c for c in clubs if c['name'] == club), None)
    if found_competition and found_club:
        # Affiche la page de réservation
        return render_template('booking.html', club=found_club, competition=found_competition)
    else:
        # Renvoie une erreur 404 si la compétition ou le club n'existent pas
        abort(404, description="Compétition ou club non trouvé")

@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    """
    Route pour gérer l'achat de places.

    Cette route traite les demandes d'achat de places pour une compétition donnée.
    Elle vérifie les conditions suivantes avant d'effectuer l'achat :
    - Le club et la compétition doivent exister.
    - Le club doit avoir suffisamment de points.
    - La compétition doit avoir suffisamment de places disponibles.
    - Le nombre de places demandées ne doit pas dépasser 12.

    Si toutes les conditions sont remplies, l'achat est effectué et le nombre de
    points et de places est mis à jour. Sinon, un message d'erreur est affiché.

    Returns:
        str: Le rendu du template de résumé avec les informations mises à jour.
    """
    competition_name = request.form['competition']
    club_name = request.form['club']
    places_required = int(request.form['places'])

    # Recherche de la compétition et du club
    found_competition = next((c for c in competitions if c['name'] == competition_name), None)
    found_club = next((c for c in clubs if c['name'] == club_name), None)

    if not found_competition or not found_club:
        flash("Erreur : Club ou compétition introuvable.")
        return redirect(url_for('index'))

    # Vérification des conditions d'achat
    if places_required > int(found_club['points']):
        flash("Erreur : Vous n'avez pas assez de points.")
    elif places_required > int(found_competition['numberOfPlaces']):
        flash("Erreur : Pas assez de places disponibles.")
    elif places_required > 12:
        flash("Erreur : Vous ne pouvez pas réserver plus de 12 places.")
    else:
        # Mise à jour du nombre de places et des points après un achat réussi
        found_competition['numberOfPlaces'] = str(int(found_competition['numberOfPlaces']) - places_required)
        found_club['points'] = str(int(found_club['points']) - places_required)
        flash(f"Réservation réussie pour {places_required} places.")
    
    return render_template('welcome.html', club=found_club, competitions=competitions)

@app.route('/logout')
def logout():
    """
    Route pour déconnecter l'utilisateur.

    Redirige l'utilisateur vers la page d'accueil après la déconnexion.

    Returns:
        werkzeug.wrappers.response.Response: La redirection vers la page d'accueil.
    """
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
