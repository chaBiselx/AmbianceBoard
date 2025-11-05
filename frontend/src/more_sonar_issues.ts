/**
 * Plus de problèmes JavaScript/TypeScript pour la démo SonarQube
 */

// FIXME: Réécrire ce fichier
// TODO: Ajouter de la documentation

// Code smell: var au lieu de let/const
var oldStyleVariable = "Should use let or const";
var anotherOldVar = 123;

// Faille: document.write (XSS)
function unsafeWrite(userInput: string): void {
    document.write(userInput);
}

// Faille: location.href sans validation
function unsafeRedirect(url: string): void {
    window.location.href = url;
}

// Bug: Comparaison avec NaN
function checkNaN(value: number): boolean {
    // Bug: NaN !== NaN
    if (value === NaN) {
        return true;
    }
    return false;
}

// Code smell: Fonction trop longue
function monsterFunction(data: any): any {
    const result: any = {};
    
    // Validation 1
    if (!data.field1) {
        result.error = "Field1 required";
        return result;
    }
    
    // Validation 2
    if (!data.field2) {
        result.error = "Field2 required";
        return result;
    }
    
    // Validation 3
    if (!data.field3) {
        result.error = "Field3 required";
        return result;
    }
    
    // Process field1
    const processed1 = data.field1.trim().toLowerCase();
    if (processed1.length < 3) {
        result.error = "Field1 too short";
        return result;
    }
    
    // Process field2
    const processed2 = data.field2.trim().toLowerCase();
    if (processed2.length < 5) {
        result.error = "Field2 too short";
        return result;
    }
    
    // Process field3
    const processed3 = data.field3.trim().toLowerCase();
    if (processed3.length < 10) {
        result.error = "Field3 too short";
        return result;
    }
    
    // Calculate something
    let total = 0;
    for (let i = 0; i < data.items.length; i++) {
        const item = data.items[i];
        if (item.price) {
            total += item.price;
            if (item.quantity) {
                total = total * item.quantity;
            }
            if (item.discount) {
                total = total - (total * item.discount);
            }
            if (item.tax) {
                total = total + (total * item.tax);
            }
        }
    }
    
    // More processing
    result.total = total;
    result.processed1 = processed1;
    result.processed2 = processed2;
    result.processed3 = processed3;
    
    // TODO: Continuer le traitement
    // FIXME: Cette partie est incomplète
    
    return result;
}

// Duplication de code
function validateUsername1(username: string): boolean {
    if (!username) return false;
    if (username.length < 3) return false;
    if (username.length > 20) return false;
    if (!/^[a-zA-Z0-9_]+$/.test(username)) return false;
    return true;
}

function validateUsername2(username: string): boolean {
    if (!username) return false;
    if (username.length < 3) return false;
    if (username.length > 20) return false;
    if (!/^[a-zA-Z0-9_]+$/.test(username)) return false;
    return true;
}

// Faille: setTimeout avec string
function dangerousTimeout(code: string): void {
    // Dangereux: comme eval()
    setTimeout(code, 1000);
}

// Bug: Array index sans vérification
function getFirstElement(arr: any[]): any {
    // Bug: pas de vérification si tableau vide
    return arr[0];
}

// Code smell: Nested ternaries
function nestedTernary(value: number): string {
    return value > 100 
        ? value > 200 
            ? value > 300 
                ? "very high" 
                : "high" 
            : "medium" 
        : "low";
}

// Faille: postMessage sans vérification de l'origine
function unsafePostMessage(data: any): void {
    // Dangereux: targetOrigin = "*"
    window.parent.postMessage(data, "*");
}

// Bug: Promise sans catch
function unhandledPromise(): void {
    fetch('https://api.example.com/data')
        .then(response => response.json())
        .then(data => console.log(data));
    // Pas de .catch() !
}

// Code smell: Trop de callbacks
function pyramidOfDoom(callback: Function): void {
    getData((data1: any) => {
        processData1(data1, (result1: any) => {
            validateResult(result1, (valid: boolean) => {
                if (valid) {
                    saveData(result1, (saved: boolean) => {
                        if (saved) {
                            notifyUser((notified: boolean) => {
                                if (notified) {
                                    callback(true);
                                }
                            });
                        }
                    });
                }
            });
        });
    });
}

// Fonctions mock pour l'exemple ci-dessus
function getData(cb: Function): void { cb({}); }
function processData1(data: any, cb: Function): void { cb(data); }
function validateResult(result: any, cb: Function): void { cb(true); }
function saveData(data: any, cb: Function): void { cb(true); }
function notifyUser(cb: Function): void { cb(true); }

// Bug: Modification d'un const object
function modifyConstObject(): void {
    const config = {
        debug: false,
        timeout: 5000
    };
    
    // Techniquement possible mais code smell
    config.debug = true;
    config.timeout = 10000;
}

// Faille: eval déguisé avec Function
function hiddenEval(code: string): any {
    // Équivalent à eval()
    return new Function('return ' + code)();
}

// Code smell: Magic strings
function handleAction(action: string): void {
    if (action === "CREATE_USER") {
        console.log("Creating user");
    } else if (action === "UPDATE_USER") {
        console.log("Updating user");
    } else if (action === "DELETE_USER") {
        console.log("Deleting user");
    } else if (action === "FETCH_USERS") {
        console.log("Fetching users");
    }
}

// Bug: Type coercion implicite
function implicitCoercion(value: any): boolean {
    // Code smell: conversion implicite
    if (value) {
        return true;
    }
    return false;
}

// Code smell: Assignment dans condition
function assignmentInCondition(): boolean {
    let value;
    // Code smell: assignment au lieu de comparison
    if (value = getValue()) {
        return true;
    }
    return false;
}

function getValue(): any {
    return "some value";
}

// Faille: Weak random pour sécurité
function generateToken(): string {
    // Pas cryptographiquement sûr
    return Math.random().toString(36).substring(7);
}

// Bug: Modification de paramètre
function modifyParameter(arr: any[]): any[] {
    // Anti-pattern: modifier le paramètre
    arr.push("new item");
    arr.sort();
    return arr;
}

// Code smell: Empty block
function emptyBlocks(value: number): void {
    if (value > 0) {
        // Block vide
    } else {
        console.log("negative");
    }
    
    try {
        riskyOperation();
    } catch (e) {
        // Catch vide
    }
}

function riskyOperation(): void {
    throw new Error("Error");
}

// TODO: Terminer cette classe
// FIXME: Corriger l'architecture
class BadClass {
    // Variables publiques (devrait être private)
    public internalState: any;
    public secretData: string;
    
    // Pas de constructor
    
    // Méthode sans type de retour explicite
    doSomething(param) {
        return param;
    }
    
    // TODO: Ajouter validation
    setData(data: any) {
        this.internalState = data;
    }
}

// Faille: innerHTML dans une boucle
function renderList(items: string[]): void {
    const container = document.getElementById('list');
    if (container) {
        let html = '';
        for (const item of items) {
            // XSS vulnerability
            html += '<li>' + item + '</li>';
        }
        container.innerHTML = html;
    }
}

// Code smell: Fonction qui fait trop de choses
function doEverything(user: any): void {
    // Validation
    if (!user.email) throw new Error("Email required");
    
    // Transformation
    user.email = user.email.toLowerCase();
    
    // API call
    fetch('/api/users', {
        method: 'POST',
        body: JSON.stringify(user)
    });
    
    // Update UI
    document.getElementById('status')!.textContent = 'User created';
    
    // Log
    console.log('User created:', user);
    
    // Analytics
    sendAnalytics('user_created', user);
    
    // Notification
    showNotification('Success!');
}

function sendAnalytics(event: string, data: any): void {}
function showNotification(message: string): void {}

// FIXME: Cette ligne ne devrait pas être là
debugger;

// Export
export {
    unsafeWrite,
    unsafeRedirect,
    checkNaN,
    monsterFunction,
    validateUsername1,
    validateUsername2,
    dangerousTimeout,
    getFirstElement,
    nestedTernary,
    unsafePostMessage,
    unhandledPromise,
    pyramidOfDoom,
    modifyConstObject,
    hiddenEval,
    handleAction,
    implicitCoercion,
    assignmentInCondition,
    generateToken,
    modifyParameter,
    emptyBlocks,
    BadClass,
    renderList,
    doEverything
};
