"""
Fichier avec des code smells, TODOs, FIXME et autres problèmes de qualité
"""
import sys
import os
import math


# TODO: Refactoriser cette classe
# FIXME: Cette implémentation est temporaire
# HACK: Solution rapide à corriger
class UserManager:
    """Gestionnaire d'utilisateurs avec pleins de problèmes"""
    
    def __init__(self):
        # TODO: Utiliser une vraie base de données
        self.users = []
        self.count = 0
        self.maxUsers = 1000
        self.minAge = 18
        self.maxAge = 120
        # Variable jamais utilisée
        self.unused_variable_1 = "This is never used"
        self.unused_variable_2 = 12345
        self.temporary_data = None
    
    # FIXME: Cette méthode est trop longue
    def add_user(self, name, age, email, address, phone, city, country, postal_code):
        """Ajoute un utilisateur"""
        # TODO: Valider les données
        # FIXME: Gérer les doublons
        
        user = {
            'name': name,
            'age': age,
            'email': email,
            'address': address,
            'phone': phone,
            'city': city,
            'country': country,
            'postal_code': postal_code
        }
        
        self.users.append(user)
        self.count = self.count + 1  # Code smell: utiliser +=
        
        # Code mort - jamais exécuté
        if False:
            print("This will never run")
            self.cleanup_old_users()
        
        return True
    
    # Méthode jamais appelée (code mort)
    def cleanup_old_users(self):
        """Nettoie les vieux utilisateurs"""
        # TODO: Implémenter cette fonctionnalité
        pass
    
    # FIXME: Paramètres par défaut mutables
    def process_data(self, items=[]):
        """Traite des données"""
        items.append("new_item")
        return items
    
    # Code smell: méthode trop longue avec beaucoup de paramètres
    def update_user(self, user_id, name=None, age=None, email=None, 
                    address=None, phone=None, city=None, country=None,
                    postal_code=None, occupation=None, salary=None,
                    department=None, manager=None, start_date=None):
        """Met à jour un utilisateur"""
        # TODO: Optimiser cette méthode
        user = self.users[user_id]
        
        if name:
            user['name'] = name
        if age:
            user['age'] = age
        if email:
            user['email'] = email
        if address:
            user['address'] = address
        if phone:
            user['phone'] = phone
        if city:
            user['city'] = city
        if country:
            user['country'] = country
        if postal_code:
            user['postal_code'] = postal_code
        if occupation:
            user['occupation'] = occupation
        if salary:
            user['salary'] = salary
        if department:
            user['department'] = department
        if manager:
            user['manager'] = manager
        if start_date:
            user['start_date'] = start_date
        
        return user


# Variables globales inutilisées
UNUSED_CONSTANT = "Never used"
ANOTHER_UNUSED_VAR = 999
global_counter = 0


# TODO: Supprimer cette fonction
def deprecated_function():
    """Cette fonction est dépréciée"""
    # FIXME: Ne plus utiliser
    print("Deprecated")
    pass


# FIXME: Utiliser une vraie classe d'exception
def risky_operation():
    """Opération risquée sans gestion d'erreur"""
    # Code smell: bare except
    try:
        result = 10 / 0
        return result
    except:  # Bare except !
        pass
    
    # Code mort
    unreachable_code = "This is never reached"
    return unreachable_code


# Code smell: fonction avec trop de return
def multiple_returns(value):
    """Fonction avec beaucoup de return"""
    if value < 0:
        return "negative"
    if value == 0:
        return "zero"
    if value == 1:
        return "one"
    if value < 10:
        return "small"
    if value < 100:
        return "medium"
    if value < 1000:
        return "large"
    if value < 10000:
        return "very large"
    return "huge"


# HACK: Solution temporaire
def temp_solution(data):
    """Solution temporaire à refactoriser"""
    # TODO: Faire mieux que ça
    # FIXME: C'est vraiment moche
    x = data
    y = x
    z = y
    a = z
    b = a
    c = b
    return c


# Code smell: noms de variables non explicites
def bad_names(a, b, c):
    """Noms de variables cryptiques"""
    x = a + b
    y = b * c
    z = x - y
    temp = z / 2
    data = temp + 10
    result = data - 5
    return result


# Code smell: Magic numbers
def calculate_something(value):
    """Calcul avec des magic numbers"""
    # Que représentent ces nombres ?
    result = value * 1.21
    if result > 5000:
        result = result * 0.95
    if result < 100:
        result = result + 50
    return result + 3.14159


# FIXME: Cette classe ne devrait pas exister
class EmptyClass:
    """Classe vide"""
    pass


# TODO: Implémenter cette classe
class IncompleteClass:
    """Classe incomplète"""
    def __init__(self):
        pass
    
    def method1(self):
        # TODO: À implémenter
        pass
    
    def method2(self):
        # FIXME: À compléter
        pass


# Code smell: comparaison avec True/False
def bad_comparison(flag):
    """Mauvaise façon de comparer des booléens"""
    if flag == True:  # Code smell !
        return True
    elif flag == False:  # Code smell !
        return False
    else:
        return None


# Code smell: isinstance redondant
def redundant_check(value):
    """Vérifications redondantes"""
    if type(value) == int:  # Utiliser isinstance
        return value * 2
    if type(value) == str:  # Utiliser isinstance
        return value.upper()
    return value


# FIXME: Formater correctement
def badly_formatted(x,y,z):
    """Mauvais formatage"""
    result=x+y*z  # Pas d'espaces
    if(result>100):  # Parenthèses inutiles
        return result
    else:
        return 0


# Code smell: print statements (utiliser logging)
def debug_function(data):
    """Fonction avec des prints de debug"""
    print("Starting function")
    print(f"Data: {data}")
    result = data * 2
    print(f"Result: {result}")
    return result


# TODO: Optimiser cet algorithme
def inefficient_algorithm(items):
    """Algorithme inefficace O(n²)"""
    result = []
    for i in items:
        for j in items:
            if i == j:
                result.append(i)
    return result


# Variables importées mais non utilisées
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter, OrderedDict


# FIXME: Fermer les fichiers correctement
def file_handling_issue(filename):
    """Gestion de fichier incorrecte"""
    f = open(filename, 'r')  # Pas de with statement
    content = f.read()
    # OOPS: fichier jamais fermé !
    return content
