package com.ibam.reclamation.service;

import com.ibam.reclamation.dto.LoginRequest;
import com.ibam.reclamation.dto.LoginResponse;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import com.ibam.reclamation.repository.UserRepository;
import com.ibam.reclamation.entity.User;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class AuthService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final Map<String, Integer> loginAttempts = new ConcurrentHashMap<>();

    public AuthService(UserRepository userRepository, 
                      PasswordEncoder passwordEncoder,
                      JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public LoginResponse authenticate(String email, String password) {
        // Vérifier si le compte est bloqué après 3 tentatives
        if (loginAttempts.getOrDefault(email, 0) >= 3) {
            throw new RuntimeException("Compte désactivé après 3 tentatives échouées");
        }
        
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("Utilisateur introuvable"));
        
        if (!passwordEncoder.matches(password, user.getPasswordHash())) {
            // Incrémenter le compteur d'échecs
            loginAttempts.put(email, loginAttempts.getOrDefault(email, 0) + 1);
            throw new RuntimeException("Mot de passe incorrect");
        }

        // Réinitialiser le compteur en cas de succès
        loginAttempts.remove(email);
        
        String token = jwtService.generateToken(user);
        String niveau = user.getNiveau() != null ? user.getNiveau().name() : null;
        String filiere = user.getFiliere() != null ? user.getFiliere().name() : null;
        
        return new LoginResponse(token, user.getRole().name(), niveau, filiere);
    }
    
    public void logout(String token) {
        throw new UnsupportedOperationException("Logout non encore implémenté");
    }
}