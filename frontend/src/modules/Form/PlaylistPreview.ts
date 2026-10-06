export function renderPlaylistPreview(doc: Document = document): void {
    const demo = doc.getElementById('demo-playlist') as HTMLDivElement | null;
    if (!demo) return;

    const useSpecificColor = doc.getElementById('id_useSpecificColor') as HTMLInputElement | null;
    if (useSpecificColor?.checked) {
        const color = doc.getElementById('id_color') as HTMLInputElement | null;
        const colorText = doc.getElementById('id_colorText') as HTMLInputElement | null;
        if (color && colorText) {
            demo.style.backgroundColor = color.value;
            demo.style.color = colorText.value;
        }
    } else {
        const typePlaylist = doc.getElementById('id_typePlaylist') as HTMLInputElement | null;
        const color = typePlaylist && doc.getElementById(`default_${typePlaylist.value}_color`) as HTMLInputElement | null;
        const colorText = typePlaylist && doc.getElementById(`default_${typePlaylist.value}_colorText`) as HTMLInputElement | null;
        if (color && colorText) {
            demo.style.backgroundColor = color.value;
            demo.style.color = colorText.value;
        }
    }

    const iconInput = doc.getElementById('id_icon') as HTMLInputElement | null;
    const existingIcon = doc.getElementById('id_icon_alreadyexist') as HTMLLinkElement | null;
    if (iconInput?.files?.[0]) {
        const reader = new FileReader();
        reader.addEventListener('load', () => {
            const image = doc.createElement('img');
            image.className = 'playlist-img';
            image.src = reader.result?.toString() || '';
            demo.replaceChildren(image);
        });
        reader.readAsDataURL(iconInput.files[0]);
    } else if (existingIcon) {
        const image = doc.createElement('img');
        image.className = 'playlist-img';
        image.src = existingIcon.href;
        demo.replaceChildren(image);
    } else {
        const name = doc.getElementById('id_name') as HTMLInputElement | null;
        demo.textContent = name?.value ?? '';
    }
}
