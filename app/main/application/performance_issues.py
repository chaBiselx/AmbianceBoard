"""
Fichier Python avec problèmes de performance et maintenabilité
Pour démonstration SonarQube
"""
import time
import requests


# TODO: Optimiser les performances
# FIXME: Ce code est très lent

class PerformanceIssues:
    """Classe avec des problèmes de performance"""
    
    def __init__(self):
        # FIXME: Ne pas charger toutes les données en mémoire
        self.all_data = self.load_all_data()
        self.cache = {}
    
    def load_all_data(self):
        """Charge TOUTES les données en mémoire - mauvaise idée"""
        # TODO: Utiliser la pagination
        data = []
        for i in range(1000000):  # Un million d'éléments !
            data.append({
                'id': i,
                'value': i * 2,
                'name': f'Item {i}',
                'description': f'Description for item {i}' * 10
            })
        return data
    
    # Bug de performance: O(n²)
    def find_duplicates(self, items):
        """Algorithme très inefficace"""
        duplicates = []
        # O(n²) - très lent !
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i] == items[j]:
                    duplicates.append(items[i])
        return duplicates
    
    # Bug de performance: Concaténation de strings dans une boucle
    def build_large_string(self, items):
        """Concaténation inefficace"""
        result = ""
        # Très lent pour de grandes listes
        for item in items:
            result += str(item) + ", "  # Crée un nouvel objet à chaque fois !
        return result
    
    # Bug de performance: Regex compilée à chaque appel
    def validate_many_emails(self, emails):
        """Compile la regex à chaque fois"""
        import re
        valid = []
        for email in emails:
            # Regex recompilée à chaque itération !
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                valid.append(email)
        return valid
    
    # Bug de performance: Requêtes N+1
    def get_user_details(self, user_ids):
        """Problème N+1 classique"""
        results = []
        # Une requête par utilisateur au lieu d'une seule requête
        for user_id in user_ids:
            # FIXME: Faire une seule requête pour tous les IDs
            user = self.fetch_user(user_id)
            results.append(user)
        return results
    
    def fetch_user(self, user_id):
        """Simule une requête DB"""
        time.sleep(0.01)  # Simule la latence
        return {'id': user_id, 'name': f'User {user_id}'}
    
    # Bug de performance: Pas de lazy loading
    def process_large_file(self, filename):
        """Charge tout le fichier en mémoire"""
        # FIXME: Utiliser un générateur pour lire ligne par ligne
        with open(filename, 'r') as f:
            all_lines = f.readlines()  # Charge TOUT en mémoire !
        
        processed = []
        for line in all_lines:
            processed.append(line.strip().upper())
        return processed


# TODO: Refactoriser cette fonction
def inefficient_search(items, target):
    """Recherche linéaire alors qu'on pourrait trier et utiliser binary search"""
    # O(n) à chaque fois
    for item in items:
        if item == target:
            return True
    return False


# Bug de performance: Calculs redondants
def redundant_calculations(data):
    """Calcule la même chose plusieurs fois"""
    results = []
    
    for item in data:
        # Calcul répété inutilement
        total = sum(data)
        average = sum(data) / len(data)
        max_val = max(data)
        min_val = min(data)
        
        # TODO: Calculer une seule fois avant la boucle
        normalized = (item - min_val) / (max_val - min_val) if max_val != min_val else 0
        results.append({
            'item': item,
            'total': total,
            'average': average,
            'normalized': normalized
        })
    
    return results


# Bug de performance: Import dans une boucle
def imports_in_loop(iterations):
    """Import dans une boucle - très mauvais"""
    results = []
    
    for i in range(iterations):
        # FIXME: Déplacer l'import en haut du fichier
        import json
        import hashlib
        
        data = {'iteration': i}
        json_str = json.dumps(data)
        hash_val = hashlib.md5(json_str.encode()).hexdigest()
        results.append(hash_val)
    
    return results


# Bug de performance: Copie profonde inutile
def unnecessary_deep_copy(data):
    """Copie profonde alors qu'une shallow copy suffirait"""
    import copy
    
    results = []
    for item in data:
        # FIXME: deep copy est très lent
        copied = copy.deepcopy(item)
        copied['processed'] = True
        results.append(copied)
    
    return results


# Code smell: Fonction trop complexe
def overly_complex_function(a, b, c, d, e, f, g, h):
    """Fonction avec trop de paramètres et trop complexe"""
    # TODO: Simplifier cette fonction
    
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            if g > 0:
                                if h > 0:
                                    result = a + b + c + d + e + f + g + h
                                    if result > 100:
                                        if result > 200:
                                            if result > 300:
                                                return result * 3
                                            else:
                                                return result * 2
                                        else:
                                            return result * 1.5
                                    else:
                                        return result
    
    return 0


# Bug de performance: Sleep dans une boucle
def slow_processing(items):
    """Utilise sleep - très lent"""
    # TODO: Supprimer le sleep ou paralléliser
    results = []
    
    for item in items:
        # FIXME: Pourquoi sleep ?
        time.sleep(0.1)
        processed = item * 2
        results.append(processed)
    
    return results


# Bug de performance: Pas de connexion pool
def multiple_http_requests(urls):
    """Crée une nouvelle session pour chaque requête"""
    results = []
    
    for url in urls:
        # FIXME: Utiliser une session réutilisable
        response = requests.get(url)
        results.append(response.json())
    
    return results


# Code smell: God class
class GodClass:
    """Classe qui fait trop de choses"""
    
    def __init__(self):
        self.users = []
        self.products = []
        self.orders = []
        self.payments = []
        self.shipping = []
        self.invoices = []
        self.reports = []
        # TODO: Diviser en plusieurs classes
    
    def create_user(self, data):
        pass
    
    def update_user(self, user_id, data):
        pass
    
    def delete_user(self, user_id):
        pass
    
    def create_product(self, data):
        pass
    
    def update_product(self, product_id, data):
        pass
    
    def delete_product(self, product_id):
        pass
    
    def create_order(self, data):
        pass
    
    def process_payment(self, order_id):
        pass
    
    def calculate_shipping(self, order_id):
        pass
    
    def generate_invoice(self, order_id):
        pass
    
    def generate_report(self, type):
        pass
    
    def send_email(self, recipient, subject, body):
        pass
    
    def send_sms(self, phone, message):
        pass
    
    def log_activity(self, activity):
        pass
    
    # TODO: Encore plus de méthodes...


# Bug de performance: Pas de cache
def expensive_calculation(n):
    """Calcul coûteux sans cache"""
    # FIXME: Implémenter un cache ou memoization
    if n <= 1:
        return n
    
    # Recalcule plusieurs fois les mêmes valeurs
    return expensive_calculation(n-1) + expensive_calculation(n-2)


# Code smell: Trop de responsabilités
def do_everything(user_data):
    """Une fonction qui fait absolument tout"""
    # TODO: Diviser en plusieurs fonctions
    
    # Validation
    if not user_data.get('email'):
        raise ValueError("Email required")
    
    # Nettoyage
    email = user_data['email'].strip().lower()
    
    # Hash du password
    import hashlib
    password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()
    
    # Création de l'utilisateur
    user = {
        'email': email,
        'password': password_hash,
        'created_at': time.time()
    }
    
    # Sauvegarde en DB
    save_to_database(user)
    
    # Envoi d'email
    send_welcome_email(email)
    
    # Log
    log_user_creation(user)
    
    # Analytics
    track_analytics('user_created', user)
    
    # Notification admin
    notify_admin_new_user(user)
    
    return user


def save_to_database(user):
    pass


def send_welcome_email(email):
    pass


def log_user_creation(user):
    pass


def track_analytics(event, data):
    pass


def notify_admin_new_user(user):
    pass


# FIXME: Cette variable ne devrait pas être globale
global_state = {'counter': 0, 'users': [], 'cache': {}}


# Code smell: Trop de lignes
def very_long_function():
    """Fonction avec trop de lignes"""
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    line10 = 10
    line11 = 11
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    # TODO: Refactoriser cette fonction
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    line32 = 32
    line33 = 33
    line34 = 34
    line35 = 35
    line36 = 36
    line37 = 37
    line38 = 38
    line39 = 39
    line40 = 40
    # FIXME: Trop de lignes !
    line41 = 41
    line42 = 42
    line43 = 43
    line44 = 44
    line45 = 45
    line46 = 46
    line47 = 47
    line48 = 48
    line49 = 49
    line50 = 50
    
    return sum([line1, line2, line3, line4, line5, line6, line7, line8, line9, line10,
                line11, line12, line13, line14, line15, line16, line17, line18, line19, line20,
                line21, line22, line23, line24, line25, line26, line27, line28, line29, line30,
                line31, line32, line33, line34, line35, line36, line37, line38, line39, line40,
                line41, line42, line43, line44, line45, line46, line47, line48, line49, line50])
