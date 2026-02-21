"""
Exercice 2 – Test de Charge avec Selenium
==========================================
Authentification de N utilisateurs en parallèle (10, 100).
Les résultats sont enregistrés dans un fichier CSV.

Structure du CSV généré :
  utilisateur_id, email, statut, duree_secondes, message_erreur, timestamp
"""

import csv
import os
import time
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ──────────────── CONFIGURATION ────────────────
BASE_URL      = "http://localhost:3000"
LOGIN_URL     = f"{BASE_URL}/"

# Comptes de test 
TEST_ACCOUNTS = [
    ("joel.soulama@ibam.ma", "password123"),
    ("aubin.compaore@ibam.ma", "password123"),
    ("soumaila.congombo@ibam.ma", "password123"),
    ("wilfried.coulibaly@ibam.ma", "password123"),
    ("noel.darga@ibam.ma", "password123"),
    ("charlene.dargani@ibam.ma", "password123"),
    ("belco.diallo@ibam.ma", "password123"),
    ("tassere.diallo@ibam.ma", "password123"),
    ("fadel.diawara@ibam.ma", "password123"),
    ("alou.dicko@ibam.ma", "password123"),
]

def get_test_account(user_id: int):
    """Retourne un compte de test différent pour chaque utilisateur."""
    return TEST_ACCOUNTS[user_id % len(TEST_ACCOUNTS)]

WAIT_TIMEOUT = 15
NB_UTILISATEURS_PHASE1 = 10    # Phase 1 : 10 utilisateurs 
NB_UTILISATEURS_PHASE2 = 100   # Phase 2 : 100 utilisateurs 
MAX_THREADS_SIMULTANES = 8

# Fichier CSV de sortie
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "resultats")
os.makedirs(RESULTS_DIR, exist_ok=True)
CSV_FILE_10   = os.path.join(RESULTS_DIR, "charge_10_utilisateurs.csv")
CSV_FILE_100  = os.path.join(RESULTS_DIR, "charge_100_utilisateurs.csv")
# ───────────────────────────────────────────────


def get_driver() -> webdriver.Chrome:
    """Crée un driver Chrome en mode headless pour les tests de charge."""
    options = Options()
    #options.add_argument("--headless")             
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")        
    driver = webdriver.Chrome(options=options)
    return driver


# ════════════════════════════════════════════════════════════════════════════
#  1) FONCTION D'ENREGISTREMENT DES RÉSULTATS DANS UN CSV
# ════════════════════════════════════════════════════════════════════════════

def enregistrer_resultats_csv(resultats: list, chemin_csv: str) -> None:
    """
    Enregistre les résultats de test de charge dans un fichier CSV.

    :param resultats: Liste de dictionnaires avec les résultats de chaque utilisateur.
    :param chemin_csv: Chemin du fichier CSV à créer/écraser.
    """
    entetes = [
        "utilisateur_id",
        "email",
        "statut",          
        "duree_secondes",
        "message_erreur",
        "timestamp"
    ]

    with open(chemin_csv, mode="w", newline="", encoding="utf-8") as fichier_csv:
        writer = csv.DictWriter(fichier_csv, fieldnames=entetes)
        writer.writeheader()
        writer.writerows(resultats)

    print(f"\n Résultats enregistrés dans : {chemin_csv}")
    print(f"     {len(resultats)} lignes écrites.")


def afficher_rapport(resultats: list, titre: str) -> None:
    """Affiche un rapport de synthèse dans la console."""
    total     = len(resultats)
    succes    = sum(1 for r in resultats if r["statut"] == "SUCCÈS")
    echecs    = total - succes
    durees    = [r["duree_secondes"] for r in resultats if r["statut"] == "SUCCÈS"]
    moy       = round(sum(durees) / len(durees), 2) if durees else 0
    duree_min = round(min(durees), 2) if durees else 0
    duree_max = round(max(durees), 2) if durees else 0

    print(f"\n{'═' * 55}")
    print(f"  RAPPORT – {titre}")
    print(f"{'═' * 55}")
    print(f"  Utilisateurs testés  : {total}")
    print(f"  ✔ Succès             : {succes}")
    print(f"  ✖ Échecs             : {echecs}")
    print(f"  Taux de succès       : {round(succes / total * 100, 1)}%")
    print(f"  Durée moyenne        : {moy} s")
    print(f"  Durée min            : {duree_min} s")
    print(f"  Durée max            : {duree_max} s")
    print(f"{'═' * 55}")


# ════════════════════════════════════════════════════════════════════════════
#  FONCTION DE TEST POUR UN UTILISATEUR
# ════════════════════════════════════════════════════════════════════════════

def tester_connexion_utilisateur(
    user_id: int,
    email: str,
    password: str,
    resultats: list,
    verrou: threading.Lock
) -> None:
    """
    Simule la connexion d'un utilisateur via Selenium.
    """
    driver = None
    debut  = time.time()
    statut = "ÉCHEC"
    message_erreur = ""

    try:
        driver  = get_driver()
        wait    = WebDriverWait(driver, WAIT_TIMEOUT)

        # ── Étape 1 : Naviguer vers la page de connexion ──
        driver.get(LOGIN_URL)

        # ── Étape 2 : Renseigner le formulaire ──
        email_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)

        # ── Étape 3 : Soumettre ──
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # ── Étape 4 : Vérifier la redirection ──
        wait.until(EC.url_contains("dashboard"))
        statut = "SUCCÈS"

    except Exception as e:
        message_erreur = str(e)[:200]  # Tronquer les messages trop longs
        statut = "ÉCHEC"

    finally:
        duree = round(time.time() - debut, 3)
        if driver:
            driver.quit()

        resultat = {
            "utilisateur_id"     : user_id,
            "email"              : email,
            "statut"             : statut,
            "duree_secondes"     : duree,
            "message_erreur"     : message_erreur,
            "timestamp"          : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        with verrou:
            resultats.append(resultat)
            print(f"  [U-{user_id:03d}] {statut} | {duree}s | {email}")


# ════════════════════════════════════════════════════════════════════════════
#  LANCEMENT DU TEST EN PARALLÈLE
# ════════════════════════════════════════════════════════════════════════════

def lancer_test_charge(nb_utilisateurs: int, csv_sortie: str) -> None:
    """
    Lance le test de charge avec N utilisateurs en parallèle.

    :param nb_utilisateurs: Nombre d'utilisateurs à simuler simultanément.
    :param csv_sortie:      Chemin du fichier CSV de sortie.
    """
    print(f"\n{'─' * 55}")
    print(f"  DÉMARRAGE DU TEST DE CHARGE")
    print(f"  Utilisateurs en parallèle : {nb_utilisateurs}")
    print(f"  URL testée                : {LOGIN_URL}")
    print(f"  Comptes utilisés          : {len(TEST_ACCOUNTS)} comptes en rotation")
    print(f"{'─' * 55}")

    resultats: list = []
    verrou          = threading.Lock()
    threads         = []

    debut_global = time.time()

    # Créer et démarrer les threads par batch pour éviter les crashs
    batch_size = MAX_THREADS_SIMULTANES
    for i in range(0, nb_utilisateurs, batch_size):
        batch_threads = []
        for user_id in range(i + 1, min(i + batch_size + 1, nb_utilisateurs + 1)):
            email, password = get_test_account(user_id)
            t = threading.Thread(
                target=tester_connexion_utilisateur,
                args=(user_id, email, password, resultats, verrou)
            )
            batch_threads.append(t)
            threads.append(t)
            t.start()
        
        # Attendre que le batch se termine avant de lancer le suivant
        for t in batch_threads:
            t.join()
        
        time.sleep(0.5)  # Pause entre les batchs

    duree_totale = round(time.time() - debut_global, 2)
    print(f"\n  Durée totale du test : {duree_totale}s")

    # ── 3) Enregistrer les résultats dans le CSV ──
    # Trier par user_id pour un CSV lisible
    resultats.sort(key=lambda r: r["utilisateur_id"])
    enregistrer_resultats_csv(resultats, csv_sortie)

    # Afficher le rapport de synthèse
    label = f"TEST DE CHARGE – {nb_utilisateurs} UTILISATEURS"
    afficher_rapport(resultats, label)


# ════════════════════════════════════════════════════════════════════════════
#  PROGRAMME PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # ── ÉTAPE 1 DEMANDÉE : 10 utilisateurs en parallèle ──
    print("\n" + "█" * 55)
    print("  EXERCICE 2 – TEST DE CHARGE")
    print("  Étape 1 : Test avec 10 utilisateurs en parallèle")
    print("█" * 55)
    lancer_test_charge(NB_UTILISATEURS_PHASE1, CSV_FILE_10)

    print("\n" + "=" * 55)
    input("  Appuyer sur Entrée pour lancer le test avec 100 utilisateurs...")
    print("=" * 55)

    # ── ÉTAPE 2 DEMANDÉE : 100 utilisateurs en parallèle ──
    print("\n" + "█" * 55)
    print("  EXERCICE 2 – TEST DE CHARGE")
    print("  Étape 2 : Test avec 100 utilisateurs en parallèle")
    print("█" * 55)
    lancer_test_charge(NB_UTILISATEURS_PHASE2, CSV_FILE_100)

    print(f"\n[✔] Tests de charge terminés.")
    print(f"    Résultats disponibles dans : {RESULTS_DIR}")
    print(f"    {len(TEST_ACCOUNTS)} comptes différents utilisés en rotation")
