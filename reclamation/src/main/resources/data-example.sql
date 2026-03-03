-- Exemple de données pour le système de réclamation IBAM
-- Mot de passe en clair pour les comptes de test: password123
-- Hash BCrypt généré: $2a$10$0Dtof0DqwdU9Ndmmz/Ethuc5.5fcl8OodJ3qsz0BROIQVjlxcIPbi

INSERT INTO app_users (nom, prenom, email, password_hash, role, niveau, filiere) VALUES
('Dupont', 'Jean', 'jean.dupont@ibam.ma', '$2a$10$0Dtof0DqwdU9Ndmmz/Ethuc5.5fcl8OodJ3qsz0BROIQVjlxcIPbi', 'ROLE_ETUDIANT', 'L3', 'MIAGE'),
('Martin', 'Marie', 'marie.martin@ibam.ma', '$2a$10$0Dtof0DqwdU9Ndmmz/Ethuc5.5fcl8OodJ3qsz0BROIQVjlxcIPbi', 'ROLE_ETUDIANT', 'L2', 'CCA'),
('Traore', 'Yaya', 'yaya.traore@ibam.ma', '$2a$10$0Dtof0DqwdU9Ndmmz/Ethuc5.5fcl8OodJ3qsz0BROIQVjlxcIPbi', 'ROLE_ENSEIGNANT', NULL, NULL),
('Tazi', 'Omar', 'omar.tazi@ibam.ma', '$2a$10$0Dtof0DqwdU9Ndmmz/Ethuc5.5fcl8OodJ3qsz0BROIQVjlxcIPbi', 'ROLE_SCOLARITE', NULL, NULL),
('Bennani', 'Rachid', 'rachid.bennani@ibam.ma', '$2a$10$0Dtof0DqwdU9Ndmmz/Ethuc5.5fcl8OodJ3qsz0BROIQVjlxcIPbi', 'ROLE_DA', NULL, NULL);

INSERT INTO matieres (nom, code, description) VALUES
('Comptabilité Générale', 'CG101', 'Principes de base de la comptabilité'),
('Systèmes d''Information', 'SI201', 'Analyse et conception de SI'),
('Techniques de Compilation', 'TC301', 'Compilation et analyse lexicale/syntaxique');

INSERT INTO enseignements (enseignant_id, matiere_id, filiere, niveau, semestre, annee_academique) VALUES
(3, 2, 'MIAGE', 'L3', 'S5', '2023-2024'),
(3, 3, 'MIAGE', 'L3', 'S5', '2023-2024');

INSERT INTO notes (etudiant_id, enseignement_id, valeur) VALUES
(1, 1, 12.5),
(1, 2, 16.5);

INSERT INTO periodes_reclamation (nom, date_debut, date_fin, active, createur_id, description, date_creation) VALUES
('Réclamations Semestre 1 - 2024', '2024-01-15 08:00:00', '2024-01-18 17:00:00', true, 5, 'Période de réclamation pour les notes du premier semestre', CURRENT_TIMESTAMP);
