class Csrf {
    static getToken(): string | null {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        return csrfToken ? csrfToken : null;
    }
}

export default Csrf;
