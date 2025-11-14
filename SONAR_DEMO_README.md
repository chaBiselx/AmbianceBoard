# Démonstration SonarQube - Catalogue des Problèmes

Ce projet contient **volontairement** des problèmes de code pour démontrer les capacités de SonarQube.

⚠️ **ATTENTION**: Ce code ne doit JAMAIS être utilisé en production !

## Fichiers créés pour la démo

### 1. `security_vulnerabilities.py` - Failles de Sécurité

**20+ vulnérabilités de sécurité critiques** :

- **SQL Injection** : Requêtes SQL construites par concaténation
- **Hardcoded Credentials** : Mots de passe et clés API en dur
- **Weak Cryptography** : Utilisation de MD5 pour hasher des mots de passe
- **Command Injection** : Exécution de commandes shell avec input utilisateur
- **eval() / exec()** : Exécution de code dynamique dangereux
- **Pickle Deserialization** : Désérialisation non sécurisée
- **Path Traversal** : Accès fichiers sans validation du chemin
- **Weak Random** : random.randint() pour de la crypto
- **XSS** : Injection HTML sans échappement
- **LDAP Injection** : Requêtes LDAP non sécurisées
- **XXE Vulnerability** : Parsing XML vulnérable
- **Open Redirect** : Redirection sans validation
- **SSL Verification Disabled** : Désactivation de la vérification SSL
- **Insecure Cookies** : Cookies sans flags secure/httponly
- **Mass Assignment** : setattr() sans validation

### 2. `code_duplication_1.py` & `code_duplication_2.py` - Duplication de Code

**Duplications massives** :

- Même logique de calcul de prix répétée 3 fois
- Validation de mot de passe dupliquée 4 fois
- Code de connexion SMTP dupliqué

### 3. `high_complexity.py` - Complexité Cyclomatique

**Complexité cognitive > 150** :

- Fonction avec 50+ conditions if/else imbriquées
- 6 niveaux de boucles imbriquées
- Logique métier impossible à maintenir

### 4. `code_smells.py` - Code Smells & TODOs

**32+ code smells détectés** :

- TODOs et FIXMEs non résolus (15+)
- Variables inutilisées (unused_variable_1, unused_variable_2)
- Code mort (cleanup_old_users jamais appelée)
- Paramètres par défaut mutables (items=[])
- Fonctions avec 14 paramètres
- Bare except (catch sans type d'exception)
- Comparaison avec True/False explicite
- type() au lieu de isinstance()
- Magic numbers partout
- print() au lieu de logging
- Fichiers non fermés

### 5. `bugs_and_errors.py` - Bugs Potentiels

**40+ bugs potentiels** :

- Division par zéro
- Index out of range
- KeyError sur dictionnaire
- AttributeError (null pointer)
- Récursion sans condition d'arrêt
- Boucle infinie potentielle
- Arguments mutables par défaut
- Closure avec variable partagée
- Shadowing de built-ins (list, dict, str)
- Code inaccessible (unreachable)
- Assertion en production

### 6. `demo_sonar_issues.ts` - Problèmes TypeScript/JavaScript

**45+ problèmes JS/TS** :

- **Sécurité** : eval(), innerHTML, document.write()
- **Type any** utilisé partout
- **console.log()** en production
- Complexité élevée
- Code dupliqué
- Division par zéro
- Variables inutilisées
- Magic numbers
- 13 paramètres dans une fonction
- localStorage non chiffré
- == au lieu de ===
- Code mort (unreachable)
- Callback hell
- ReDoS vulnerability
- Promise sans .catch()
- parseInt() sans radix
- Hardcoded credentials

### 7. `more_sonar_issues.ts` - Plus de Problèmes JS

**35+ problèmes supplémentaires** :

- var au lieu de let/const
- Comparaison avec NaN
- Fonction trop longue (100+ lignes)
- setTimeout() avec string
- Nested ternaries
- postMessage sans validation d'origine
- new Function() (eval déguisé)
- Assignment dans condition
- Math.random() pour sécurité
- debugger; en production
- Empty catch blocks

### 8. `performance_issues.py` - Problèmes de Performance

**25+ anti-patterns de performance** :

- Algorithme O(n²) au lieu de O(n)
- Concaténation de strings dans boucle
- Regex recompilée à chaque itération
- Problème N+1 queries
- Pas de lazy loading (tout en mémoire)
- Calculs redondants dans boucle
- Import dans une boucle
- Deep copy inutile
- sleep() dans une boucle
- Pas de connection pool HTTP
- God Class (fait tout)
- Pas de cache/memoization
- Fonction avec 50+ lignes

### 9. `mixed_issues.py` - Problèmes Variés

**40+ problèmes mixtes** :

- Logging non configuré
- Exception handling incorrect
- Mauvais noms de variables (x, y, z)
- Shadow de built-ins
- Fichiers non fermés
- Trop de return statements
- type() au lieu de isinstance()
- 15 paramètres dans fonction
- Modification de variable globale
- Classe vide
- Try/except trop large
- Assert pour validation
- 8 boolean flags comme paramètres
- Silent failure (catch vide)
- Ternaires imbriqués
- Constants en minuscules
- Code commenté non supprimé
- Float comme clé de dict
- Styles de nommage incohérents

### 10. `legacy_issues.py` - Code Legacy & Dette Technique

**35+ problèmes legacy** :

- **CRITICAL** : yaml.load() sans Loader
- XXE vulnerability
- Pickle unsafe
- exec() et compile()
- Race conditions (TOCTOU)
- État global mutable
- Code non thread-safe
- Singleton anti-pattern
- Références circulaires (memory leak)
- God object
- Integer overflow potentiel
- Hardcoded IPs et credentials
- Path traversal
- Feature envy
- Train wreck (Law of Demeter)
- Shell injection
- Primitive obsession
- Shadow de built-ins (open, input)
- Anemic domain model
- pdb.set_trace() en prod
- Comparaison de floats
- Code déprécié

## Statistiques Attendues

Avec SonarQube, vous devriez voir :

- **Bugs** : 80+ détections
- **Vulnerabilities** : 50+ failles critiques/hautes
- **Code Smells** : 150+ problèmes
- **Security Hotspots** : 30+ à reviewer
- **Duplications** : 15-20% de code dupliqué
- **Complexité cyclomatique** : Plusieurs fonctions > 50
- **Dette technique** : Plusieurs jours/semaines
- **TODOs/FIXMEs** : 60+ commentaires

## Types de Problèmes par Catégorie

### 🔴 Critical Security Issues
- SQL Injection
- Command Injection
- eval()/exec()
- Hardcoded secrets
- Pickle deserialization
- YAML unsafe load
- XXE attacks

### 🟠 Major Security Issues
- Weak crypto (MD5)
- No SSL verification
- XSS vulnerabilities
- Path traversal
- Open redirect
- LDAP injection
- ReDoS

### 🟡 Code Quality Issues
- High complexity (>50)
- Code duplication (>10 lines)
- Too many parameters (>7)
- Too long functions (>50 lines)
- God classes
- Magic numbers

### 🔵 Maintainability Issues
- TODOs/FIXMEs
- Dead code
- Unused variables
- Poor naming
- No documentation
- Commented code

### 🟣 Performance Issues
- O(n²) algorithms
- N+1 queries
- No caching
- Unnecessary deep copy
- Import in loops
- String concatenation in loops

## Utilisation pour la Présentation

1. **Lancer SonarQube** sur ce projet
2. **Dashboard** : Montrer les métriques globales
3. **Issues** : Filtrer par type (Bug, Vulnerability, Code Smell)
4. **Security** : Montrer les hotspots et vulnérabilités
5. **Duplications** : Visualiser les blocs dupliqués
6. **Complexity** : Identifier les fonctions complexes
7. **Debt** : Calculer la dette technique

## Points Clés pour la Démo

- ✅ Détection automatique des failles de sécurité
- ✅ Identification des bugs avant la production
- ✅ Réduction de la dette technique
- ✅ Amélioration de la maintenabilité
- ✅ Standards de codage appliqués
- ✅ Métriques objectives pour le code review

## Fichiers à Analyser

```bash
# Python
app/main/application/security_vulnerabilities.py
app/main/application/code_duplication_1.py
app/main/application/code_duplication_2.py
app/main/application/high_complexity.py
app/main/application/code_smells.py
app/main/application/bugs_and_errors.py
app/main/application/performance_issues.py
app/main/application/mixed_issues.py
app/main/application/legacy_issues.py

# TypeScript/JavaScript
frontend/src/demo_sonar_issues.ts
frontend/src/more_sonar_issues.ts
```

## Note Importante

⚠️ **Ce code est VOLONTAIREMENT mauvais !**

Il sert uniquement à démontrer les capacités de SonarQube.
Ne JAMAIS utiliser ces patterns en production !

---

Bonne présentation ! 🎯
