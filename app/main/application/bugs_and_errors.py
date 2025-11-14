"""
Fichier avec des bugs potentiels pour démonstration SonarQube
"""
import math


def divide_numbers(a, b):
    """Division sans vérification de zéro"""
    # Bug: Division par zéro possible
    return a / b


def get_user_from_list(users, index):
    """Accès sans vérification de l'index"""
    # Bug: Index out of range possible
    return users[index]


def calculate_average(numbers):
    """Calcul de moyenne sans vérifier la liste vide"""
    # Bug: Division par zéro si liste vide
    return sum(numbers) / len(numbers)


def access_dict_value(data, key):
    """Accès dictionnaire sans vérification"""
    # Bug: KeyError possible
    return data[key]


def null_pointer_risk(obj):
    """Accès à un attribut sans vérifier None"""
    # Bug: AttributeError si obj est None
    return obj.name.upper()


def recursive_function(n):
    """Fonction récursive sans condition d'arrêt claire"""
    # Bug: Récursion infinie possible
    if n > 0:
        return n + recursive_function(n - 1)
    # Pas de return pour n <= 0


def string_operation(text):
    """Opération sur string sans vérification"""
    # Bug: AttributeError si text est None
    return text.strip().upper().replace(" ", "_")


def math_operation(value):
    """Opération mathématique risquée"""
    # Bug: Domaine invalide pour sqrt si value < 0
    sqrt_result = math.sqrt(value)
    
    # Bug: Division par zéro si sqrt_result == 0
    final_result = 100 / sqrt_result
    
    return final_result


def list_operation(items):
    """Opération sur liste sans vérification"""
    # Bug: IndexError si liste vide
    first = items[0]
    last = items[-1]
    
    # Bug: Modification pendant l'itération
    for item in items:
        if item < 0:
            items.remove(item)
    
    return first, last


def file_operation(filename):
    """Opération sur fichier sans gestion d'erreur"""
    # Bug: FileNotFoundError possible
    with open(filename, 'r') as f:
        content = f.read()
    
    # Bug: JSONDecodeError possible
    import json
    data = json.loads(content)
    
    return data


def type_conversion(value):
    """Conversion de type sans vérification"""
    # Bug: ValueError si value n'est pas convertible
    num = int(value)
    
    # Bug: Division par zéro si num est 0
    result = 1000 / num
    
    return result


def nested_access(data):
    """Accès imbriqué sans vérification"""
    # Bug: Multiple points de défaillance possibles
    return data['user']['profile']['address']['street']


def comparison_error(x, y):
    """Comparaison avec types incompatibles"""
    # Bug: Comparaison potentiellement incorrecte
    if x == y:
        return True
    
    # Bug: TypeError possible si types incompatibles
    return x > y


def infinite_loop_risk(value):
    """Boucle avec risque d'infini"""
    counter = value
    result = []
    
    # Bug: Boucle infinie si value <= 0
    while counter != 0:
        result.append(counter)
        counter -= 1
    
    return result


def memory_leak_risk():
    """Risque de fuite mémoire"""
    # Bug: Liste qui grandit indéfiniment
    global_list = []
    
    for i in range(1000000):
        global_list.append([0] * 1000)
    
    return len(global_list)


def race_condition_risk(shared_data):
    """Condition de course potentielle"""
    # Bug: Pas de synchronisation
    value = shared_data.get('counter', 0)
    value += 1
    shared_data['counter'] = value
    return value


def overflow_risk(a, b, c):
    """Risque de dépassement"""
    # Bug: Dépassement possible avec grands nombres
    result = a * b * c * 999999999
    return result


def float_comparison(x, y):
    """Comparaison de flottants"""
    # Bug: Comparaison directe de floats est risquée
    if x == y:
        return "Equal"
    return "Not equal"


def unhandled_exception():
    """Exception non gérée"""
    # Bug: Exception levée sans gestion
    raise ValueError("Something went wrong")


def resource_leak(filename):
    """Fuite de ressource"""
    # Bug: Fichier jamais fermé en cas d'erreur
    f = open(filename, 'r')
    data = f.read()
    # Pas de f.close() !
    return data


def logical_error(age):
    """Erreur logique"""
    # Bug: Logique inversée
    if age < 18:
        return "adult"
    else:
        return "minor"


def off_by_one(items):
    """Erreur off-by-one"""
    result = []
    # Bug: Dépasse l'index
    for i in range(len(items) + 1):
        result.append(items[i])
    return result


def incorrect_return_type(value):
    """Type de retour incohérent"""
    if value > 0:
        return value
    elif value < 0:
        return str(value)
    else:
        return None  # Bug: Types de retour différents


def mutable_default_argument(item, my_list=[]):
    """Argument mutable par défaut"""
    # Bug: Partage de la même liste entre appels
    my_list.append(item)
    return my_list


def closure_issue():
    """Problème de closure"""
    # Bug: Toutes les fonctions partagent la même variable
    functions = []
    for i in range(5):
        functions.append(lambda: i)
    return functions


def unicode_error(text):
    """Erreur d'encodage potentielle"""
    # Bug: UnicodeEncodeError possible
    return text.encode('ascii')


def import_error():
    """Import conditionnel risqué"""
    # Bug: Module peut ne pas exister
    import non_existent_module
    return non_existent_module.do_something()


def assertion_in_production(value):
    """Assertion en production"""
    # Bug: Assert désactivé avec -O
    assert value > 0, "Value must be positive"
    return 100 / value


def shadowing_builtin(list, dict, str):
    """Shadow de built-ins"""
    # Bug: Masque les types built-in
    result = list + dict + str
    return result


def unreachable_code():
    """Code inaccessible"""
    return True
    # Bug: Code jamais exécuté
    print("This will never print")
    cleanup_resources()


def cleanup_resources():
    """Nettoyage des ressources"""
    pass
