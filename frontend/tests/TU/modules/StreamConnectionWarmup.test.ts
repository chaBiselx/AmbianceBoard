import { beforeEach, describe, expect, it } from 'vitest';
import StreamConnectionWarmup from '@/modules/StreamConnectionWarmup';

describe('StreamConnectionWarmup', () => {
    beforeEach(() => {
        document.head.innerHTML = '';
        document.body.innerHTML = '';
    });

    it('adds DNS and preconnect hints once per playlist origin', () => {
        document.body.innerHTML = `
            <a class="playlist-link" data-playlist-uri="https://cdn.example.test/audio/one.mp3"></a>
            <a class="playlist-link" data-playlist-uri="https://cdn.example.test/audio/two.mp3"></a>
            <a class="playlist-link" data-playlist-uri="/media/local.mp3"></a>
        `;

        new StreamConnectionWarmup().initialize();

        const preconnectHints = [...document.head.querySelectorAll('link[rel="preconnect"]')];
        const dnsHints = [...document.head.querySelectorAll('link[rel="dns-prefetch"]')];
        expect(preconnectHints.map((link) => link.getAttribute('href'))).toEqual([
            'https://cdn.example.test',
            'http://localhost:3000',
        ]);
        expect(dnsHints.map((link) => link.getAttribute('href'))).toEqual([
            'https://cdn.example.test',
            'http://localhost:3000',
        ]);
    });

    it('ignores playlist elements without a URI and malformed URLs', () => {
        document.body.innerHTML = `
            <a class="playlist-link"></a>
            <a class="playlist-link" data-playlist-uri="http://[invalid"></a>
        `;

        new StreamConnectionWarmup().initialize();

        expect(document.head.querySelectorAll('link')).toHaveLength(0);
    });

    it('does not add duplicate hints that are already in the document', () => {
        document.head.innerHTML = '<link rel="preconnect" href="https://cdn.example.test">';
        document.body.innerHTML = '<a class="playlist-link" data-playlist-uri="https://cdn.example.test/audio.mp3"></a>';

        new StreamConnectionWarmup().initialize();

        expect(document.head.querySelectorAll('link[rel="preconnect"]')).toHaveLength(1);
        expect(document.head.querySelectorAll('link[rel="dns-prefetch"]')).toHaveLength(1);
    });
});