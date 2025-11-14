"""
Ce fichier contient volontairement des failles de sécurité pour une démonstration SonarQube
NE PAS utiliser en production !
"""
import os
import pickle
import hashlib
import subprocess
from django.db import connection
from django.http import HttpResponse


# FAILLE 1: Hardcoded credentials
DATABASE_PASSWORD = "admin123"  # Hardcoded password
API_KEY = "sk-1234567890abcdefghijklmnop"  # Hardcoded secret
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


# FAILLE 2: SQL Injection
def get_user_by_name(username):
    """Vulnérable à l'injection SQL"""
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor = connection.cursor()
    cursor.execute(query)  # SQL Injection !
    return cursor.fetchall()


# FAILLE 3: Weak cryptography
def weak_hash_password(password):
    """Utilisation d'un algorithme de hashage faible"""
    return hashlib.md5(password.encode()).hexdigest()  # MD5 est faible !


# FAILLE 4: Command Injection
def ping_server(hostname):
    """Vulnérable à l'injection de commande"""
    cmd = "ping -c 1 " + hostname
    os.system(cmd)  # Command Injection !
    return "Ping executed"


# FAILLE 5: Use of eval()
def calculate_expression(expr):
    """Utilisation dangereuse d'eval"""
    result = eval(expr)  # Dangereux !
    return result


# FAILLE 6: Insecure deserialization
def load_user_data(data):
    """Désérialisation non sécurisée"""
    user_obj = pickle.loads(data)  # Pickle est dangereux !
    return user_obj


# FAILLE 7: Path Traversal
def read_file(filename):
    """Vulnérable au path traversal"""
    with open("/var/www/uploads/" + filename, 'r') as f:  # Path traversal !
        return f.read()


# FAILLE 8: Weak random
import random
def generate_token():
    """Génération de token avec random non sécurisé"""
    return random.randint(1000, 9999)  # random n'est pas cryptographiquement sûr !


# FAILLE 9: XSS vulnerability
def render_user_input(user_input):
    """Vulnérable aux XSS"""
    html = "<div>" + user_input + "</div>"  # Pas d'échappement !
    return HttpResponse(html)


# FAILLE 10: LDAP Injection
def ldap_search(username):
    """Vulnérable à l'injection LDAP"""
    filter = "(uid=" + username + ")"  # LDAP Injection !
    return filter


# FAILLE 11: XXE vulnerability
import xml.etree.ElementTree as ET
def parse_xml(xml_data):
    """Vulnérable aux attaques XXE"""
    root = ET.fromstring(xml_data)  # XXE vulnerable !
    return root


# FAILLE 12: Open redirect
def redirect_user(url):
    """Vulnérable aux open redirects"""
    from django.shortcuts import redirect
    return redirect(url)  # Pas de validation !


# FAILLE 13: Information disclosure
def get_error_details(exception):
    """Divulgation d'informations sensibles"""
    return str(exception) + "\n" + str(exception.__traceback__)


# FAILLE 14: Insecure file permissions
def create_secret_file():
    """Création de fichier avec permissions trop larges"""
    with open("/tmp/secret.txt", 'w') as f:
        f.write("Secret data")
    os.chmod("/tmp/secret.txt", 0o777)  # Permissions trop larges !


# FAILLE 15: Use of shell=True
def execute_command(user_cmd):
    """Utilisation dangereuse de subprocess"""
    subprocess.call(user_cmd, shell=True)  # shell=True est dangereux !


# FAILLE 16: Regular expression DoS (ReDoS)
import re
def validate_email(email):
    """Expression régulière vulnérable au ReDoS"""
    pattern = r'^([a-zA-Z0-9]+)*@.*$'  # Pattern dangereux !
    return re.match(pattern, email)


# FAILLE 17: Certificate validation disabled
import urllib.request
import ssl
def fetch_data(url):
    """Désactivation de la validation SSL"""
    context = ssl._create_unverified_context()  # Dangereux !
    return urllib.request.urlopen(url, context=context).read()


# FAILLE 18: Insecure cookie
def set_session_cookie(response):
    """Cookie sans flag secure"""
    response.set_cookie('session_id', 'abc123', secure=False, httponly=False)  # Dangereux !
    return response


# FAILLE 19: Mass assignment vulnerability
def update_user(request, user):
    """Mise à jour sans validation"""
    for key, value in request.POST.items():
        setattr(user, key, value)  # Mass assignment !
    user.save()


# FAILLE 20: Debug mode enabled
DEBUG = True  # Ne jamais mettre en production !
ALLOWED_HOSTS = ['*']  # Trop permissif !
