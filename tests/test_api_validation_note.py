"""
Test API : Validation de la nouvelle note proposée (Enseignant)
================================================================
Ce script vérifie que l'API du backend rejette correctement les notes
invalides (ex: 25/20 ou -2/20) lors de l'analyse d'une réclamation.

L'enseignant (ahmed.benali@ibam.ma) tente d'analyser la demande ID 1
dont le statut est 'IMPUTEE'.

Prérequis :
  pip install requests
  Le backend Spring Boot doit tourner sur localhost:8080
"""

import requests
import sys

# Configuration
BASE_URL = "http://localhost:8080/api"
ENSEIGNANT_EMAIL = "ahmed.benali@ibam.ma"
ENSEIGNANT_PASSWORD = "password123"
DEMANDE_ID = 1  # L'ID 1 est imputée à Ahmed Benali dans data.sql


def get_auth_token():
    print(f"[→] Connexion en tant qu'enseignant : {ENSEIGNANT_EMAIL}")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ENSEIGNANT_EMAIL, "password": ENSEIGNANT_PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"[!] Erreur de connexion : {response.status_code}")
        print(response.text)
        sys.exit(1)
        
    token = response.json().get("token")
    print("[✔] Token JWT récupéré avec succès")
    return token


def tester_note(token, note_proposee, description_test, attendu_ok=False):
    print(f"\n{'─' * 50}")
    print(f"Test : {description_test}")
    print(f"Note envoyée : {note_proposee}")
    
    url = f"{BASE_URL}/reclamations/{DEMANDE_ID}/analyser"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "acceptee": True,
        "commentaire": "Test API de validation de note"
    }
    if note_proposee is not None:
        payload["nouvelleNoteProposee"] = note_proposee
    
    response = requests.put(url, params=payload, headers=headers)
    status = response.status_code
    
    print(f"Code HTTP reçu : {status}")
    
    if attendu_ok:
        if status == 200:
            print("[✔] SUCCÈS : La note a été acceptée comme prévu (200 OK)")
            # On remet la demande à l'état précédent pour les autres tests
            reset_payload = {"acceptee": True, "commentaire": "Reset", "nouvelleNoteProposee": 12.0}
            requests.put(url, params=reset_payload, headers=headers)
            return True
        else:
            print(f"[✖] ÉCHEC : La note devait être acceptée, mais on a eu {status}")
            print("Message :", response.json().get('message', ''))
            return False
    else:
        if status == 400: # 400 Bad Request attendu pour une erreur de validation
            message = response.json().get('message', '')
            print(f"[✔] SUCCÈS : La note a été rejetée comme prévu (400 Bad Request)")
            print(f"    Message d'erreur du backend : '{message}'")
            return True
        else:
            print(f"[✖] ÉCHEC : La note devait être rejetée (400), mais on a eu {status}")
            if status != 500:
                 print("Message :", response.json().get('message', ''))
            return False


if __name__ == "__main__":
    print("================================================================")
    print(" Lancement des tests de validation de note (API REST - Python) ")
    print("================================================================")
    
    token = get_auth_token()
    tests_reussis = 0
    total_tests = 4
    
    # 1. Test : Note > 20
    if tester_note(token, 25.0, "Tentative d'envoyer 25/20", attendu_ok=False): tests_reussis += 1
    
    # 2. Test : Note < 0
    if tester_note(token, -2.0, "Tentative d'envoyer -2/20", attendu_ok=False): tests_reussis += 1
        
    # 3. Test : Note NULL (autorisée seulement si refus)
    if tester_note(token, None, "Tentative d'accepter sans mettre de note (NULL)", attendu_ok=False): tests_reussis += 1
        
    # 4. Test : Note valide (0-20)
    if tester_note(token, 18.5, "Tentative d'envoyer une note valide (18.5/20)", attendu_ok=True): tests_reussis += 1

    print("\n================================================================")
    print(f" Bilan : {tests_reussis}/{total_tests} tests sont passés avec succès.")
    if tests_reussis == total_tests:
        print(" [✔] L'API REST est robuste face aux saisies invalides.")
    else:
        print(" [✖] Il y a eu des échecs (regarder les logs ci-dessus).")
    print("================================================================")
