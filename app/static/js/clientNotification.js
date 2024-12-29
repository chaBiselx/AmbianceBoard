  function createClientNotification(options = {}) {
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
        notificationContainer.style.zIndex = '1050';
        document.body.appendChild(notificationContainer);
    }

    // Crée l'élément de notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${config.type} fade show`;
    notification.role = 'alert';
    notification.innerText = config.message;
    notification.style.marginBottom = '10px';

    // Ajoute la notification au conteneur
    notificationContainer.appendChild(notification);

    // Supprime la notification après la durée spécifiée
    setTimeout(() => {
        notification.classList.remove('show'); // Déclenche l'animation fade-out
        notification.classList.add('fade'); // Ajoute la classe fade
        setTimeout(() => notification.remove(), 150); // Supprime complètement après l'animation
    }, config.duration);
}
