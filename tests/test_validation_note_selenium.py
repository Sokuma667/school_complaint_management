"""
Test Selenium : Validation de note avec navigateur visible
===========================================================
Test de validation de note par un enseignant via l'interface web.
Le navigateur s'ouvre pour voir les actions en temps réel.

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

# Configuration
BASE_URL = "http://localhost:3000"
LOGIN_URL = f"{BASE_URL}/"
ENSEIGNANT_EMAIL = "yaya.traore@ibam.ma"  # Enseignant avec des demandes
ENSEIGNANT_PASSWORD = "password123"
WAIT_TIMEOUT = 10


def get_driver() -> webdriver.Chrome:
    """Crée un driver Chrome AVEC interface visible."""
    options = Options()
    # PAS de --headless pour voir le navigateur
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver


class TestValidationNoteSelenium(unittest.TestCase):
    """Test de validation de note via l'interface web."""

    def setUp(self):
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def tearDown(self):
        time.sleep(2)  # Pause pour voir le résultat
        self.driver.quit()

    def _login_enseignant(self):
        """Connexion en tant qu'enseignant."""
        print(f"\n[→] Connexion en tant qu'enseignant : {ENSEIGNANT_EMAIL}")
        self.driver.get(LOGIN_URL)
        
        email_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.send_keys(ENSEIGNANT_EMAIL)
        self.driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(ENSEIGNANT_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Attendre le dashboard
        self.wait.until(EC.url_contains("dashboard"))
        print("[✔] Connexion réussie")
        time.sleep(1)

    def test_validation_note_interface(self):
        """
        Test : Tenter de saisir une note invalide via l'interface web.
        Le navigateur s'ouvre pour voir les actions.
        """
        # Étape 1 : Connexion
        self._login_enseignant()
        
        # Étape 2 : Trouver une demande IMPUTEE
        print("[→] Recherche d'une demande à analyser...")
        demandes = self.driver.find_elements(By.CSS_SELECTOR, ".reclamation-card")
        
        if not demandes:
            print("[!] Aucune demande trouvée pour cet enseignant")
            self.skipTest("Aucune demande disponible")
        
        # Cliquer sur la première demande IMPUTEE
        demande_trouvee = False
        for demande in demandes:
            statut = demande.find_element(By.CSS_SELECTOR, ".status").text
            if "IMPUTEE" in statut or "IMPUTÉE" in statut:
                print(f"[→] Demande trouvée avec statut : {statut}")
                demande.click()
                demande_trouvee = True
                break
        
        if not demande_trouvee:
            print("[!] Aucune demande IMPUTEE trouvée")
            self.skipTest("Aucune demande IMPUTEE disponible")
        
        # Étape 3 : Cliquer sur une carte de demande IMPUTEE pour ouvrir la modal
        print("[→] Clic sur la demande pour ouvrir la modal...")
        self.driver.execute_script("arguments[0].click();", demande)
        time.sleep(2)
        
        # Étape 4 : La modal s'ouvre automatiquement avec le formulaire d'analyse
        print("[→] Test : Saisie d'une note invalide (25/20)...")
        try:
            # Saisir un commentaire
            commentaire = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".modal input[placeholder*='Commentaire'], .modal input[placeholder*='commentaire']"))
            )
            commentaire.send_keys("Test de validation de note")
            
            # Saisir une note invalide
            note_input = self.driver.find_element(By.CSS_SELECTOR, ".modal input[type='number']")
            note_input.clear()
            note_input.send_keys("25")
            
            time.sleep(1)
            
            # Cliquer sur Accepter
            accepter_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accepter') and contains(@class, 'btn-primary')]")
            accepter_btn.click()
            
            time.sleep(2)
            
            # Vérifier qu'un message d'erreur apparaît
            try:
                error_msg = self.driver.find_element(By.CSS_SELECTOR, ".error, .alert-danger, [class*='error']")
                print(f"[✔] Message d'erreur affiché : {error_msg.text}")
                self.assertTrue(len(error_msg.text) > 0, "Un message d'erreur doit être affiché")
            except:
                # Si pas de message d'erreur visible, vérifier qu'on n'a pas été redirigé
                current_url = self.driver.current_url
                print(f"[→] URL actuelle : {current_url}")
                # On devrait toujours être sur la page de détail
                self.assertIn("reclamation", current_url.lower(), 
                             "L'utilisateur ne devrait pas être redirigé avec une note invalide")
            
            print("[✔] Test terminé : La note invalide a été rejetée")
            
        except Exception as e:
            print(f"[!] Erreur lors du test : {str(e)}")
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("  TEST SELENIUM : VALIDATION DE NOTE (NAVIGATEUR VISIBLE)")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestValidationNoteSelenium)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    exit(0 if result.wasSuccessful() else 1)
