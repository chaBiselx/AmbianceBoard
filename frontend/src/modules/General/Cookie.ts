
class Cookie {

    static get(name: string) {
        let cookieValue = null;
        if (document.cookie && document.cookie != '') {
            let cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                if (cookie.trim().substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    if(cookieValue.startsWith('="') && cookieValue.endsWith('"')) {
                        cookieValue = cookieValue.substring(2, cookieValue.length - 1);
                    }
                    break;
                }
            }
           
        }
        return cookieValue;
    }

    static set(name: string, value: string) {
        let date = new Date();
        date.setTime(date.getTime() + (7 * 24 * 60 * 60 * 1000));
        let expires = "expires=" + date.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

}

export default Cookie;

