import ReportingContent from '@/modules/ReportingContent'
import { PaginationManager } from '@/modules/PaginationManager';
import { TagManager } from '@/modules/TagManager';
import { SelectManager } from '@/modules/SelectManager';
import FilterFormHtmlManager from '@/modules/Filter/FilterFormHtmlManager';
import ConsoleCustom from "@/modules/General/ConsoleCustom";
import BootstrapComponentInitializer from "@/modules/General/BootstrapComponentInitializer";
import ConsoleTesteur from "@/modules/General/ConsoleTesteur";
import GeneralTheme from "@/modules/General/GeneralTheme";
import NotificationGeneral from "@/modules/General/NotificationGeneral";
import OnboardingManager from "@/modules/OnboardingManager";
import EmailConfirmationAccount from "@/modules/General/EmailConfirmationAccount";
import FullScreen from "@/modules/General/FullScreen";
import Sidebar from "@/modules/General/Sidebar";
import DeleteAccount from "@/modules/General/DeleteAccount";
import UserActivityLog from "@/modules/General/UserActivityLog";
import ShowConsoleBetaTester from "@/modules/General/ShowConsoleBetaTester";

// Gestionnaire global pour les erreurs de promesses non gérées
globalThis.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection', {
        reason: event.reason,
        promise: event.promise,
        message: event.reason?.message || String(event.reason),
        stack: event.reason?.stack,
        timestamp: Date.now(),
        url: globalThis.location.href,
        userAgent: navigator.userAgent
    });
    
    // Vérifier si c'est l'erreur spécifique des extensions de navigateur
    if (event.reason?.message && 
        (event.reason.message.includes('message channel closed') || 
         event.reason.message.includes('asynchronous response'))) {
        console.error('Browser Extension Message Channel Error Detected', {
            errorMessage: event.reason.message,
            stack: event.reason.stack,
            timestamp: Date.now()
        });
        // Empêcher l'affichage de l'erreur dans la console si c'est lié aux extensions
        event.preventDefault();
    }
});

// Gestionnaire global pour les erreurs non capturées
globalThis.addEventListener('error', (event) => {
    console.error('Uncaught Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error,
        stack: event.error?.stack,
        timestamp: Date.now(),
        url: globalThis.location.href
    });
});


// Initialise automatiquement tous les composants Bootstrap disponibles
document.addEventListener('DOMContentLoaded', () => {
    new BootstrapComponentInitializer().initialize();
    new FilterFormHtmlManager().init();
    ConsoleTesteur.log('General Event initialised');
});




document.addEventListener("DOMContentLoaded", () => {
    new GeneralTheme().addEvent();
    new FullScreen().addEvent();
    new EmailConfirmationAccount('resend_email_confirmation_account').addEvent();
    new Sidebar().addEvent();
    new ReportingContent('reportButton').addEvent();
    new PaginationManager().addEventListeners();
    new TagManager().addEventListeners();
    new SelectManager().addEventListeners();
    new NotificationGeneral().addEvent();
    new DeleteAccount().addEvent();
    new UserActivityLog().addEvent();
    new ShowConsoleBetaTester().addEvent();

    // Initialize Onboarding Shepherd
    const onboardingManager = new OnboardingManager();
    onboardingManager.initialize().catch((error) => {
        ConsoleCustom.error('Failed to initialize Onboarding:', error);
    });

});