"""
Fichier de démonstration avec problèmes variés pour SonarQube
Incluant: logging incorrect, exception handling, naming conventions, etc.
"""
import logging
import sys
import os


# TODO: Configurer le logging correctement
# FIXME: Logger vers un fichier, pas la console

# Code smell: Pas de configuration de logging
logger = logging.getLogger()


# Bug: Mauvaise gestion des exceptions
def catch_all_exceptions():
    """Attrape toutes les exceptions de manière incorrecte"""
    try:
        dangerous_operation()
    except Exception as e:  # Trop général !
        pass  # Et en plus on ne fait rien !


def dangerous_operation():
    raise RuntimeError("Something bad happened")


# Code smell: Mauvais noms de variables
def bad_naming():
    """Noms de variables incompréhensibles"""
    x = 10  # Que représente x ?
    y = 20  # Et y ?
    z = x + y
    
    # Noms trompeurs
    list = [1, 2, 3]  # Shadow le type built-in !
    dict = {'key': 'value'}  # Shadow le type built-in !
    str = "hello"  # Shadow le type built-in !
    
    return z, list, dict, str


# Bug: Re-raise sans préserver la stack trace
def improper_reraise():
    """Re-raise une exception incorrectement"""
    try:
        risky_function()
    except ValueError as e:
        # FIXME: Utiliser 'raise' seul pour préserver la trace
        raise ValueError(str(e))  # Perd la stack trace originale !


def risky_function():
    raise ValueError("Original error")


# Code smell: Print au lieu de logging
def print_instead_of_logging():
    """Utilise print au lieu du module logging"""
    print("Starting process")  # Code smell !
    print("Processing data")  # Code smell !
    print("Process complete")  # Code smell !
    
    # TODO: Utiliser logger.info() à la place


# Bug: Fichier ouvert mais jamais fermé
def file_not_closed():
    """Ouvre un fichier sans le fermer"""
    # FIXME: Utiliser un context manager (with)
    f = open('/tmp/data.txt', 'r')
    data = f.read()
    # Oops, jamais fermé !
    return data


# Code smell: Trop de return statements
def too_many_returns(status_code):
    """Fonction avec trop de returns"""
    if status_code == 200:
        return "OK"
    if status_code == 201:
        return "Created"
    if status_code == 400:
        return "Bad Request"
    if status_code == 401:
        return "Unauthorized"
    if status_code == 403:
        return "Forbidden"
    if status_code == 404:
        return "Not Found"
    if status_code == 500:
        return "Internal Server Error"
    if status_code == 502:
        return "Bad Gateway"
    if status_code == 503:
        return "Service Unavailable"
    return "Unknown"


# Bug: Comparaison de types incorrecte
def wrong_type_check(value):
    """Mauvaise façon de vérifier le type"""
    # Code smell: utiliser isinstance()
    if type(value) == str:
        return value.upper()
    if type(value) == int:
        return value * 2
    if type(value) == list:
        return len(value)
    return None


# Code smell: Fonction avec trop d'arguments
def too_many_parameters(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 
                        arg9, arg10, arg11, arg12, arg13, arg14, arg15):
    """15 paramètres, c'est trop !"""
    # TODO: Utiliser un objet de configuration
    return sum([arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, 
                arg9, arg10, arg11, arg12, arg13, arg14, arg15])


# Bug: Modification de variable globale
GLOBAL_COUNTER = 0

def modify_global():
    """Modifie une variable globale"""
    global GLOBAL_COUNTER
    GLOBAL_COUNTER += 1  # Anti-pattern !
    return GLOBAL_COUNTER


# Code smell: Classe vide
class EmptyClass:
    """Classe sans contenu"""
    pass  # Pourquoi cette classe existe ?


# Bug: Méthode qui retourne None implicitement
class InconsistentReturns:
    """Classe avec des returns inconsistants"""
    
    def get_value(self, key):
        """Return inconsistant"""
        if key == 'name':
            return 'John'
        if key == 'age':
            return 30
        # Pas de return explicite pour les autres cas !
    
    def calculate(self, a, b):
        """Parfois retourne, parfois non"""
        if a > 0 and b > 0:
            return a + b
        # Pas de return si condition fausse


# Code smell: Try/except trop large
def overly_broad_except():
    """Try block trop large"""
    try:
        # FIXME: Séparer en plusieurs try/except
        data = fetch_data()
        validated = validate_data(data)
        processed = process_data(validated)
        saved = save_data(processed)
        notified = notify_users(saved)
        logged = log_results(notified)
        return logged
    except:  # Bare except !
        return None


def fetch_data():
    return {}

def validate_data(data):
    return data

def process_data(data):
    return data

def save_data(data):
    return data

def notify_users(data):
    return data

def log_results(data):
    return data


# Bug: Assert utilisé pour la validation
def validation_with_assert(value):
    """Utilise assert pour la validation"""
    # Bug: assert est désactivé avec python -O
    assert value > 0, "Value must be positive"
    assert isinstance(value, int), "Value must be an integer"
    return 100 / value


# Code smell: Boolean flag parameter
def process_user(user, is_admin, is_active, is_verified, send_email, 
                 update_cache, log_activity, notify_admin):
    """Trop de boolean flags"""
    # FIXME: Utiliser un objet de configuration
    if is_admin:
        print("Admin user")
    if is_active:
        print("Active user")
    if is_verified:
        print("Verified user")
    if send_email:
        print("Sending email")
    if update_cache:
        print("Updating cache")
    if log_activity:
        print("Logging activity")
    if notify_admin:
        print("Notifying admin")


# Bug: Silently catching and ignoring errors
def silent_failure():
    """Ignore silencieusement les erreurs"""
    try:
        critical_operation()
    except Exception:
        pass  # FIXME: Au moins logger l'erreur !


def critical_operation():
    raise Exception("Critical error")


# Code smell: Nested ternary
def complex_ternary(x):
    """Ternaire imbriqué illisible"""
    return (
        "very high" if x > 300 else
        "high" if x > 200 else
        "medium" if x > 100 else
        "low" if x > 50 else
        "very low"
    )


# Bug: Mutable default argument
def mutable_default(item, collection=[]):
    """Argument mutable par défaut"""
    collection.append(item)
    return collection  # Bug classique !


# Code smell: Constants en minuscules
minimum_age = 18  # Devrait être MINIMUM_AGE
maximum_users = 1000  # Devrait être MAXIMUM_USERS
default_timeout = 30  # Devrait être DEFAULT_TIMEOUT


# Bug: Division entière au lieu de float
def integer_division(a, b):
    """Division qui peut perdre de la précision"""
    # En Python 3, / fait une division float, mais c'est un pattern à surveiller
    percentage = (a / b) * 100
    return int(percentage)  # Perte de précision


# Code smell: Magic numbers partout
def magic_numbers_everywhere(value):
    """Plein de magic numbers"""
    if value < 18:
        return value * 1.5 + 100
    elif value < 65:
        return value * 2.3 + 250
    else:
        return value * 0.8 - 150


# Bug: Recursion sans limite
def dangerous_recursion(n):
    """Recursion qui peut dépasser la limite"""
    # FIXME: Ajouter une limite ou convertir en itératif
    if n > 0:
        return n + dangerous_recursion(n - 1)
    return 0


# Code smell: Commented out code
def with_commented_code():
    """Code commenté au lieu d'être supprimé"""
    active_code = "This runs"
    
    # old_code = "This is old"
    # deprecated_function()
    # legacy_system.update()
    
    # TODO: Supprimer le code commenté
    # if False:
    #     print("Never runs")
    #     do_something_old()
    
    return active_code


# Bug: String concatenation dans SQL (même simulé)
def sql_concatenation(username):
    """Concaténation dans requête SQL"""
    # FIXME: Utiliser des paramètres préparés !
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return query  # SQL Injection !


# Code smell: Duplicate condition
def duplicate_conditions(x, y):
    """Conditions dupliquées"""
    if x > 10:
        if y > 20:
            if x > 10:  # Dupliqué !
                return "case1"
    
    if y > 20 and x > 10:
        if y > 20:  # Dupliqué !
            return "case2"
    
    return "default"


# Bug: Float utilisé comme clé de dictionnaire
def float_as_dict_key():
    """Float comme clé de dictionnaire - problématique"""
    data = {}
    # FIXME: Les floats ne sont pas idéaux comme clés
    data[0.1 + 0.2] = "value1"  # Problème de précision
    data[0.3] = "value2"
    
    return data


# Code smell: Inconsistent naming
def inconsistent_naming():
    """Styles de nommage mélangés"""
    user_name = "John"  # snake_case
    UserAge = 30  # PascalCase
    userEmail = "john@example.com"  # camelCase
    USER_ID = 123  # UPPER_CASE
    
    return user_name, UserAge, userEmail, USER_ID


# TODO: Finir d'implémenter cette fonction
def incomplete_function():
    """Fonction incomplète"""
    # FIXME: Ajouter l'implémentation
    pass


# Bug: Comparaison avec boolean
def boolean_comparison(flag):
    """Comparaison explicite avec True/False"""
    if flag == True:  # Code smell !
        return "true"
    if flag == False:  # Code smell !
        return "false"
    return "unknown"


# HACK: Solution temporaire
# FIXME: Remplacer par une vraie implémentation
def temporary_hack():
    """Solution temporaire qui devrait être remplacée"""
    # TODO: Faire proprement
    return "quick fix"


# Variables globales non utilisées
UNUSED_CONSTANT_1 = "Never used"
UNUSED_CONSTANT_2 = 999
UNUSED_CONSTANT_3 = {'key': 'value'}
