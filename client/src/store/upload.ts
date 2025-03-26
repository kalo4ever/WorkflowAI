import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { client } from '@/lib/api';
import { API_URL } from '@/lib/constants';
import { TaskID, TenantID } from '@/types/aliases';
import { UploadFileResponse } from '@/types/workflowAI';

enableMapSet();

interface UploadState {
  // Record instead of Map becasue Map is not correctly supported with the zustand persist
  uploadURLsByHash: Record<string, string>;
  getUploadURL: ({
    tenant,
    taskId,
    form,
    hash,
    token,
    onProgress,
  }: {
    tenant: TenantID;
    taskId: TaskID;
    form: FormData;
    hash: string;
    token: string;
    onProgress?: (progress: number) => void;
  }) => Promise<string>;
}

export const useUpload = create<UploadState>()(
  persist(
    (set, get) => ({
      uploadURLsByHash: {},
      getUploadURL: async ({ tenant, taskId, form, hash, token, onProgress }) => {
        const existing = get().uploadURLsByHash[hash];
        if (existing) return existing;
        const { url } = await client.uploadFile<UploadFileResponse>(
          `${API_URL}/${tenant}/upload/${taskId}`,
          form,
          token,
          onProgress
        );
        set(
          produce((state) => {
            state.uploadURLsByHash[hash] = url;
          })
        );
        return url;
      },
    }),
    {
      name: 'upload-storage',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
