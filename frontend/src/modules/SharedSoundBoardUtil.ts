
class SharedSoundBoardUtil {


    public static isSlavePage(): boolean {
        return SharedSoundBoardUtil.getSlaveUrl() !== null;
    }

    public static getSlaveUrl(): string | null {
        const activeWS = document.getElementById('active-WS')
        if (activeWS) {
            return activeWS.dataset.url || null;
        }
        return null;
    }

}

export default SharedSoundBoardUtil;