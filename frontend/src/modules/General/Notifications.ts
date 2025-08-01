

class Notification {
    static createClientNotification(options = {}) {
        // Options par défaut
        const defaults = {
            message: 'Notification',
            type: 'info',
            duration: 3000,
            padding: '15px'
          };
    
        const config = { ...defaults, ...options };
    
        // Crée un conteneur pour les notifications s'il n'existe pas
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            notificationContainer.style.position = 'fixed';
            notificationContainer.style.padding = config.padding;
            notificationContainer.style.top = '20px';
            notificationContainer.style.right = '20px';
            notificationContainer.style.zIndex = '9999';
            document.body.appendChild(notificationContainer);
        }
    
        // Crée l'élément de notification
        const notification = document.createElement('div');
        
        notification.className = `bg-${config.type} fade show`;
        notification.role = 'alert';
        notification.style.borderRadius  = "3px";
        notification.innerText = config.message;
        notification.style.padding = '7px';
        notification.style.marginBottom = '10px';
    
        // Ajoute la notification au conteneur
        notificationContainer.appendChild(notification);
    
    
        // Disparition automatique
        const fadeOut = () => {
            notification.classList.remove('show'); // Déclenche l'animation fade-out
            notification.classList.add('fade'); // Ajoute la classe fade
            setTimeout(() => notification.remove(), 150); // Supprime complètement après l'animation
        };
      
        setTimeout(fadeOut, config.duration);
      
        // Permettre la fermeture au clic
        notification.addEventListener('click', fadeOut);
    
    }
    


}

export default Notification;