# Activation du MFA (TOTP) pour SSH

Réf : https://ubuntu.com/tutorials/configure-ssh-2fa

> ⚠️ Garder une session SSH ouverte pendant toute la procédure et tester dans un second terminal.

## Installation 
Installer la librairie
```
sudo apt install libpam-google-authenticator
```

## Configuration TOTP 
Configurer le TOTP avec l'utilisateur cible (avant de modifier sshd)
```
google-authenticator
```
Réponses :
- Make tokens "time-based" : `yes`
- Update the ~/.google_authenticator file : `yes`
- Disallow multiple uses : `yes`
- Increase the original generation time window : `no`
- Enable rate-limiting : `yes`

Scanner le QR code dans l'application TOTP, puis enregistrer la clé secrète
et les codes de secours dans un coffre-fort numérique.

## Configuration SSH 
Configurer PAM
```
sudo vi /etc/pam.d/sshd
```
Commenter :
```
# @include common-auth
```
et jouter :
```
auth required pam_google_authenticator.so
```
(Attention : plus de connexion par mot de passe via PAM pour les autres utilisateurs.)

```
sudo vi /etc/ssh/sshd_config
```
Vérifier / ajouter :
```
ChallengeResponseAuthentication no 

Match User user_account
    PasswordAuthentication no
    KbdInteractiveAuthentication yes
    PubkeyAuthentication yes
    AuthenticationMethods publickey,keyboard-interactive
```

## Synchronisation  
Se connecter avec l'utilisateur cible : 
```
google-authenticator
```

Valider et recharger
```
sudo sshd -t && sudo systemctl restart ssh
```

## Tester dans un nouveau terminal
Attendu : passphrase de la clé, puis code TOTP.
