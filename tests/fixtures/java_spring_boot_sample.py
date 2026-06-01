"""Test fixtures for Java Spring Boot sample projects."""

from pathlib import Path
import tempfile
from typing import Optional


class JavaSpringBootSample:
    """Generate sample Java Spring Boot project for testing."""

    @staticmethod
    def create_sample_project(
        tmpdir: Optional[Path] = None, with_tests: bool = True
    ) -> Path:
        """
        Create a sample Java Spring Boot project.

        Args:
            tmpdir: Base directory (uses temp if None)
            with_tests: Include test files

        Returns:
            Path to project root
        """
        if tmpdir is None:
            tmpdir = Path(tempfile.mkdtemp())

        # Create directory structure
        src = tmpdir / "src" / "main" / "java" / "com" / "example" / "app"
        src.mkdir(parents=True, exist_ok=True)

        test = tmpdir / "src" / "test" / "java" / "com" / "example" / "app"
        if with_tests:
            test.mkdir(parents=True, exist_ok=True)

        resources = tmpdir / "src" / "main" / "resources"
        resources.mkdir(parents=True, exist_ok=True)

        # Main application class
        app_class = src / "Application.java"
        app_class.write_text(
            """package com.example.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
"""
        )

        # Service class
        service_class = src / "UserService.java"
        service_class.write_text(
            """package com.example.app;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;

    public User getUserById(Long id) {
        return userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
    }

    public User createUser(UserRequest request) {
        User user = new User();
        user.setName(request.getName());
        user.setEmail(request.getEmail());
        return userRepository.save(user);
    }
}
"""
        )

        # Repository interface
        repo_class = src / "UserRepository.java"
        repo_class.write_text(
            """package com.example.app;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}
"""
        )

        # Entity class
        entity_class = src / "User.java"
        entity_class.write_text(
            """package com.example.app;

import javax.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(unique = true, nullable = false)
    private String email;

    // Getters and setters...
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
}
"""
        )

        # Controller class
        controller_class = src / "UserController.java"
        controller_class.write_text(
            """package com.example.app;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;

@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;

    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.getUserById(id);
    }

    @PostMapping
    public User createUser(@RequestBody UserRequest request) {
        return userService.createUser(request);
    }
}
"""
        )

        # Exception class
        exception_class = src / "UserNotFoundException.java"
        exception_class.write_text(
            """package com.example.app;

public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(Long id) {
        super("User not found: " + id);
    }
}
"""
        )

        # Request DTO
        request_class = src / "UserRequest.java"
        request_class.write_text(
            """package com.example.app;

public class UserRequest {
    private String name;
    private String email;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
}
"""
        )

        # Test files
        if with_tests:
            service_test = test / "UserServiceTest.java"
            service_test.write_text(
                """package com.example.app;

import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class UserServiceTest {
    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    public void givenValidId_whenGetUser_thenReturnUser() {
        User user = new User();
        user.setId(1L);
        user.setName("Test User");

        when(userRepository.findById(1L))
            .thenReturn(java.util.Optional.of(user));

        User result = userService.getUserById(1L);

        assertNotNull(result);
        assertEquals("Test User", result.getName());
    }
}
"""
            )

            controller_test = test / "UserControllerTest.java"
            controller_test.write_text(
                """package com.example.app;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.mockito.Mockito.*;

@WebMvcTest(UserController.class)
public class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    public void givenValidId_whenGetUser_thenReturn200() throws Exception {
        User user = new User();
        user.setId(1L);
        user.setName("Test");

        when(userService.getUserById(1L)).thenReturn(user);

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk());
    }
}
"""
            )

        # POM file
        pom_file = tmpdir / "pom.xml"
        pom_file.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>spring-boot-app</artifactId>
    <version>1.0.0</version>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.1.0</version>
    </parent>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
"""
        )

        return tmpdir
