package com.ibam.reclamation;

import com.ibam.reclamation.entity.*;
import com.ibam.reclamation.security.RoleEnum;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests unitaires PURS – aucun contexte Spring, aucune base de données.
 *
 * Objectif : vérifier que la méthode DemandeReclamation.analyser()
 * rejette toute « nouvelle note proposée » qui sort de l'intervalle [0, 20].
 *
 * Règle métier (DemandeReclamation.java ligne 147) :
 * Si la demande est acceptée ET que nouvelleNoteProposee < 0 ou > 20
 * → IllegalArgumentException("Une nouvelle note valide (0-20) est obligatoire
 * si acceptée")
 */
@DisplayName("Validation de la nouvelle note proposée par l'enseignant [0-20]")
class NoteInvalideValidationTest {

    private DemandeReclamation demande;
    private User etudiant;
    private User enseignant;
    private Note note;

    /**
     * Préparation d'une demande dans l'état IMPUTEE avant chaque test.
     * C'est le seul état qui permet d'appeler analyser().
     */
    @BeforeEach
    void setUp() {
        // ── Créer un étudiant ──
        etudiant = new User();
        etudiant.setId(1L);
        etudiant.setNom("Soulama");
        etudiant.setPrenom("Joel");
        etudiant.setEmail("joel.soulama@ibam.ma");
        etudiant.setPasswordHash("$2a$10$xxx");
        etudiant.setRole(RoleEnum.ROLE_ETUDIANT);
        etudiant.setNiveau(Niveau.L3);
        etudiant.setFiliere(Filiere.MIAGE);

        // ── Créer un enseignant ──
        enseignant = new User();
        enseignant.setId(2L);
        enseignant.setNom("Traore");
        enseignant.setPrenom("Yaya");
        enseignant.setEmail("yaya.traore@ibam.ma");
        enseignant.setPasswordHash("$2a$10$xxx");
        enseignant.setRole(RoleEnum.ROLE_ENSEIGNANT);

        // ── Créer une matière et un enseignement ──
        Matiere matiere = new Matiere();
        matiere.setId(1L);
        matiere.setCode("INFO301");
        matiere.setNom("Algorithmique");

        Enseignement enseignement = new Enseignement();
        enseignement.setId(1L);
        enseignement.setMatiere(matiere);
        enseignement.setEnseignant(enseignant);
        enseignement.setSemestre(Semestre.S1);

        // ── Créer une note initiale valide (12.0 / 20) ──
        note = new Note();
        note.setId(1L);
        note.setValeur(12.0);
        note.setEtudiant(etudiant);
        note.setEnseignement(enseignement);

        // ── Créer la demande et la faire passer jusqu'à l'état IMPUTEE ──
        demande = DemandeReclamation.soumettre(
                etudiant,
                note,
                "Je pense avoir une meilleure note.",
                "justificatif.pdf",
                "application/pdf",
                new byte[] { 1, 2, 3 });
        // Vérifier la recevabilité (SOUMISE → TRANSMISE_DA)
        demande.verifierRecevabilite(true, null);
        // Imputer à l'enseignant (TRANSMISE_DA → IMPUTEE)
        demande.imputer(enseignant);
    }

    // ═══════════════════════════════════════════════════════════════
    // CAS VALIDES : notes dans [0, 20] — doivent être acceptées
    // ═══════════════════════════════════════════════════════════════

    @Test
    @DisplayName("✔ Note valide : 15.0 / 20 doit être acceptée")
    void noteValide_15_doitEtreAcceptee() {
        assertDoesNotThrow(() -> demande.analyser(true, "Correction après vérification.", 15.0),
                "Une note de 15/20 est valide et doit être acceptée sans exception");
        assertEquals(StatutDemande.ACCEPTEE, demande.getStatut());
        assertEquals(15.0, demande.getNouvelleNoteProposee());
        System.out.println("[✔] Note 15/20 acceptée. Statut → ACCEPTEE");
    }

    @Test
    @DisplayName("✔ Note valide : 0.0 / 20 (limite basse) doit être acceptée")
    void noteValide_zero_doitEtreAcceptee() {
        assertDoesNotThrow(() -> demande.analyser(true, "Note minimale correcte.", 0.0),
                "Une note de 0.0 est la limite minimale valide");
        assertEquals(StatutDemande.ACCEPTEE, demande.getStatut());
        System.out.println("[✔] Note 0.0/20 (limite basse) acceptée. Statut → ACCEPTEE");
    }

    @Test
    @DisplayName("✔ Note valide : 20.0 / 20 (limite haute) doit être acceptée")
    void noteValide_vingt_doitEtreAcceptee() {
        assertDoesNotThrow(() -> demande.analyser(true, "Excellent travail confirmé.", 20.0),
                "Une note de 20.0 est la limite maximale valide");
        assertEquals(StatutDemande.ACCEPTEE, demande.getStatut());
        System.out.println("[✔] Note 20.0/20 (limite haute) acceptée. Statut → ACCEPTEE");
    }

    // ═══════════════════════════════════════════════════════════════
    // CAS INVALIDES : note > 20 (IMPOSSIBLE dans le système)
    // ═══════════════════════════════════════════════════════════════

    @Test
    @DisplayName("✖ Note invalide : 25.0 / 20 doit être rejetée (> 20)")
    void noteInvalide_25_doitLancerException() {
        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> demande.analyser(true, "Note trop haute.", 25.0),
                "Une note de 25/20 est impossible et doit lever IllegalArgumentException");
        System.out.println("[✔] Note 25/20 rejetée. Message : " + exception.getMessage());
        assertTrue(
                exception.getMessage().contains("0-20"),
                "Le message doit mentionner la plage valide '0-20'");
        // Vérifier que le statut n'a PAS changé (la demande reste IMPUTEE)
        assertEquals(StatutDemande.IMPUTEE, demande.getStatut(),
                "Le statut doit rester IMPUTEE si la validation échoue");
    }

    @Test
    @DisplayName("✖ Note invalide : 21.0 / 20 doit être rejetée (juste au-dessus de 20)")
    void noteInvalide_21_doitLancerException() {
        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> demande.analyser(true, "Dépasse légèrement.", 21.0),
                "Une note de 21/20 est hors plage et doit lever IllegalArgumentException");
        System.out.println("[✔] Note 21/20 rejetée. Message : " + exception.getMessage());
        assertEquals(StatutDemande.IMPUTEE, demande.getStatut());
    }

    @ParameterizedTest(name = "✖ Note {0} / 20 doit être rejetée (> 20)")
    @ValueSource(doubles = { 20.01, 21.0, 25.0, 100.0, 999.99, Double.MAX_VALUE })
    @DisplayName("✖ Toutes les notes supérieures à 20 doivent être rejetées")
    void toutesNotesSuperieures20_doiventEtreRejetees(double noteInvalide) {
        assertThrows(
                IllegalArgumentException.class,
                () -> demande.analyser(true, "Commentaire test.", noteInvalide),
                "Une note de " + noteInvalide + "/20 doit lever IllegalArgumentException");
        System.out.println("[✔] Note " + noteInvalide + "/20 rejetée correctement");
        assertEquals(StatutDemande.IMPUTEE, demande.getStatut());
    }

    // ═══════════════════════════════════════════════════════════════
    // CAS INVALIDES : note < 0 (IMPOSSIBLE dans le système)
    // ═══════════════════════════════════════════════════════════════

    @Test
    @DisplayName("✖ Note invalide : -2.0 / 20 doit être rejetée (< 0)")
    void noteInvalide_moins2_doitLancerException() {
        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class,
                () -> demande.analyser(true, "Note négative impossible.", -2.0),
                "Une note de -2/20 est impossible et doit lever IllegalArgumentException");
        System.out.println("[✔] Note -2/20 rejetée. Message : " + exception.getMessage());
        assertTrue(
                exception.getMessage().contains("0-20"),
                "Le message doit mentionner la plage valide '0-20'");
        assertEquals(StatutDemande.IMPUTEE, demande.getStatut());
    }

    @Test
    @DisplayName("✖ Note invalide : -0.01 / 20 doit être rejetée (juste en dessous de 0)")
    void noteInvalide_moinsPetit_doitLancerException() {
        assertThrows(
                IllegalArgumentException.class,
                () -> demande.analyser(true, "Légèrement négative.", -0.01),
                "Une note de -0.01/20 est hors plage et doit lever IllegalArgumentException");
        System.out.println("[✔] Note -0.01/20 rejetée correctement");
        assertEquals(StatutDemande.IMPUTEE, demande.getStatut());
    }

    @ParameterizedTest(name = "✖ Note {0} / 20 doit être rejetée (< 0)")
    @ValueSource(doubles = { -0.01, -1.0, -2.0, -10.0, -100.0, Double.MIN_VALUE * -1 })
    @DisplayName("✖ Toutes les notes négatives doivent être rejetées")
    void toutesNotesNegatives_doiventEtreRejetees(double noteInvalide) {
        assertThrows(
                IllegalArgumentException.class,
                () -> demande.analyser(true, "Commentaire test.", noteInvalide),
                "Une note de " + noteInvalide + "/20 doit lever IllegalArgumentException");
        System.out.println("[✔] Note " + noteInvalide + "/20 rejetée correctement");
        assertEquals(StatutDemande.IMPUTEE, demande.getStatut());
    }

    // ═══════════════════════════════════════════════════════════════
    // CAS PARTICULIER : note null quand la demande est acceptée
    // ═══════════════════════════════════════════════════════════════

    @Test
    @DisplayName("✖ Note null avec demande acceptée doit être rejetée")
    void noteNull_avecAcceptation_doitLancerException() {
        assertThrows(
                IllegalArgumentException.class,
                () -> demande.analyser(true, "Commentaire sans note.", null),
                "Une note null avec acceptee=true doit lever IllegalArgumentException");
        System.out.println("[✔] Note null rejetée quand acceptee=true");
        assertEquals(StatutDemande.IMPUTEE, demande.getStatut());
    }

    // ═══════════════════════════════════════════════════════════════
    // CAS PARTICULIER : note invalide mais demande REFUSÉE
    // → la note n'est pas utilisée donc pas de validation sur la valeur
    // ═══════════════════════════════════════════════════════════════

    @Test
    @DisplayName("✔ Note 25/20 ignorée si la demande est REFUSÉE (acceptee=false)")
    void noteInvalide_avecRefus_doitEtreIgnoree() {
        // Quand acceptee=false, la note n'est pas requise
        // → même une note "invalide" en valeur ne doit pas lever d'exception
        assertDoesNotThrow(() -> demande.analyser(false, "Réclamation non justifiée.", 25.0),
                "Quand acceptee=false, la valeur de la note n'est pas validée");
        assertEquals(StatutDemande.REFUSEE, demande.getStatut());
        System.out.println("[✔] Demande refusée avec note 25/20 passée en paramètre : OK (note non utilisée)");
    }
}
