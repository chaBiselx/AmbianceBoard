export interface TimeSeriesDataItem {
    date: string;
    count: number;
}

export class DataProcessor {
    
    /**
     * Génère une liste complète de dates entre deux dates
     * @param startDate Date de début
     * @param endDate Date de fin
     * @returns Array de dates au format YYYY-MM-DD
     */
    static generateDateRange(startDate: string | Date, endDate: string | Date): string[] {
        const start = new Date(startDate);
        const end = new Date(endDate);
        const dateLabels: string[] = [];
        
        // Vérification que la date de début est antérieure à la date de fin
        if (start > end) {
            throw new Error('La date de début doit être antérieure à la date de fin');
        }
        
        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            dateLabels.push(d.toISOString().split('T')[0]); // Format YYYY-MM-DD
        }
        
        return dateLabels;
    }
    
    /**
     * Transforme un tableau de données temporelles en dictionnaire pour accès rapide
     * @param data Tableau d'objets avec date et count
     * @returns Dictionnaire {date: count}
     */
    static createDataDictionary(data: TimeSeriesDataItem[]): { [key: string]: number } {
        const dictionary: { [key: string]: number } = {};
        
        data.forEach((item: TimeSeriesDataItem) => {
            if (item.date && typeof item.count === 'number') {
                dictionary[item.date] = item.count;
            }
        });
        
        return dictionary;
    }
    
    /**
     * Remplit les données manquantes avec des zéros pour une période donnée
     * @param dateLabels Liste des dates à couvrir
     * @param dataDict Dictionnaire des données existantes
     * @param defaultValue Valeur par défaut pour les jours manquants (défaut: 0)
     * @returns Array des valeurs complétées
     */
    static fillMissingDatas(
        dateLabels: string[], 
        dataDict: { [key: string]: number }, 
        defaultValue: number = 0
    ): number[] {
        return dateLabels.map(date => dataDict[date] ?? defaultValue);
    }
    
    /**
     * Valide que les données requises sont présentes
     * @param data Objet de données à valider
     * @param requiredFields Champs requis
     * @throws Error si des champs requis sont manquants
     */
    static validateRequiredData(data: any, requiredFields: string[]): void {
        const missingFields = requiredFields.filter(field => {
            const value = data[field];
            return value === undefined || value === null;
        });
        
        if (missingFields.length > 0) {
            throw new Error(`Champs requis manquants: ${missingFields.join(', ')}`);
        }
    }
}
