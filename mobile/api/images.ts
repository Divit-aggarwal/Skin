import { apiClient } from './client';
import type { ImageOut } from './types';

export const imagesApi = {
  upload: (imageData: string, mimeType: string) =>
    apiClient.post<ImageOut>('/images/upload', {
      image_data: imageData,
      mime_type: mimeType,
    }),
};
