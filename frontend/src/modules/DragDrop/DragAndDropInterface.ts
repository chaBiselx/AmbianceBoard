/**
 * Interface pour la configuration de base d'un système de drag & drop
 */
interface IDropAndDropConfig {
    containerSelector: string;
    uploadUrl: string;
    acceptedFiles?: string;
    uploadMultiple?: boolean;
    parallelUploads?: number;
    createImageThumbnails?: boolean;
    addRemoveLinks?: boolean;
    headers?: Record<string, string>;
    paramName?: string;
    method?: string;
}

/**
 * Interface pour les callbacks du système de drag & drop
 */
interface IDropZoneCallbacks {
    onFileAdded?: (file: File) => void;
    onUploadSuccess?: (files: File | File[] | FileList, response: any) => void;
    onUploadError?: (files: File | File[] | FileList, error: any) => void;
}

/**
 * Interface pour les réponses d'upload
 */
interface IUploadResponse {
    success: boolean;
    errors?: string[];
    [key: string]: any;
}

/**
 * Interface abstraite pour un système de drag & drop
 */
interface IDropZoneAdapter {
    initialize(): void;
    destroy(): void;
}

/**
 * Interface pour la configuration les reponses
 */
interface IUploadResponse {
    success: boolean;
    uploaded_files?: Array<{
        id: number;
        filename: string;
        alternativeName: string;
    }>;
    errors?: string[];
}

export type {IDropAndDropConfig, IDropZoneCallbacks, IDropZoneAdapter, IUploadResponse}
