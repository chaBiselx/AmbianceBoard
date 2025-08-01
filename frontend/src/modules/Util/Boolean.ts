

class Boolean {

    static convert(value: string | boolean): boolean {
        if (typeof value === 'boolean') {
            return value;
        }
        if (typeof value === 'string') {
            const lowerValue = value.toLowerCase();
            return lowerValue === 'true';
        }
        return false;
    }

}

export default Boolean;