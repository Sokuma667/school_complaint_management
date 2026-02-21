"""
Exercice 3 – Test de Performance avec Selenium
===============================================
Mesure les temps de réponse de l'authentification pour N utilisateurs en parallèle (10, 100).
Les résultats détaillés (avec métriques de performance) sont enregistrés dans un CSV.

Différence avec l'Exercice 2 :
  - Exercice 2 : test de CHARGE (succès/échec, volume)
  - Exercice 3 : test de PERFORMANCE (temps de chargement, métriques detaillées)

Métriques mesurées :
  - Temps de chargement de la page de connexion
  - Temps de saisie du formulaire
  - Temps de réponse après soumission
  - Temps total de connexion
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

# Comptes de test (rotation entre plusieurs comptes)
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
    """Retourne un compte de test différent pour chaque utilisateur (rotation)."""
    return TEST_ACCOUNTS[user_id % len(TEST_ACCOUNTS)]

WAIT_TIMEOUT = 15
NB_UTILISATEURS_PHASE1 = 10
NB_UTILISATEURS_PHASE2 = 100
MAX_THREADS_SIMULTANES = 8

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "resultats")
os.makedirs(RESULTS_DIR, exist_ok=True)
CSV_FILE_10   = os.path.join(RESULTS_DIR, "perf_10_utilisateurs.csv")
CSV_FILE_100  = os.path.join(RESULTS_DIR, "perf_100_utilisateurs.csv")

# Seuils de performance acceptables (en secondes)
SEUIL_CHARGEMENT_PAGE = 3.0   
SEUIL_CONNEXION_TOTALE = 5.0  
# ───────────────────────────────────────────────


def get_driver() -> webdriver.Chrome:
    """Crée un driver Chrome en mode headless pour les tests de performance."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    return driver


# ════════════════════════════════════════════════════════════════════════════
#  4) FONCTION D'ENREGISTREMENT DES RÉSULTATS DANS UN CSV
# ════════════════════════════════════════════════════════════════════════════

def enregistrer_resultats_csv(resultats: list, chemin_csv: str) -> None:
    """
    Enregistre les métriques de performance dans un fichier CSV.

    Colonnes :
      utilisateur_id | email | statut | temps_chargement_page_s |
      temps_saisie_s | temps_reponse_serveur_s | temps_total_s |
      conforme_seuils | message_erreur | timestamp
    """
    entetes = [
        "utilisateur_id",
        "telephone_ou_email",
        "statut",                       # SUCCÈS ou ÉCHEC
        "temps_chargement_page_s",      # Chargement de la page de connexion
        "temps_saisie_s",               # Saisie des champs du formulaire
        "temps_reponse_serveur_s",      # Temps de réponse du backend
        "temps_total_s",                # Durée totale du scénario
        "conforme_seuils",              # OUI ou NON selon les seuils définis
        "message_erreur",
        "timestamp",
    ]

    with open(chemin_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=entetes)
        writer.writeheader()
        writer.writerows(resultats)

    print(f"\n Résultats de performance enregistrés dans : {chemin_csv}")
    print(f"     {len(resultats)} lignes écrites.")


# ════════════════════════════════════════════════════════════════════════════
#  FONCTION DE TEST DE PERFORMANCE POUR UN UTILISATEUR (THREAD)
# ════════════════════════════════════════════════════════════════════════════

def tester_performance_utilisateur(
    user_id: int,
    email: str,
    password: str,
    resultats: list,
    verrou: threading.Lock
) -> None:
    """
    Simule la connexion d'un utilisateur et mesure les temps de chaque étape.
    """
    driver = None
    debut_total = time.time()
    statut = "ÉCHEC"
    message_erreur = ""

    # Métriques individuelles
    tps_chargement_page   = 0.0
    tps_saisie            = 0.0
    tps_reponse_serveur   = 0.0
    tps_total             = 0.0

    try:
        driver = get_driver()
        wait   = WebDriverWait(driver, WAIT_TIMEOUT)

        # ══ MESURE 1 : Temps de chargement de la page ══
        t0 = time.time()
        driver.get(LOGIN_URL)
        # Attendre que le formulaire soit visible
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        tps_chargement_page = round(time.time() - t0, 3)

        # ══ MESURE 2 : Temps de saisie du formulaire ══
        t1 = time.time()
        email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email_input.send_keys(email)
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
        tps_saisie = round(time.time() - t1, 3)

        # ══ MESURE 3 : Temps de réponse du serveur ══
        t2 = time.time()
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("dashboard"))
        tps_reponse_serveur = round(time.time() - t2, 3)

        statut = "SUCCÈS"

    except Exception as e:
        message_erreur = str(e)[:200]

    finally:
        tps_total = round(time.time() - debut_total, 3)
        if driver:
            driver.quit()

        # Évaluation des seuils de performance
        conforme = (
            tps_chargement_page <= SEUIL_CHARGEMENT_PAGE and
            tps_total <= SEUIL_CONNEXION_TOTALE and
            statut == "SUCCÈS"
        )

        resultat = {
            "utilisateur_id"          : user_id,
            "telephone_ou_email"      : email,
            "statut"                  : statut,
            "temps_chargement_page_s" : tps_chargement_page,
            "temps_saisie_s"          : tps_saisie,
            "temps_reponse_serveur_s" : tps_reponse_serveur,
            "temps_total_s"           : tps_total,
            "conforme_seuils"         : "OUI" if conforme else "NON",
            "message_erreur"          : message_erreur,
            "timestamp"               : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        with verrou:
            resultats.append(resultat)
            seuil_ok = "✔ CONFORME" if conforme else "✖ HORS SEUIL"
            print(
                f"  [U-{user_id:03d}] {statut} | total={tps_total}s | "
                f"page={tps_chargement_page}s | serveur={tps_reponse_serveur}s | {seuil_ok}"
            )


# ════════════════════════════════════════════════════════════════════════════
#  RAPPORT DE PERFORMANCE
# ════════════════════════════════════════════════════════════════════════════

def afficher_rapport_performance(resultats: list, titre: str) -> None:
    """Affiche un rapport détaillé de performance dans la console."""
    total   = len(resultats)
    succes  = [r for r in resultats if r["statut"] == "SUCCÈS"]
    echecs  = total - len(succes)
    conformes = sum(1 for r in resultats if r["conforme_seuils"] == "OUI")

    def stat(valeurs):
        if not valeurs:
            return 0, 0, 0
        return round(min(valeurs), 3), round(max(valeurs), 3), round(sum(valeurs) / len(valeurs), 3)

    temps_total    = [r["temps_total_s"]             for r in succes]
    temps_charg    = [r["temps_chargement_page_s"]   for r in succes]
    temps_serveur  = [r["temps_reponse_serveur_s"]   for r in succes]

    t_min, t_max, t_moy = stat(temps_total)
    p_min, p_max, p_moy = stat(temps_charg)
    s_min, s_max, s_moy = stat(temps_serveur)

    print(f"\n{'═' * 60}")
    print(f"  RAPPORT PERFORMANCE – {titre}")
    print(f"{'═' * 60}")
    print(f"  Utilisateurs testés      : {total}")
    print(f"  ✔ Succès                 : {len(succes)}")
    print(f"  ✖ Échecs                 : {echecs}")
    print(f"  ✔ Conformes aux seuils   : {conformes}")
    print(f"{'─' * 60}")
    print(f"  Temps total (connexion) :")
    print(f"    Min={t_min}s | Max={t_max}s | Moy={t_moy}s")
    print(f"    Seuil accepté : < {SEUIL_CONNEXION_TOTALE}s")
    print(f"  Temps chargement page :")
    print(f"    Min={p_min}s | Max={p_max}s | Moy={p_moy}s")
    print(f"    Seuil accepté : < {SEUIL_CHARGEMENT_PAGE}s")
    print(f"  Temps réponse serveur :")
    print(f"    Min={s_min}s | Max={s_max}s | Moy={s_moy}s")
    print(f"{'═' * 60}")


# ════════════════════════════════════════════════════════════════════════════
#  LANCEMENT DU TEST DE PERFORMANCE EN PARALLÈLE
# ════════════════════════════════════════════════════════════════════════════

def lancer_test_performance(nb_utilisateurs: int, csv_sortie: str) -> None:
    """
    Lance le test de performance avec N utilisateurs en parallèle.
    """
    print(f"\n{'─' * 60}")
    print(f"  DÉMARRAGE DU TEST DE PERFORMANCE")
    print(f"  Utilisateurs en parallèle : {nb_utilisateurs}")
    print(f"  Seuils : page < {SEUIL_CHARGEMENT_PAGE}s | total < {SEUIL_CONNEXION_TOTALE}s")
    print(f"{'─' * 60}")

    resultats: list  = []
    verrou           = threading.Lock()
    threads          = []
    debut_global     = time.time()

    # Lancer par batch pour éviter les crashs
    batch_size = MAX_THREADS_SIMULTANES
    for i in range(0, nb_utilisateurs, batch_size):
        batch_threads = []
        for user_id in range(i + 1, min(i + batch_size + 1, nb_utilisateurs + 1)):
            email, password = get_test_account(user_id)
            t = threading.Thread(
                target=tester_performance_utilisateur,
                args=(user_id, email, password, resultats, verrou)
            )
            batch_threads.append(t)
            threads.append(t)
            t.start()
        
        for t in batch_threads:
            t.join()
        
        time.sleep(0.5)

    duree_totale = round(time.time() - debut_global, 2)
    print(f"\n  Durée totale du test : {duree_totale}s")

    # Trier par user_id
    resultats.sort(key=lambda r: r["utilisateur_id"])

    # ── 5) Enregistrer dans le CSV ──
    enregistrer_resultats_csv(resultats, csv_sortie)

    # ── 6) Rapport de synthèse ──
    afficher_rapport_performance(resultats, f"TEST PERF – {nb_utilisateurs} UTILISATEURS")


# ════════════════════════════════════════════════════════════════════════════
#  PROGRAMME PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "█" * 60)
    print("  EXERCICE 3 – TEST DE PERFORMANCE")
    print("█" * 60)

    # ── Étape 1 : 10 utilisateurs en parallèle ──
    print("\n  Étape 1 : Test avec 10 utilisateurs en parallèle")
    lancer_test_performance(NB_UTILISATEURS_PHASE1, CSV_FILE_10)

    print("\n" + "=" * 60)
    input("  Appuyer sur Entrée pour lancer le test avec 100 utilisateurs...")
    print("=" * 60)

    # ── Étape 2 : 100 utilisateurs en parallèle ──
    print("\n  Étape 2 : Test avec 100 utilisateurs en parallèle")
    lancer_test_performance(NB_UTILISATEURS_PHASE2, CSV_FILE_100)

    print(f"\n[✔] Tests de performance terminés.")
    print(f"    Résultats disponibles dans : {RESULTS_DIR}")
