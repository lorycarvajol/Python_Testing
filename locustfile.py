from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    def on_start(self):
        """Cette méthode est exécutée lorsque l'utilisateur démarre, simulate la connexion."""
        # Simuler la connexion
        response = self.client.post("/showSummary", data={"email": "admin@irontemple.com"})
        if response.status_code != 200:
            print("Erreur lors de la connexion !")

    @task(2)
    def index(self):
        """Simuler l'accès à la page d'accueil."""
        self.client.get("/")
    
    @task(3)
    def book_places(self):
        """Simuler la réservation de places."""
        # Simuler la réservation de 3 places pour la compétition "Spring Festival"
        response = self.client.post("/purchasePlaces", data={
            "club": "Iron Temple",
            "competition": "Spring Festival",
            "places": "3"
        })
        if response.status_code != 200:
            print("Erreur lors de la réservation des places !")

    @task(1)
    def logout(self):
        """Simuler la déconnexion."""
        self.client.get("/logout")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 3)  # Le temps d'attente entre les tâches est de 1 à 3 secondes.
