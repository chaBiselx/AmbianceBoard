# Montage de disque dur



## Montage de dossier de destination
création du dossier de destination : 

```bash
sudo mkdir -p /mnt/disque-backup
```


verifier les disques via `lsblk` et regarder 

créer le montage en lecture
```bash
sudo mount -t ntfs3 /dev/sdb6 /mnt/disque-backup
```

en read only : 
```bash
sudo mount -t ntfs3 -o ro /dev/sdb6 /mnt/disque-backup

```

verifier le montage : 
```bash
findmnt /mnt/disque-backup
```


pour supprimer le montage 
```bash
sudo umount  /mnt/disque-backup
```

## autre command utiles

voie la liste d'espace disponible 
```bash
df -h /path
```