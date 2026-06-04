---
name: Java Project Intake Template
version: 2.0
description: >
  Q&A intake form for new Java projects. The agent fills this in based on user
  responses before generating any code. Covers environment, architecture, stack,
  and conventions.
applies_to: [java, spring-boot]
---

# Java Project Intake Form

> **Agent Instructions:** Present these questions to the user in groups of 3–4.
> Wait for answers before asking the next group.
> Fill in this template as answers arrive, then confirm the summary before coding.

---

## GROUP 1 — Environment Check

Ask the user to run these commands and share the output:

```bash
java -version
mvn -version      # OR: gradle -version
```

| Question | Answer |
|----------|--------|
| Q1. What Java version is installed? | __________ |
| Q2. Build tool (Maven or Gradle)? | __________ |
| Q3. Build tool version? | __________ |

**Agent Decision Table — Java Version:**

| Installed | Features Available | Features NOT Available |
|-----------|-------------------|----------------------|
| Java 11 | `var`, HTTP Client, Optionals | Records, Sealed classes, Pattern matching |
| Java 17 (LTS) | Records, Sealed classes, Text blocks | Pattern matching for switch (preview) |
| Java 21 (LTS) | All above + Virtual threads (Project Loom), Pattern matching, SequencedCollections | — |
| Java 23+ | All above + Unnamed classes (preview) | — |

---

## GROUP 2 — Project Identity

| Question | Answer |
|----------|--------|
| Q4. Project name? (e.g. `order-service`) | __________ |
| Q5. Base Java package? (e.g. `com.acme.orders`) | __________ |
| Q6. Short description — what does this service do? | __________ |
| Q7. Project type? | `[ ]` REST API  `[ ]` Microservice  `[ ]` Batch Job  `[ ]` Library  `[ ]` Monolith |

---

## GROUP 3 — Framework & Spring

| Question | Answer |
|----------|--------|
| Q8. Using Spring Boot? | `[ ]` Yes  `[ ]` No (plain Java) |
| Q9. If yes — Spring Boot version? | __________ |
| Q10. Spring modules needed? | `[ ]` Web  `[ ]` Data JPA  `[ ]` Security  `[ ]` Actuator  `[ ]` Kafka  `[ ]` Cache `[ ]` Batch |
| Q11. Embedded server preference? | `[ ]` Tomcat (default)  `[ ]` Undertow  `[ ]` Netty (reactive) |

**Agent Decision Table — Spring Boot Version:**

| Version | Key Difference |
|---------|---------------|
| 2.7.x | Java EE APIs (`javax.*`), Spring Security 5, Hibernate 5 |
| 3.0.x | Jakarta EE (`jakarta.*`) — BREAKING change from 2.x. Spring Security 6. Requires Java 17+ |
| 3.2.x | Virtual thread support, RestClient (replacement for RestTemplate), improved observability |
| 3.3.x+ | CDS (Class Data Sharing) improvements, Spring AI integration ready |

> **Note:** If the user is on Spring Boot 3.x, import packages from `jakarta.*`, NOT `javax.*`.

---

## GROUP 4 — Database

| Question | Answer |
|----------|--------|
| Q12. Database type? | `[ ]` PostgreSQL  `[ ]` MySQL  `[ ]` MS SQL Server  `[ ]` H2 (in-memory)  `[ ]` MongoDB  `[ ]` None |
| Q13. ORM / access layer? | `[ ]` Spring Data JPA  `[ ]` Spring Data JDBC  `[ ]` JOOQ  `[ ]` Plain JDBC  `[ ]` None |
| Q14. Database migrations? | `[ ]` Flyway  `[ ]` Liquibase  `[ ]` None |
| Q15. Multiple datasources? | `[ ]` Yes  `[ ]` No |

---

## GROUP 5 — Security & Auth

| Question | Answer |
|----------|--------|
| Q16. Authentication required? | `[ ]` Yes  `[ ]` No |
| Q17. Auth type? | `[ ]` JWT  `[ ]` OAuth2 / OpenID Connect  `[ ]` Basic Auth  `[ ]` API Key  `[ ]` Session-based |
| Q18. Using Spring Security? | `[ ]` Yes  `[ ]` No |
| Q19. Role-based access control (RBAC)? | `[ ]` Yes  `[ ]` No |

---

## GROUP 6 — Testing

| Question | Answer |
|----------|--------|
| Q20. Test framework? | `[ ]` JUnit 5 (default)  `[ ]` TestNG |
| Q21. Mocking library? | `[ ]` Mockito (default)  `[ ]` EasyMock |
| Q22. Integration tests with real DB? | `[ ]` Yes — Testcontainers  `[ ]` Yes — H2 in-memory  `[ ]` No |
| Q23. Code coverage target? | `[ ]` 70%+  `[ ]` 80%+  `[ ]` Best-effort |

---

## GROUP 7 — Additional Libraries

| Question | Answer |
|----------|--------|
| Q24. Using Lombok? | `[ ]` Yes  `[ ]` No |
| Q25. Using MapStruct (DTO mapping)? | `[ ]` Yes  `[ ]` No |
| Q26. API documentation? | `[ ]` OpenAPI / Swagger  `[ ]` None |
| Q27. Logging format? | `[ ]` JSON (structured)  `[ ]` Plain text |
| Q28. Any messaging? | `[ ]` Kafka  `[ ]` RabbitMQ  `[ ]` SQS  `[ ]` None |
| Q29. Caching? | `[ ]` Caffeine  `[ ]` Redis  `[ ]` None |

---

## GROUP 8 — Code Style Preferences

| Question | Answer |
|----------|--------|
| Q30. Prefer Lombok annotations? | `[ ]` Yes — use `@Data`, `@Builder` etc.  `[ ]` No — write manually |
| Q31. Immutability preference? | `[ ]` Use Java `record` types for DTOs  `[ ]` Use regular classes |
| Q32. Exception style? | `[ ]` Checked exceptions for business errors  `[ ]` Unchecked only |
| Q33. API versioning? | `[ ]` URL path (`/api/v1/`)  `[ ]` Header  `[ ]` None |

---

## COMPLETED INTAKE SUMMARY

> **Agent:** Once all groups are filled in, present this summary and ask for confirmation before writing any code.

```
╔══════════════════════════════════════════════════════════╗
║            JAVA PROJECT CONFIGURATION SUMMARY            ║
╠══════════════════════════════════════════════════════════╣
║  Java Version:     ______   Build Tool:    ______        ║
║  Project Name:     ______   Base Package:  ______        ║
║  Spring Boot:      ______   Server:        ______        ║
║  Database:         ______   ORM:           ______        ║
║  Auth:             ______   Test DB:       ______        ║
║  Lombok:           ______   MapStruct:     ______        ║
╚══════════════════════════════════════════════════════════╝

Does this look right? Type YES to begin or correct any item.
```

---

## GENERATED PROJECT STRUCTURE

After confirmation, generate the following starter structure. Fill in `{base}` with the confirmed base package (e.g. `com.acme.orders`).

```
{project-name}/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── {base}/
│   │   │       ├── {ProjectName}Application.java   ← main entry point
│   │   │       ├── controller/                     ← REST controllers
│   │   │       ├── service/                        ← business logic interfaces + implementations
│   │   │       │   └── impl/
│   │   │       ├── repository/                     ← Spring Data repositories
│   │   │       ├── model/
│   │   │       │   ├── entity/                     ← JPA / database entities
│   │   │       │   ├── dto/                        ← request & response DTOs
│   │   │       │   └── enums/                      ← status codes, categories
│   │   │       ├── exception/                      ← custom exceptions + global handler
│   │   │       ├── config/                         ← Spring @Configuration classes
│   │   │       └── util/                           ← shared utility classes
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       └── application-prod.yml
│   └── test/
│       └── java/
│           └── {base}/
│               ├── controller/                     ← @WebMvcTest / @SpringBootTest tests
│               ├── service/                        ← unit tests with Mockito
│               └── repository/                     ← @DataJpaTest / Testcontainers tests
├── pom.xml (or build.gradle)
└── README.md
```

---

## SPRING BOOT 3.x CHECKLIST (if applicable)

When Spring Boot 3.x is confirmed, apply these guidelines automatically:

- [ ] All imports use `jakarta.*` — not `javax.*`
- [ ] Spring Security 6: `SecurityFilterChain` bean replaces `WebSecurityConfigurerAdapter`
- [ ] `HttpSecurity` uses lambda DSL: `.authorizeHttpRequests(auth -> auth...)`
- [ ] `spring.jpa.open-in-view=false` in `application.yml` (performance best practice)
- [ ] Use `RestClient` instead of deprecated `RestTemplate` for outbound HTTP
- [ ] Use `@SpringBootTest` with `webEnvironment = RANDOM_PORT` for integration tests
- [ ] Enable virtual threads (Java 21 + Spring Boot 3.2+): `spring.threads.virtual.enabled=true`
- [ ] Use `Problem Details` (RFC 9457) for error responses: `spring.mvc.problemdetails.enabled=true`
