"""
Exercice 6 – Test Unitaire avec Selenium
=========================================
Test d'affichage de la page de connexion :
  - Vérifie que le bon formulaire est affiché
  - Vérifie que le TITRE du formulaire correspond au titre attendu
  - Vérifie la présence de tous les champs du formulaire
  - Vérifie le titre de l'onglet (document.title)

Prérequis :
  pip install selenium
  Le backend Spring Boot doit tourner  (localhost:8080)
  Le frontend Vite doit tourner        (localhost:3000)
"""

import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ──────────────── CONFIGURATION ────────────────
BASE_URL  = "http://localhost:3000"
LOGIN_URL = f"{BASE_URL}/"

# Valeurs attendues (définies par la spécification de la plateforme)
TITRE_ONGLET_ATTENDU   = "IBAM - Réclamations"  # document.title (index.html)
TITRE_FORMULAIRE_ATTENDU = "IBAM - Réclamations"       # Contenu du <h1> affiché dans la page

WAIT_TIMEOUT = 10
# ───────────────────────────────────────────────


def get_driver() -> webdriver.Chrome:
    """Crée et retourne un driver Chrome."""
    options = Options()
    # options.add_argument("--headless")  # Décommenter pour exécution sans interface
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver


# ═══════════════════════════════════════════════════════════════════════════
#  EXERCICE 6 – TESTS UNITAIRES : AFFICHAGE DE LA PAGE DE CONNEXION
# ═══════════════════════════════════════════════════════════════════════════

class TestAffichagePageConnexion(unittest.TestCase):
    """
    Tests unitaires vérifiant que le formulaire de connexion est correctement affiché.
    Chaque méthode = un test unitaire atomique et indépendant.
    """

    @classmethod
    def setUpClass(cls):
        """Ouvre le navigateur UNE SEULE FOIS pour tous les tests de cette classe."""
        cls.driver = get_driver()
        cls.wait   = WebDriverWait(cls.driver, WAIT_TIMEOUT)
        cls.driver.get(LOGIN_URL)
        # Attendre que le contenu React soit rendu
        cls.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )

    @classmethod
    def tearDownClass(cls):
        """Ferme le navigateur après tous les tests de la classe."""
        cls.driver.quit()

    # ── TEST 1 : Titre de l'onglet du navigateur ──────────────────────────

    def test_01_titre_onglet_navigateur(self):
        """
        Vérifie que le TITRE de l'onglet du navigateur (document.title)
        correspond au titre attendu défini dans index.html.

        Valeur attendue : "Logiciel de Réclamations"
        """
        titre_actuel = self.driver.title
        print(f"\n[→] Titre de l'onglet détecté : '{titre_actuel}'")
        print(f"[→] Titre attendu              : '{TITRE_ONGLET_ATTENDU}'")

        self.assertEqual(
            titre_actuel,
            TITRE_ONGLET_ATTENDU,
            f"Le titre de l'onglet doit être '{TITRE_ONGLET_ATTENDU}', "
            f"mais on a obtenu : '{titre_actuel}'"
        )
        print("[✔] Test 1 PASSÉ : Titre de l'onglet correct")

    # ── TEST 2 : Titre du formulaire (H1) ─────────────────────────────────

    def test_02_titre_formulaire_h1(self):
        """
        Vérifie que le TITRE AFFICHÉ dans le formulaire de connexion (balise H1)
        correspond au titre attendu.

        C'est la vérification principale demandée par l'Exercice 6 :
        "Vérifie que le formulaire qui s'affiche est le bon en vérifiant
         si le titre du formulaire correspond au titre du formulaire attendu."

        Valeur attendue : "IBAM - Réclamations"
        """
        h1 = self.wait.until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )
        titre_actuel = h1.text.strip()
        print(f"\n[→] Titre du formulaire détecté : '{titre_actuel}'")
        print(f"[→] Titre attendu               : '{TITRE_FORMULAIRE_ATTENDU}'")

        self.assertEqual(
            titre_actuel,
            TITRE_FORMULAIRE_ATTENDU,
            f"Le titre du formulaire doit être '{TITRE_FORMULAIRE_ATTENDU}', "
            f"mais on a obtenu : '{titre_actuel}'"
        )
        print("[✔] Test 2 PASSÉ : Titre du formulaire correct")

    # ── TEST 3 : Présence du champ Email ──────────────────────────────────

    def test_03_presence_champ_email(self):
        """
        Vérifie que le champ de saisie de l'email est bien présent et visible
        dans le formulaire de connexion.
        """
        email_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")

        self.assertTrue(
            email_input.is_displayed(),
            "Le champ Email (type='email') doit être visible sur la page de connexion"
        )
        print("[✔] Test 3 PASSÉ : Champ Email visible")

    # ── TEST 4 : Présence du champ Mot de passe ───────────────────────────

    def test_04_presence_champ_mot_de_passe(self):
        """
        Vérifie que le champ de saisie du mot de passe est présent et visible.
        """
        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")

        self.assertTrue(
            password_input.is_displayed(),
            "Le champ Mot de passe (type='password') doit être visible sur la page de connexion"
        )
        print("[✔] Test 4 PASSÉ : Champ Mot de passe visible")

    # ── TEST 5 : Présence du bouton de soumission ─────────────────────────

    def test_05_presence_bouton_connexion(self):
        """
        Vérifie que le bouton 'Se connecter' est présent, visible et cliquable.
        """
        submit_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )

        self.assertTrue(
            submit_btn.is_displayed(),
            "Le bouton de soumission doit être visible"
        )
        self.assertTrue(
            submit_btn.is_enabled(),
            "Le bouton de soumission doit être activé (enabled)"
        )

        texte_bouton = submit_btn.text.strip()
        print(f"\n[→] Texte du bouton : '{texte_bouton}'")
        self.assertIn(
            "connect", texte_bouton.lower(),
            f"Le bouton de soumission doit contenir 'connect', obtenu : '{texte_bouton}'"
        )
        print("[✔] Test 5 PASSÉ : Bouton de connexion visible et activé")

    # ── TEST 6 : Présence du label "Email" ────────────────────────────────

    def test_06_presence_label_email(self):
        """
        Vérifie que le label 'Email' est affiché avant le champ de saisie.
        """
        labels = self.driver.find_elements(By.TAG_NAME, "label")
        textes_labels = [lbl.text.strip().lower() for lbl in labels]

        self.assertTrue(
            any("email" in t for t in textes_labels),
            f"Un label 'Email' doit être présent. Labels trouvés : {textes_labels}"
        )
        print("[✔] Test 6 PASSÉ : Label 'Email' présent")

    # ── TEST 7 : Présence du label "Mot de passe" ─────────────────────────

    def test_07_presence_label_mot_de_passe(self):
        """
        Vérifie que le label 'Mot de passe' est affiché avant le champ de saisie.
        """
        labels = self.driver.find_elements(By.TAG_NAME, "label")
        textes_labels = [lbl.text.strip().lower() for lbl in labels]

        self.assertTrue(
            any("mot de passe" in t or "password" in t for t in textes_labels),
            f"Un label 'Mot de passe' doit être présent. Labels trouvés : {textes_labels}"
        )
        print("[✔] Test 7 PASSÉ : Label 'Mot de passe' présent")

    # ── TEST 8 : URL correcte ─────────────────────────────────────────────

    def test_08_url_page_connexion(self):
        """
        Vérifie que l'URL actuelle correspond bien à la page de connexion.
        """
        current_url = self.driver.current_url
        print(f"\n[→] URL actuelle : '{current_url}'")

        self.assertTrue(
            current_url.startswith(BASE_URL),
            f"L'URL doit commencer par '{BASE_URL}', obtenu : '{current_url}'"
        )
        self.assertNotIn(
            "dashboard", current_url,
            "La page de connexion ne doit PAS rediriger vers le dashboard sans authentification"
        )
        print("[✔] Test 8 PASSÉ : URL de la page de connexion correcte")

    # ── TEST 9 : Formulaire est le bon (structure globale) ────────────────

    def test_09_structure_formulaire(self):
        """
        Vérifie la structure globale du formulaire de connexion :
        Le formulaire doit contenir 2 champs (email + password) et 1 bouton.
        C'est la vérification que "le bon formulaire" est affiché.
        """
        # Vérifier qu'il y a exactement 2 champs input dans le formulaire principal
        form = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        inputs = form.find_elements(By.TAG_NAME, "input")
        nb_inputs = len(inputs)

        print(f"\n[→] Nombre de champs dans le formulaire : {nb_inputs}")
        self.assertGreaterEqual(
            nb_inputs, 2,
            f"Le formulaire de connexion doit avoir au moins 2 champs (email + password), "
            f"trouvé : {nb_inputs}"
        )

        # Vérifier qu'il y a un bouton de soumission
        buttons = form.find_elements(By.CSS_SELECTOR, "button[type='submit']")
        self.assertEqual(
            len(buttons), 1,
            f"Le formulaire doit avoir exactement 1 bouton de soumission, trouvé : {len(buttons)}"
        )

        print("[✔] Test 9 PASSÉ : Structure du formulaire correcte")
        print(f"    → {nb_inputs} champs de saisie + 1 bouton de soumission")


# ═══════════════════════════════════════════════════════════════════════════
#  PROGRAMME PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("  EXERCICE 6 – TESTS UNITAIRES : AFFICHAGE FORMULAIRE")
    print(f"  URL testée : {LOGIN_URL}")
    print(f"  Titre attendu du formulaire : '{TITRE_FORMULAIRE_ATTENDU}'")
    print(f"  Titre attendu de l'onglet   : '{TITRE_ONGLET_ATTENDU}'")
    print("═" * 60)

    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromTestCase(TestAffichagePageConnexion)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "═" * 60)
    print(f"  Tests passés  : {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Tests échoués : {len(result.failures)}")
    print(f"  Erreurs       : {len(result.errors)}")
    print("═" * 60)

    exit(0 if result.wasSuccessful() else 1)
