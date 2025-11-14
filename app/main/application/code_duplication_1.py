"""
Fichier avec duplication de code intentionnelle pour démonstration SonarQube
"""


def calculate_total_price_for_products(products):
    """Calcule le prix total des produits"""
    total = 0
    tax_rate = 0.20
    discount_rate = 0.10
    
    for product in products:
        base_price = product.get('price', 0)
        quantity = product.get('quantity', 1)
        
        # Calcul du prix de base
        subtotal = base_price * quantity
        
        # Application de la taxe
        tax_amount = subtotal * tax_rate
        price_with_tax = subtotal + tax_amount
        
        # Application de la remise si montant > 100
        if price_with_tax > 100:
            discount_amount = price_with_tax * discount_rate
            final_price = price_with_tax - discount_amount
        else:
            final_price = price_with_tax
        
        # Ajout au total
        total += final_price
    
    return round(total, 2)


def calculate_total_price_for_services(services):
    """Calcule le prix total des services"""
    total = 0
    tax_rate = 0.20
    discount_rate = 0.10
    
    for service in services:
        base_price = service.get('price', 0)
        quantity = service.get('quantity', 1)
        
        # Calcul du prix de base
        subtotal = base_price * quantity
        
        # Application de la taxe
        tax_amount = subtotal * tax_rate
        price_with_tax = subtotal + tax_amount
        
        # Application de la remise si montant > 100
        if price_with_tax > 100:
            discount_amount = price_with_tax * discount_rate
            final_price = price_with_tax - discount_amount
        else:
            final_price = price_with_tax
        
        # Ajout au total
        total += final_price
    
    return round(total, 2)


def process_user_login(username, password):
    """Traite la connexion utilisateur"""
    if username is None or username == "":
        return {"error": "Username is required"}
    
    if password is None or password == "":
        return {"error": "Password is required"}
    
    if len(password) < 8:
        return {"error": "Password too short"}
    
    if not any(char.isdigit() for char in password):
        return {"error": "Password must contain a number"}
    
    if not any(char.isupper() for char in password):
        return {"error": "Password must contain an uppercase letter"}
    
    if not any(char.islower() for char in password):
        return {"error": "Password must contain a lowercase letter"}
    
    return {"success": True, "username": username}


def process_user_registration(username, password):
    """Traite l'inscription utilisateur"""
    if username is None or username == "":
        return {"error": "Username is required"}
    
    if password is None or password == "":
        return {"error": "Password is required"}
    
    if len(password) < 8:
        return {"error": "Password too short"}
    
    if not any(char.isdigit() for char in password):
        return {"error": "Password must contain a number"}
    
    if not any(char.isupper() for char in password):
        return {"error": "Password must contain an uppercase letter"}
    
    if not any(char.islower() for char in password):
        return {"error": "Password must contain a lowercase letter"}
    
    return {"success": True, "username": username}
