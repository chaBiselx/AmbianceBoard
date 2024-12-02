function createClientNotification(options = {}) {
    // Options par défaut
    const defaults = {
      message: 'Notification',
      type: 'info',
      duration: 3000,
      position: 'top-right',
      padding: '15px'
    };
  
    // Fusionner les options par défaut avec les options personnalisées
    const config = { ...defaults, ...options };
  
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.classList.add('notification', `notification-${config.type}`);
    notification.style.position = 'fixed';
  
    // Définir la position
    switch(config.position) {
      case 'top-right':
        notification.style.top = '20px';
        notification.style.right = '20px';
        break;
      case 'top-left':
        notification.style.top = '20px';
        notification.style.left = '20px';
        break;
      case 'bottom-right':
        notification.style.bottom = '20px';
        notification.style.right = '20px';
        break;
      case 'bottom-left':
        notification.style.bottom = '20px';
        notification.style.left = '20px';
        break;
      default:
        notification.style.top = '20px';
        notification.style.right = '20px';
    }
  
    // Ajouter le message
    notification.textContent = config.message;
  
    // Style de base
    notification.style.padding = config.padding;
    notification.style.borderRadius = '5px';
    notification.style.color = 'white';
    notification.style.zIndex = '1000';
    notification.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    notification.style.transition = 'opacity 0.3s ease-in-out';
  
    // Styles selon le type
    const typeStyles = {
      info: { backgroundColor: '#3498db' },
      success: { backgroundColor: '#2ecc71' },
      warning: { backgroundColor: '#f39c12' },
      error: { backgroundColor: '#e74c3c' }
    };
  
    Object.assign(notification.style, typeStyles[config.type] || typeStyles.info);
  
    // Ajouter au body
    document.body.appendChild(notification);
  
    // Disparition automatique
    const fadeOut = () => {
      notification.style.opacity = '0';
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    };
  
    setTimeout(fadeOut, config.duration);
  
    // Permettre la fermeture au clic
    notification.addEventListener('click', fadeOut);
  
    return notification;
  }