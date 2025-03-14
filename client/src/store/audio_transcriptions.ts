import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { client } from '@/lib/api';
import { RequestError } from '@/lib/api/client';
import { FileInputRequest } from '@/types/workflowAI';
import { api__routers__transcriptions__TranscriptionResponse } from '@/types/workflowAI';
import { rootTenantPath } from './utils';

enableMapSet();

interface AudioTranscriptionsState {
  // Record instead of Map becasue Map is not correctly supported with the zustand persist
  audioTranscriptionsById: Record<string, string>;
  isLoadingById: Record<string, boolean>;
  isInitializedById: Record<string, boolean>;
  fetchAudioTranscription: (
    payload: FileInputRequest
  ) => Promise<string | undefined>;
}

export const useAudioTranscriptions = create<AudioTranscriptionsState>()(
  persist(
    (set, get) => ({
      audioTranscriptionsById: {},
      isLoadingById: {},
      isInitializedById: {},
      fetchAudioTranscription: async (payload: FileInputRequest) => {
        const fileId = payload.file_id;
        const currentTranscription = get().audioTranscriptionsById[fileId];
        if (currentTranscription) {
          return currentTranscription;
        }
        if (get().isLoadingById[fileId]) return;
        set(
          produce((state) => {
            state.isLoadingById[fileId] = true;
          })
        );
        let transcription:
          | api__routers__transcriptions__TranscriptionResponse
          | undefined;
        try {
          transcription =
            await client.get<api__routers__transcriptions__TranscriptionResponse>(
              `${rootTenantPath()}/transcriptions/${fileId}`
            );
        } catch (error) {
          if ((error as RequestError)?.status === 404) {
            try {
              transcription = await client.post<
                FileInputRequest,
                api__routers__transcriptions__TranscriptionResponse
              >(`${rootTenantPath()}/transcriptions`, payload);
            } catch (error) {
              set(
                produce((state) => {
                  state.isLoadingById[fileId] = false;
                  state.isInitializedById[fileId] = true;
                })
              );
              console.error('Error creating audio transcription:', error);
              throw error;
            }
          } else {
            console.error('Error fetching audio transcription:', error);
          }
        }
        if (!!transcription) {
          set(
            produce((state) => {
              state.audioTranscriptionsById[fileId] =
                transcription?.transcription;
            })
          );
        }
        set(
          produce((state) => {
            state.isLoadingById[fileId] = false;
            state.isInitializedById[fileId] = true;
          })
        );
        return transcription?.transcription;
      },
    }),
    {
      name: 'audio-transcription-storage',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
