"""
Autre fichier avec duplication de code
"""


def calculate_invoice_total(invoice_items):
    """Calcule le total de la facture"""
    total = 0
    tax_rate = 0.20
    discount_rate = 0.10
    
    for item in invoice_items:
        base_price = item.get('price', 0)
        quantity = item.get('quantity', 1)
        
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


def validate_user_password(password):
    """Valide le mot de passe utilisateur"""
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
    
    return {"valid": True}


def send_email_notification(recipient, subject, body):
    """Envoie une notification par email"""
    import smtplib
    from email.mime.text import MIMEText
    
    # Configuration SMTP
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_user = "user@example.com"
    smtp_password = "password123"
    
    # Création du message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = recipient
    
    # Envoi
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def send_sms_notification(phone, message):
    """Envoie une notification par SMS"""
    import smtplib
    from email.mime.text import MIMEText
    
    # Configuration SMTP
    smtp_server = "smtp.example.com"
    smtp_port = 587
    smtp_user = "user@example.com"
    smtp_password = "password123"
    
    # Création du message
    msg = MIMEText(message)
    msg['Subject'] = "SMS Notification"
    msg['From'] = smtp_user
    msg['To'] = phone
    
    # Envoi
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
