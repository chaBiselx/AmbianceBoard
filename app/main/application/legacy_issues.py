"""
Fichier final avec des anti-patterns et code legacy simulé
"""
import pickle
import yaml
import xml.etree.ElementTree as ET


# TODO: Nettoyer ce fichier legacy
# FIXME: Code technique debt élevée
# XXX: Code dangereux à refactoriser


# Faille: Désérialisation non sécurisée YAML
def unsafe_yaml_load(yaml_string):
    """Charge du YAML de manière non sécurisée"""
    # CRITICAL: yaml.load sans Loader est dangereux !
    data = yaml.load(yaml_string)  # Exécution de code possible !
    return data


# Faille: XML Entity Expansion (Billion Laughs)
def parse_untrusted_xml(xml_string):
    """Parse du XML sans protection"""
    # FIXME: Vulnérable aux attaques XXE et entity expansion
    root = ET.fromstring(xml_string)
    return root


# Faille: Pickle de données non fiables
def unsafe_pickle_load(pickled_data):
    """Désérialise du pickle non fiable"""
    # CRITICAL: pickle peut exécuter du code arbitraire !
    obj = pickle.loads(pickled_data)
    return obj


# Code smell: Utilisation de exec()
def execute_dynamic_code(code_string):
    """Exécute du code dynamique"""
    # DANGER: exec() est aussi dangereux qu'eval()
    exec(code_string)


# Code smell: Utilisation de compile()
def compile_and_exec(source):
    """Compile et exécute du code"""
    # FIXME: Très dangereux
    code = compile(source, '<string>', 'exec')
    exec(code)


# Bug: Race condition avec fichiers
def race_condition_file():
    """Race condition classique"""
    import os
    filename = '/tmp/shared_file.txt'
    
    # FIXME: Race condition entre check et use
    if os.path.exists(filename):
        # Quelqu'un pourrait supprimer le fichier ici !
        with open(filename, 'r') as f:
            return f.read()


# Faille: TOCTOU (Time-of-check to time-of-use)
def toctou_vulnerability(filepath):
    """Vulnérabilité TOCTOU"""
    import os
    
    # Check
    if os.access(filepath, os.R_OK):
        # Time gap - le fichier pourrait changer ici !
        # Use
        with open(filepath, 'r') as f:
            return f.read()


# Code smell: Global state mutable
GLOBAL_CACHE = {}
GLOBAL_CONFIG = {
    'debug': True,
    'api_key': 'secret123'  # Hardcoded secret !
}


def use_global_state(key, value):
    """Modifie un état global"""
    # Anti-pattern: mutation globale
    GLOBAL_CACHE[key] = value
    GLOBAL_CONFIG['last_update'] = value


# Bug: Thread-unsafe code
class UnsafeCounter:
    """Compteur non thread-safe"""
    
    def __init__(self):
        self.count = 0
    
    def increment(self):
        # FIXME: Race condition en multi-threading
        temp = self.count
        temp += 1
        self.count = temp  # Pas atomique !


# Code smell: Singleton anti-pattern
class Singleton:
    """Implémentation de singleton (anti-pattern)"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


# Bug: Memory leak avec références circulaires
class Parent:
    """Classe avec référence circulaire"""
    def __init__(self):
        self.child = None
    
    def set_child(self, child):
        self.child = child


class Child:
    """Classe avec référence au parent"""
    def __init__(self, parent):
        self.parent = parent  # Référence circulaire !
        parent.set_child(self)


# Code smell: God object (objet dieu)
class ApplicationManager:
    """Classe qui fait absolument tout"""
    
    def __init__(self):
        self.db_connection = None
        self.cache = {}
        self.sessions = {}
        self.config = {}
        self.logger = None
        # TODO: Séparer les responsabilités
    
    def connect_database(self):
        pass
    
    def execute_query(self, query):
        pass
    
    def cache_set(self, key, value):
        pass
    
    def cache_get(self, key):
        pass
    
    def session_create(self, user):
        pass
    
    def session_destroy(self, session_id):
        pass
    
    def config_load(self, filepath):
        pass
    
    def config_save(self, filepath):
        pass
    
    def log_info(self, message):
        pass
    
    def log_error(self, message):
        pass
    
    def send_email(self, to, subject, body):
        pass
    
    def process_payment(self, amount):
        pass
    
    def generate_report(self):
        pass


# Bug: Integer overflow (simulé)
def potential_overflow(a, b, c):
    """Potentiel dépassement avec grands nombres"""
    # En Python, pas de vrai overflow mais problème de performance
    result = a ** b ** c  # Peut exploser !
    return result


# Code smell: Circular dependency (simulé)
# from module_a import ClassA  # ClassA importe de ce module
class ClassB:
    """Classe qui crée une dépendance circulaire"""
    def __init__(self):
        # from module_a import ClassA  # Circular import !
        pass


# Bug: Temps de réponse non borné
def unbounded_operation(data):
    """Opération sans timeout"""
    import requests
    
    # FIXME: Pas de timeout !
    response = requests.get('https://api.example.com/data')
    return response.json()


# Code smell: Hardcoded configuration
DATABASE_HOST = "192.168.1.100"  # Hardcoded !
DATABASE_PORT = 5432
DATABASE_NAME = "production_db"
DATABASE_USER = "admin"
DATABASE_PASSWORD = "P@ssw0rd123"  # Hardcoded password !

SMTP_SERVER = "smtp.gmail.com"
SMTP_USER = "myapp@gmail.com"
SMTP_PASSWORD = "smtp_secret_123"  # Hardcoded !

AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"  # Hardcoded !
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # Hardcoded !


# Bug: Path traversal vulnerability
def read_user_file(filename):
    """Vulnérable au path traversal"""
    import os
    
    base_dir = "/var/www/uploads/"
    # FIXME: Valider et nettoyer le filename !
    filepath = os.path.join(base_dir, filename)
    # Utilisateur peut passer "../../../etc/passwd"
    with open(filepath, 'r') as f:
        return f.read()


# Code smell: Feature envy
class Customer:
    """Client avec des données"""
    def __init__(self, name, orders):
        self.name = name
        self.orders = orders


class OrderProcessor:
    """Classe qui connaît trop Customer (feature envy)"""
    def calculate_total(self, customer):
        # FIXME: Cette logique devrait être dans Customer
        total = 0
        for order in customer.orders:
            total += order.price * order.quantity
        return total
    
    def get_customer_status(self, customer):
        # FIXME: Feature envy
        if len(customer.orders) > 10:
            return "VIP"
        elif len(customer.orders) > 5:
            return "Regular"
        else:
            return "New"


# Bug: Suppression de fichier sans vérification
def dangerous_file_delete(filename):
    """Supprime un fichier sans vérification"""
    import os
    
    # DANGER: Pas de vérification !
    os.remove(filename)


# Code smell: Train wreck (Law of Demeter violation)
def train_wreck(user):
    """Chaîne d'appels trop longue"""
    # Code smell: connaît trop la structure interne
    street = user.address.location.street.name.upper()
    return street


# Bug: Shell injection avec subprocess
def shell_injection(user_input):
    """Injection de commande shell"""
    import subprocess
    
    # CRITICAL: Vulnérable à l'injection
    command = f"ls -la {user_input}"
    subprocess.call(command, shell=True)  # DANGER !


# Code smell: Primitive obsession
def create_user_old_way(name, email, street, city, zip_code, country,
                        phone_country, phone_area, phone_number):
    """Trop de primitives au lieu d'objets"""
    # FIXME: Créer des classes Address et Phone
    return {
        'name': name,
        'email': email,
        'street': street,
        'city': city,
        'zip': zip_code,
        'country': country,
        'phone_country': phone_country,
        'phone_area': phone_area,
        'phone_number': phone_number
    }


# Bug: Conflit de noms avec modules standard
def open(filename):  # Shadow la fonction built-in open() !
    """Nom qui masque un built-in"""
    print(f"Opening {filename}")


def input(prompt):  # Shadow la fonction built-in input() !
    """Autre nom qui masque un built-in"""
    print(prompt)
    return "fake input"


# Code smell: Anemic domain model
class User:
    """Classe anémique (que des getters/setters, pas de logique)"""
    def __init__(self):
        self._name = None
        self._email = None
        self._age = None
    
    def get_name(self):
        return self._name
    
    def set_name(self, name):
        self._name = name
    
    def get_email(self):
        return self._email
    
    def set_email(self, email):
        self._email = email
    
    def get_age(self):
        return self._age
    
    def set_age(self, age):
        self._age = age


# TODO: Supprimer ce code de test
# XXX: NE PAS DEPLOYER EN PRODUCTION !
def debug_code():
    """Code de debug à supprimer"""
    print("DEBUG: Starting")
    import pdb; pdb.set_trace()  # FIXME: Retirer le debugger !
    print("DEBUG: Done")


# Bug: Comparaison de floats
def compare_floats(a, b):
    """Comparaison directe de floats"""
    # Bug: problème de précision
    if a == b:
        return "equal"
    return "different"


# DEPRECATED: Ne plus utiliser
# TODO: Migrer vers new_api()
def old_api():
    """API dépréciée"""
    # FIXME: Marquer comme deprecated avec decorator
    return "old implementation"


# Code smell: Flags dans les noms de méthodes
class DataProcessor:
    """Noms de méthodes avec des flags"""
    
    # FIXME: Créer deux méthodes séparées
    def process_data_sync_or_async(self, data, is_async=False):
        if is_async:
            return self._process_async(data)
        else:
            return self._process_sync(data)
    
    def _process_sync(self, data):
        return data
    
    def _process_async(self, data):
        return data


# Variables non utilisées (code mort)
DEAD_CONSTANT = "Never used anywhere"
OBSOLETE_CONFIG = {'old': 'config'}
DEPRECATED_MAPPING = {1: 'one', 2: 'two'}
