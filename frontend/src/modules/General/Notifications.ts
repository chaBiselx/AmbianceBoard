type NotificationOptions = {
    message: string;
    type?: 'primary' | 'secondary' | 'info' | 'success' | 'warning' | 'danger';
    duration?: number;
    padding?: string;
};

type ActionNotificationOptions = {
    title: string;
    message: string;
    actionLabel: string;
    dismissLabel: string;
    onAction: () => void;
    onDismiss?: () => void;
};

class Notification {
    static createActionNotification(options: ActionNotificationOptions): { close: () => void } {
        let container = document.getElementById('action-notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'action-notification-container';
            container.className = 'action-notification-container';
            document.body.appendChild(container);
        }

        const notification = document.createElement('section');
        notification.className = 'action-notification';
        notification.setAttribute('role', 'status');
        notification.setAttribute('aria-live', 'polite');

        const title = document.createElement('h2');
        title.className = 'action-notification-title';
        title.textContent = options.title;
        const message = document.createElement('p');
        message.textContent = options.message;

        const dismiss = document.createElement('button');
        dismiss.type = 'button';
        dismiss.className = 'btn action-notification-dismiss';
        dismiss.setAttribute('aria-label', options.dismissLabel);
        dismiss.title = options.dismissLabel;
        const icon = document.createElement('i');
        icon.className = 'fa-solid fa-xmark';
        icon.setAttribute('aria-hidden', 'true');
        dismiss.appendChild(icon);

        const action = document.createElement('button');
        action.type = 'button';
        action.className = 'btn btn-primary action-notification-action';
        action.textContent = options.actionLabel;

        let closed = false;
        const close = () => {
            if (closed) return;
            closed = true;
            notification.remove();
            if (!container.hasChildNodes()) container.remove();
        };
        action.addEventListener('click', () => {
            if (closed) return;
            close();
            options.onAction();
        });
        dismiss.addEventListener('click', () => {
            if (closed) return;
            close();
            options.onDismiss?.();
        });
        notification.append(title, dismiss, message, action);
        container.appendChild(notification);
        return { close };
    }

    static createClientNotification(options: NotificationOptions) {
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