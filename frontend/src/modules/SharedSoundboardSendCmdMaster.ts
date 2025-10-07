import SharedSoundBoardWebSocket from "@/modules/SharedSoundBoardWebSocket.js";
import SharedSoundBoardUtil from "@/modules/SharedSoundBoardUtil.js";

class SharedSoundboardSendCmdMaster {
    private readonly webSocket: SharedSoundBoardWebSocket | null = null;

    constructor() {
        const url = SharedSoundBoardUtil.getSlaveUrl()
        if (url) {
            this.webSocket = SharedSoundBoardWebSocket.getSlaveInstance(url);
            this.webSocket.start();
        }
    }

    public sendPlayPlaylistOnMaster(PlaylistUuid: string) {
        if (!this.webSocket) return;
            this.webSocket.sendMessage({ type: 'player_play_on_master', data: { 'playlist_uuid': PlaylistUuid } });
    }

}

export default SharedSoundboardSendCmdMaster;