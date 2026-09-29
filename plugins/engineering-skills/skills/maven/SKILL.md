---
name: maven
description: Creating or fixing a Maven build, adding a module, resolving a dependency conflict, or wiring Maven into CI — `implementer:build`, `implementer:pipeline`
---

# Maven Skill — v1.0

## Quick Card

> Read this card first. Load a section below only when the task needs it.

| | |
|---|---|
| **Use when** | Creating or fixing a Maven build, adding a module, resolving a dependency conflict, or wiring Maven into CI — `implementer:build`, `implementer:pipeline` |
| **Skip when** | Gradle project — the principles hold, the syntax does not |
| **Inputs** | JDK version, framework (Spring Boot or none), module list, artifact repository (Maven Central or a corporate mirror) |
| **Produces** | Parent `pom.xml`, module POMs, `.mvn/maven.config`, Maven Wrapper, CI command |
| **Steps** | 1. Parent POM owns versions (§2) → 2. Import the framework BOM → 3. Pin every plugin (§3) → 4. Enforcer rules (§4) → 5. Tests + coverage (§5) → 6. Wrapper + CI (§6) → 7. Diagnose conflicts with the tree (§7) |
| **Done when** | `./mvnw verify` passes from a clean checkout; Enforcer passes; no version appears in a module POM |
| **Senior defaults** | Versions only in the parent's `dependencyManagement` / `pluginManagement` · import a BOM, never hand-pick Spring or Jackson versions · pin **every** plugin, including clean/install/deploy/site · `dependencyConvergence` fails the build instead of "nearest wins" guessing · never version ranges · `project.build.outputTimestamp` for reproducible jars · credentials in `settings.xml`, never in a POM |
| **Load on demand** | §1 layout · §2 parent POM · §3 plugins · §4 enforcer · §5 tests and coverage · §6 wrapper and CI · §7 conflicts · §8 repositories and security · §9 release |
| **Run report** | `html_report_skill` — adds: Plugin versions · Enforcer results · Dependency changes |
| **Pairs with** | `java_advanced_skill`, `spring_advanced_skill`, `test_skill`, `project_setup_skill`, `security_audit_skill` (dependency CVEs) |

---

## 1. Layout

```text
orders/
├── pom.xml                  ← parent: packaging pom, versions, plugins, rules
├── mvnw, mvnw.cmd           ← wrapper — commit these
├── .mvn/
│   ├── maven.config         ← default flags for every invocation
│   └── wrapper/maven-wrapper.properties
├── core/pom.xml             ← domain code, no framework
└── app/pom.xml              ← depends on core; Spring Boot lives here
```

One reactor, one version for all modules. A module POM names its parent, its
`artifactId`, and dependencies **without versions**.

## 2. The Parent POM

This is the exact POM that built the example project: two modules, three unit
tests, one integration test, coverage gate met, Enforcer passing, SBOM written.
Versions were the newest stable releases on Maven Central on 2026-09-28 —
check again before copying (`./mvnw versions:display-plugin-updates`).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.example</groupId>
  <artifactId>orders-parent</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <packaging>pom</packaging>

  <modules>
    <module>core</module>
    <module>app</module>
  </modules>

  <properties>
    <java.version>21</java.version>
    <maven.compiler.release>${java.version}</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <!-- reproducible builds: fixed timestamp in every jar -->
    <project.build.outputTimestamp>2026-09-28T00:00:00Z</project.build.outputTimestamp>
    <spring-boot.version>4.1.1</spring-boot.version>
    <jacoco.minimum.line.coverage>0.80</jacoco.minimum.line.coverage>
  </properties>

  <!-- Versions live here and only here. Modules declare dependencies without versions. -->
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>${spring-boot.version}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
      <dependency>
        <groupId>com.example</groupId>
        <artifactId>orders-core</artifactId>
        <version>${project.version}</version>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <build>
    <pluginManagement>
      <plugins>
        <!-- Default-lifecycle plugins: pin them too, or requirePluginVersions fails
             and builds silently change when Maven itself is upgraded -->
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-clean-plugin</artifactId>
          <version>3.5.0</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-resources-plugin</artifactId>
          <version>3.5.0</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-jar-plugin</artifactId>
          <version>3.5.1</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-install-plugin</artifactId>
          <version>3.2.0</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-deploy-plugin</artifactId>
          <version>3.2.0</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-site-plugin</artifactId>
          <version>3.22.0</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-compiler-plugin</artifactId>
          <version>3.16.0</version>
          <configuration>
            <parameters>true</parameters>
            <compilerArgs>
              <arg>-Xlint:all</arg>
            </compilerArgs>
          </configuration>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-surefire-plugin</artifactId>
          <version>3.6.0</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-failsafe-plugin</artifactId>
          <version>3.6.0</version>
        </plugin>
        <plugin>
          <groupId>org.jacoco</groupId>
          <artifactId>jacoco-maven-plugin</artifactId>
          <version>0.8.15</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-enforcer-plugin</artifactId>
          <version>3.6.3</version>
        </plugin>
        <plugin>
          <groupId>com.diffplug.spotless</groupId>
          <artifactId>spotless-maven-plugin</artifactId>
          <version>3.10.3</version>
        </plugin>
        <plugin>
          <groupId>org.codehaus.mojo</groupId>
          <artifactId>versions-maven-plugin</artifactId>
          <version>2.22.0</version>
        </plugin>
        <plugin>
          <groupId>org.cyclonedx</groupId>
          <artifactId>cyclonedx-maven-plugin</artifactId>
          <version>2.9.3</version>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-dependency-plugin</artifactId>
          <version>3.11.0</version>
        </plugin>
      </plugins>
    </pluginManagement>

    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-enforcer-plugin</artifactId>
        <executions>
          <execution>
            <id>enforce</id>
            <goals><goal>enforce</goal></goals>
            <configuration>
              <rules>
                <requireMavenVersion><version>[3.9.0,)</version></requireMavenVersion>
                <requireJavaVersion><version>[${java.version},)</version></requireJavaVersion>
                <dependencyConvergence/>
                <banDuplicatePomDependencyVersions/>
                <requirePluginVersions/>
              </rules>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>com.diffplug.spotless</groupId>
        <artifactId>spotless-maven-plugin</artifactId>
        <configuration>
          <java>
            <googleJavaFormat/>
            <removeUnusedImports/>
          </java>
        </configuration>
        <executions>
          <execution>
            <goals><goal>check</goal></goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-failsafe-plugin</artifactId>
        <executions>
          <execution>
            <goals>
              <goal>integration-test</goal>
              <goal>verify</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.jacoco</groupId>
        <artifactId>jacoco-maven-plugin</artifactId>
        <executions>
          <execution>
            <id>prepare-agent</id>
            <goals><goal>prepare-agent</goal></goals>
          </execution>
          <execution>
            <id>report</id>
            <goals><goal>report</goal></goals>
          </execution>
          <execution>
            <id>check</id>
            <goals><goal>check</goal></goals>
            <configuration>
              <rules>
                <rule>
                  <element>BUNDLE</element>
                  <limits>
                    <limit>
                      <counter>LINE</counter>
                      <value>COVEREDRATIO</value>
                      <minimum>${jacoco.minimum.line.coverage}</minimum>
                    </limit>
                  </limits>
                </rule>
              </rules>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.cyclonedx</groupId>
        <artifactId>cyclonedx-maven-plugin</artifactId>
        <executions>
          <execution>
            <phase>package</phase>
            <goals><goal>makeAggregateBom</goal></goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</project>
```

A module then needs nothing but coordinates:

```xml
<parent>
  <groupId>com.example</groupId>
  <artifactId>orders-parent</artifactId>
  <version>1.0.0-SNAPSHOT</version>
</parent>
<artifactId>orders-app</artifactId>

<dependencies>
  <dependency>
    <groupId>com.example</groupId>
    <artifactId>orders-core</artifactId>
  </dependency>
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>
```

**BOM import vs. `spring-boot-starter-parent`.** Inheriting the Boot parent is
fine for a single-module app. For a multi-module build with its own parent,
import `spring-boot-dependencies` as above — a project has only one parent,
and it should be yours.

## 3. Plugins — Pin Every One

`requirePluginVersions` fails the build until every plugin has a version,
including the ones Maven binds by default. On the example it failed first on
`maven-clean-plugin`, `maven-install-plugin`, `maven-site-plugin` and
`maven-deploy-plugin` — which were running whatever Maven 3.9.16 ships. Unpinned,
they change the day someone upgrades Maven.

| Plugin | Job |
|---|---|
| `maven-compiler-plugin` | `maven.compiler.release` (not `source`/`target` — `release` also checks the API), `-parameters`, `-Xlint:all` |
| `maven-surefire-plugin` | Unit tests: `*Test.java` in `test` |
| `maven-failsafe-plugin` | Integration tests: `*IT.java` in `integration-test`, failures reported in `verify` so cleanup still runs |
| `jacoco-maven-plugin` | Coverage; `check` fails below the floor |
| `maven-enforcer-plugin` | Build rules, §4 |
| `spotless-maven-plugin` | Formatting: `check` in CI, `apply` locally |
| `cyclonedx-maven-plugin` | SBOM (`target/bom.json`) for supply-chain scanning |
| `versions-maven-plugin` | `display-dependency-updates`, `display-plugin-updates` |

## 4. Enforcer Rules

| Rule | Catches |
|---|---|
| `requireMavenVersion` / `requireJavaVersion` | "Works on my machine" toolchains |
| `dependencyConvergence` | Two versions of one artifact in the tree, where Maven would silently pick the nearest |
| `banDuplicatePomDependencyVersions` | The same dependency declared twice in one POM |
| `requirePluginVersions` | Any unpinned plugin, including default-lifecycle ones |

Verified on the example: adding `org.reflections:reflections:0.10.2` (which
brings `javassist` 3.28.0-GA) next to a direct `javassist` 3.30.2-GA failed
the build:

```text
Rule 2: org.apache.maven.enforcer.rules.dependency.DependencyConvergence failed with message:
Dependency convergence error for org.javassist:javassist:jar:3.28.0-GA. Paths to dependency are:
    +-org.javassist:javassist:jar:3.28.0-GA:compile
  +-org.javassist:javassist:jar:3.30.2-GA:compile
```

Fixed by managing the version once in the parent — the rule passed:

```xml
<dependencyManagement>
  <dependencies>
    <!-- reflections pulls 3.28.0-GA; one version for the whole build -->
    <dependency>
      <groupId>org.javassist</groupId>
      <artifactId>javassist</artifactId>
      <version>3.30.2-GA</version>
    </dependency>
  </dependencies>
</dependencyManagement>
```

## 5. Tests and Coverage

- **The coverage floor is the project's, not this file's.** Set `jacoco.minimum.line.coverage` to the floor in `docs/project-setup/rules.md` (`project_setup_skill` §5 suggests 90%). The example's 0.80 is what that example project used.
- **Unit tests** end in `Test` → Surefire, `test` phase. **Integration tests** end in `IT` → Failsafe, `integration-test` + `verify`.
- `jacoco:prepare-agent` sets `argLine`; Surefire **and** Failsafe both use it, so coverage from integration tests counts. On the example, the `app` module has only an `IT` and still met its coverage gate.
- **If you set your own `argLine`, write `<argLine>@{argLine} -Xmx1g</argLine>`.** Verified on the example: a plain `<argLine>-Xmx512m</argLine>` dropped the JaCoCo agent, JaCoCo logged `Skipping JaCoCo execution due to missing execution data file`, and the build still ended in `BUILD SUCCESS` — the coverage gate never ran. With `@{argLine}` the gate ran and passed.
- A module with no tests at all prints `Skipping JaCoCo execution due to missing execution data file` and passes — the gate cannot see what never ran. Every module with code needs tests.
- Testcontainers-based tests belong in `*IT` classes: they need Docker and are slow.

## 6. Wrapper and CI

```bash
mvn -N wrapper:wrapper -Dmaven=3.9.16   # writes mvnw, mvnw.cmd, .mvn/wrapper/ — commit them
```

`.mvn/maven.config` — flags every invocation gets:

```text
-B
-ntp
```

(`-B` batch mode, `-ntp` no transfer progress — keeps CI logs readable.)

CI runs one command:

```bash
./mvnw verify
```

`verify`, not `install`: nothing needs to land in `~/.m2`. Cache `~/.m2/repository`
keyed on the hash of all `pom.xml` files. Use `-T 1C` for parallel module builds
once the build is known to be thread-safe.

## 7. Dependency Conflicts

```bash
./mvnw dependency:tree -Dincludes=org.javassist        # who brings it in
./mvnw dependency:tree -Dverbose                       # shows omitted-for-conflict versions
./mvnw dependency:analyze                              # used-undeclared and declared-unused
./mvnw versions:display-dependency-updates             # what is out of date
```

| Symptom | Cause | Fix |
|---|---|---|
| `NoSuchMethodError` / `ClassNotFoundException` at runtime | Two versions in the tree; the older one won | Pin in `dependencyManagement`; `dependencyConvergence` prevents recurrence |
| Enforcer convergence failure after adding a library | Library needs a different version of a shared dependency | Manage the version in the parent; exclude only when the library works with yours |
| `dependency:analyze` lists used-undeclared | Code compiles against a transitive dependency | Declare it — the transitive can disappear on any upgrade |
| Build differs between machines | Unpinned plugin, `SNAPSHOT` dependency, or version range | Pin; release snapshots; never `[1.0,)` |

`<exclusions>` is a last resort — document why on the exclusion.

## 8. Repositories and Security

- **Credentials live in `~/.m2/settings.xml`** (`<servers>`), referenced by `id` — never in a POM, never in the repository. In CI, generate `settings.xml` from secrets.
- **Corporate mirror**: one `<mirror>` with `<mirrorOf>*</mirrorOf>` in `settings.xml`, so every artifact goes through the proxy.
- **No `http://` repositories** — Maven 3.8.1+ blocks them by default for a reason.
- **Scan dependencies**: feed `target/bom.json` to a scanner, or run `org.owasp:dependency-check-maven` in a scheduled job — it is slow on the first run.
- **Scopes**: `provided` for container-supplied APIs, `test` for test-only, `runtime` for drivers; `optional` only in libraries.

## 9. Releasing

- Versions: `1.4.0-SNAPSHOT` during development, `1.4.0` for the release.
  `./mvnw versions:set -DnewVersion=1.4.0 -DgenerateBackupPoms=false` sets every module at once.
- Tag, build from the tag, `./mvnw deploy` with release credentials.
- `project.build.outputTimestamp` makes jars byte-identical across rebuilds —
  set it to the release commit's timestamp when releasing.

## 10. Checklist

✅ Maven Wrapper committed; CI runs `./mvnw verify`
✅ All versions in the parent's `dependencyManagement` / `pluginManagement`; none in modules
✅ Framework BOM imported
✅ Every plugin pinned, including clean, resources, jar, install, deploy, site
✅ Enforcer: Maven and Java versions, dependency convergence, duplicate declarations, plugin versions
✅ Unit tests in Surefire, `*IT` in Failsafe; coverage gate on both
✅ Formatter check in CI
✅ SBOM generated; dependencies scanned
✅ No credentials, `http://` repositories, version ranges, or snapshots in a release
✅ `project.build.outputTimestamp` set
