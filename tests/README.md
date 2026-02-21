# TP 2 – Tests Selenium – Plateforme Demande de Réclamation IBAM

## Prérequis

```bash
# 1. Installer Python 3.9+
# 2. Installer Selenium
pip install selenium

# 3. Vérifier votre version de Chrome
google-chrome --version

# 4. ChromeDriver doit correspondre à votre version Chrome
#    (Selenium >= 4.6 gère ça automatiquement via selenium-manager)
```

> Avant de lancer les tests, assurez-vous que :
> - Le **backend Spring Boot** tourne sur `localhost:8080`
> - Le **frontend Vite** tourne sur `localhost:3000` (`npm run dev` dans `/frontend`)

---

## Compte de test utilisé

| Champ    | Valeur                       |
|----------|------------------------------|
| Email    | `joel.soulama@ibam.ma`       |
| Password | `password123`                |
| Rôle     | Étudiant                     |

---

## Exercice 1 – Tests Fonctionnels

```bash
python tests/exercice1_test_fonctionnel.py
```

| Test | Description |
|------|-------------|
| `test_01_affichage_formulaire_connexion` | Page de connexion affichée avec le bon titre |
| `test_02_authentification_reussie` | Login valide → redirection dashboard |
| `test_03_deconnexion` | Logout → retour page connexion |
| `test_01_premiere_tentative_echouee` | Mauvais identifiants → message d'erreur |
| `test_02_deuxieme_tentative_echouee` | 2ème mauvais identifiants → message d'erreur |
| `test_03_troisieme_tentative_compte_desactive` | 3ème tentative → compte désactivé |

---

## Exercice 2 – Test de Charge

```bash
python tests/exercice2_test_charge.py
```

- **Phase 1** : 10 utilisateurs en parallèle → `resultats/charge_10_utilisateurs.csv`
- **Phase 2** : 100 utilisateurs en parallèle → `resultats/charge_100_utilisateurs.csv`
- **Phase 3** : 200 utilisateurs en parallèle → `resultats/charge_200_utilisateurs.csv`

**Format CSV** :

| Colonne | Description |
|---------|-------------|
| `utilisateur_id` | Numéro de l'utilisateur simulé |
| `telephone_ou_email` | Email/Numéro utilisé |
| `statut` | `SUCCÈS` ou `ÉCHEC` |
| `duree_secondes` | Durée totale de connexion en secondes |
| `message_erreur` | Message d'erreur si ÉCHEC |
| `timestamp` | Date/heure du test |

---

## Exercice 3 – Test de Performance

```bash
python tests/exercice3_test_performance.py
```

- **Phase 1** : 10 utilisateurs en parallèle → `resultats/perf_10_utilisateurs.csv`
- **Phase 2** : 100 utilisateurs en parallèle → `resultats/perf_100_utilisateurs.csv`
- **Phase 3** : 200 utilisateurs en parallèle → `resultats/perf_200_utilisateurs.csv`

**Format CSV** (métriques détaillées) :

| Colonne | Description |
|---------|-------------|
| `temps_chargement_page_s` | Temps de chargement de la page |
| `temps_saisie_s` | Temps de saisie du formulaire |
| `temps_reponse_serveur_s` | Temps de réponse du backend |
| `temps_total_s` | Durée totale |
| `conforme_seuils` | `OUI` si dans les seuils (page <3s, total <5s) |

---

## Exercice 6 – Tests Unitaires (Affichage de page)

```bash
python tests/exercice6_test_unitaire.py
```

| Test | Description |
|------|-------------|
| `test_01_titre_onglet_navigateur` | Titre onglet = "Logiciel de Réclamations" |
| `test_02_titre_formulaire_h1` | Titre H1 = "IBAM - Réclamations" ✅ (test principal Exo 6) |
| `test_03_presence_champ_email` | Champ email visible |
| `test_04_presence_champ_mot_de_passe` | Champ password visible |
| `test_05_presence_bouton_connexion` | Bouton submit visible et actif |
| `test_06_presence_label_email` | Label "Email" présent |
| `test_07_presence_label_mot_de_passe` | Label "Mot de passe" présent |
| `test_08_url_page_connexion` | URL correcte (pas de dashboard) |
| `test_09_structure_formulaire` | 2 champs + 1 bouton submit |

---

## Dossier des résultats

```
tests/
├── exercice1_test_fonctionnel.py
├── exercice2_test_charge.py
├── exercice3_test_performance.py
├── exercice6_test_unitaire.py
├── test_api_validation_note.py
├── README.md
└── resultats/                        ← Créé automatiquement
    ├── charge_10_utilisateurs.csv
    ├── charge_100_utilisateurs.csv
    ├── charge_200_utilisateurs.csv
    ├── perf_10_utilisateurs.csv
    ├── perf_100_utilisateurs.csv
    └── perf_200_utilisateurs.csv
```
