/**
 * Fichier TypeScript avec des problèmes de sécurité et code smells
 * Pour démonstration SonarQube
 */

// TODO: Refactoriser ce fichier
// FIXME: Corriger les problèmes de sécurité
// HACK: Solution temporaire

// Code smell: Variable globale
var globalCounter = 0;
var unusedGlobalVariable = "Never used";

// Faille de sécurité: eval()
function executeUserCode(userInput: string): any {
    // Dangereux: eval permet l'exécution de code arbitraire
    return eval(userInput);
}

// Faille de sécurité: innerHTML avec données utilisateur
function renderUserContent(content: string): void {
    const container = document.getElementById('content');
    if (container) {
        // XSS vulnerability
        container.innerHTML = content;
    }
}

// Code smell: any partout
function processData(data: any): any {
    const result: any = {};
    result.value = data.value;
    result.name = data.name;
    return result;
}

// Bug: null/undefined non géré
function getUserName(user: any): string {
    // Bug: peut crasher si user est null ou name undefined
    return user.name.toUpperCase();
}

// Complexité élevée
function complexValidation(user: any, product: any, order: any): boolean {
    if (user) {
        if (user.active) {
            if (!user.banned) {
                if (user.emailVerified) {
                    if (product) {
                        if (product.available) {
                            if (product.stock > 0) {
                                if (order) {
                                    if (order.quantity > 0) {
                                        if (order.quantity <= product.stock) {
                                            if (order.totalPrice > 0) {
                                                if (order.paymentMethod) {
                                                    return true;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return false;
}

// Code dupliqué
function calculatePriceWithTax1(price: number): number {
    const taxRate = 0.20;
    const tax = price * taxRate;
    const total = price + tax;
    return Math.round(total * 100) / 100;
}

function calculatePriceWithTax2(amount: number): number {
    const taxRate = 0.20;
    const tax = amount * taxRate;
    const total = amount + tax;
    return Math.round(total * 100) / 100;
}

// Code smell: console.log en production
function debugFunction(data: any): void {
    console.log("Starting function");
    console.log("Data:", data);
    const result = data.value * 2;
    console.log("Result:", result);
}

// Bug: Division par zéro
function calculateAverage(numbers: number[]): number {
    const sum = numbers.reduce((a, b) => a + b, 0);
    // Bug: pas de vérification si numbers.length === 0
    return sum / numbers.length;
}

// Code smell: Variable jamais utilisée
function unusedVariables(): void {
    const used = "This is used";
    const unused1 = "Never used";
    const unused2 = 12345;
    const unused3 = { key: "value" };
    
    console.log(used);
}

// Magic numbers
function applyDiscount(price: number): number {
    if (price > 1000) {
        return price * 0.85;
    } else if (price > 500) {
        return price * 0.90;
    } else if (price > 100) {
        return price * 0.95;
    }
    return price;
}

// Code smell: Trop de paramètres
function createUser(
    firstName: string,
    lastName: string,
    email: string,
    phone: string,
    address: string,
    city: string,
    country: string,
    postalCode: string,
    birthDate: string,
    occupation: string,
    company: string,
    department: string,
    salary: number
): any {
    // TODO: Utiliser un objet au lieu de 13 paramètres
    return {
        firstName,
        lastName,
        email,
        phone,
        address,
        city,
        country,
        postalCode,
        birthDate,
        occupation,
        company,
        department,
        salary
    };
}

// Faille: localStorage sans encryption
function saveUserData(userData: any): void {
    // Faille de sécurité: données sensibles en clair
    localStorage.setItem('userData', JSON.stringify(userData));
    localStorage.setItem('password', userData.password);
    localStorage.setItem('creditCard', userData.creditCard);
}

// Code smell: == au lieu de ===
function compareValues(a: any, b: any): boolean {
    // Code smell: utiliser === au lieu de ==
    if (a == b) {
        return true;
    }
    return false;
}

// Code mort (unreachable)
function deadCode(): string {
    return "returned";
    
    // Code mort - jamais atteint
    const unreachable = "Never executed";
    console.log(unreachable);
    doSomething();
}

function doSomething(): void {
    // FIXME: Implémenter cette fonction
}

// Bug: Modification du prototype
function modifyPrototype(): void {
    // Dangereux: modification du prototype Array
    (Array.prototype as any).customMethod = function() {
        return this.length;
    };
}

// Callback hell
function callbackHell(): void {
    setTimeout(() => {
        console.log("Level 1");
        setTimeout(() => {
            console.log("Level 2");
            setTimeout(() => {
                console.log("Level 3");
                setTimeout(() => {
                    console.log("Level 4");
                    setTimeout(() => {
                        console.log("Level 5");
                    }, 100);
                }, 100);
            }, 100);
        }, 100);
    }, 100);
}

// Faille: Regex DoS
function validateEmail(email: string): boolean {
    // ReDoS vulnerability
    const regex = /^([a-zA-Z0-9]+)*@.*$/;
    return regex.test(email);
}

// Bug: Async/await mal géré
async function poorAsyncHandling(): Promise<void> {
    // Bug: erreur non gérée
    const data = await fetch('https://api.example.com/data');
    const json = await data.json();
    console.log(json);
}

// Code smell: try-catch vide
function emptyCatch(): void {
    try {
        dangerousOperation();
    } catch (error) {
        // Code smell: catch vide
    }
}

function dangerousOperation(): void {
    throw new Error("Something went wrong");
}

// Bug: Boucle infinie potentielle
function infiniteLoopRisk(value: number): number[] {
    const result: number[] = [];
    let counter = value;
    
    // Bug: boucle infinie si value <= 0
    while (counter != 0) {
        result.push(counter);
        counter--;
    }
    
    return result;
}

// Code smell: Chaînes dupliquées
function duplicatedStrings(): void {
    console.log("Error: Invalid user input");
    console.log("Error: Invalid user input");
    console.log("Error: Invalid user input");
    alert("Error: Invalid user input");
}

// Faille: Désactivation de la vérification CORS
function unsafeFetch(url: string): Promise<Response> {
    // Dangereux: mode no-cors
    return fetch(url, {
        mode: 'no-cors',
        credentials: 'include'
    });
}

// Code smell: Switch sans default
function switchWithoutDefault(value: string): string {
    switch (value) {
        case 'a':
            return 'A';
        case 'b':
            return 'B';
        case 'c':
            return 'C';
        // Pas de default!
    }
    return '';
}

// Bug: parseInt sans radix
function parseNumber(value: string): number {
    // Bug: devrait spécifier la base (radix)
    return parseInt(value);
}

// Code smell: Trop de return
function multipleReturns(value: number): string {
    if (value < 0) return 'negative';
    if (value === 0) return 'zero';
    if (value === 1) return 'one';
    if (value < 10) return 'small';
    if (value < 100) return 'medium';
    if (value < 1000) return 'large';
    if (value < 10000) return 'very large';
    return 'huge';
}

// Duplication de code
class UserService1 {
    getUsers(): any[] {
        const url = 'https://api.example.com/users';
        return fetch(url)
            .then(response => response.json())
            .then(data => data.users)
            .catch(error => {
                console.error('Error:', error);
                return [];
            });
    }
}

class UserService2 {
    getProducts(): any[] {
        const url = 'https://api.example.com/products';
        return fetch(url)
            .then(response => response.json())
            .then(data => data.users)
            .catch(error => {
                console.error('Error:', error);
                return [];
            });
    }
}

// TODO: Optimiser cette classe
// FIXME: Gérer les erreurs correctement
class IncompleteClass {
    // Variables non initialisées
    private data: any;
    private config: any;
    
    constructor() {
        // FIXME: Initialiser les propriétés
    }
    
    // TODO: Implémenter cette méthode
    process(): void {
        // Code vide
    }
}

// Faille: Hardcoded credentials
const API_KEY = 'sk-1234567890abcdefghijklmnopqrstuvwxyz';
const PASSWORD = 'admin123';
const SECRET_TOKEN = 'secret-token-12345';

// Export pour éviter erreurs de compilation
export {
    executeUserCode,
    renderUserContent,
    processData,
    getUserName,
    complexValidation,
    calculatePriceWithTax1,
    calculatePriceWithTax2,
    debugFunction,
    calculateAverage,
    unusedVariables,
    applyDiscount,
    createUser,
    saveUserData,
    compareValues,
    deadCode,
    modifyPrototype,
    callbackHell,
    validateEmail,
    poorAsyncHandling,
    emptyCatch,
    infiniteLoopRisk,
    duplicatedStrings,
    unsafeFetch,
    switchWithoutDefault,
    parseNumber,
    multipleReturns,
    UserService1,
    UserService2,
    IncompleteClass
};
