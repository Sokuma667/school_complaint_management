package com.ibam.reclamation.util;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

public class HashGen {

    public static void main(String[] args) {
        String password = args.length > 0 ? args[0] : "password123";
        BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
        String hash = encoder.encode(password);
        System.out.println("Password: " + password);
        System.out.println("BCrypt: " + hash);
    }
}
