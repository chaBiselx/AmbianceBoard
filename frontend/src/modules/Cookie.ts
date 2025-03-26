
class Cookie {

    static get(name: string) {
        let cookieValue = null;
        if (document.cookie && document.cookie != '') {
            let cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                if (cookie.trim().substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
           
        }
        return cookieValue;
    }

}

export default Cookie;

