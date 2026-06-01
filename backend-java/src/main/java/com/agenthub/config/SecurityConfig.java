package com.agenthub.config;

import org.springframework.context.annotation.Configuration;

@Configuration
public class SecurityConfig {

    /*
     * MVP: spring-boot-starter-security is NOT in pom.xml, all requests are open by default.
     * P1:  Add spring-boot-starter-security dependency, then uncomment below:
     *
     * ---------------------------------------------------------------------------
     * P1 Activation Steps:
     * 1. Add to pom.xml:
     *    <dependency>
     *        <groupId>org.springframework.boot</groupId>
     *        <artifactId>spring-boot-starter-security</artifactId>
     *    </dependency>
     * 2. Create JwtAuthenticationFilter extends OncePerRequestFilter
     * 3. Uncomment the beans below
     * 4. Add JWT secret to application.yml
     * ---------------------------------------------------------------------------
     *
     * @Bean
     * public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
     *     http
     *         .csrf(csrf -> csrf.disable())
     *         .sessionManagement(session -> session.sessionCreationPolicy(STATELESS))
     *         .authorizeHttpRequests(auth -> auth
     *             .requestMatchers("/ws/**", "/h2-console/**").permitAll()
     *             .anyRequest().authenticated()
     *         )
     *         .addFilterBefore(jwtAuthenticationFilter(), UsernamePasswordAuthenticationFilter.class);
     *     return http.build();
     * }
     *
     * @Bean
     * public JwtAuthenticationFilter jwtAuthenticationFilter() {
     *     return new JwtAuthenticationFilter();
     * }
     */
}
