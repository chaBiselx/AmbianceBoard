import Time from "@/modules/Util/Time";

class Cookie {

    static get(name: string) {
        let cookieValue = null;
        if (document.cookie && document.cookie != '') {
            let cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const labelFromCookie: string = cookie.trim().substring(0, cookie.indexOf('=') - 1);
                if (labelFromCookie === name) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 2));
                    if(cookieValue.startsWith('"') && cookieValue.endsWith('"')) {
                        cookieValue = cookieValue.substring(1, cookieValue.length - 1);
                    }
                    break;
                }
            }
           
        }
        return cookieValue;
    }

    static set(name: string, value: string) {
        let date = new Date();
        date.setTime(date.getTime() + Time.get_days(7));
        let expires = "expires=" + date.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

}

export default Cookie;

