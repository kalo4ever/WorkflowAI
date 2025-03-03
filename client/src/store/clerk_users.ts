import { enableMapSet, produce } from 'immer';
import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { client } from '@/lib/api';
import { User } from '@/types/user';

enableMapSet();

interface ClerkUserState {
  // Record instead of Map becasue Map is not correctly supported with the zustand persist
  usersByID: Record<string, User>;
  isLoadingById: Record<string, boolean>;
  isInitializedById: Record<string, boolean>;
  fetchClerkUser: (userId: string) => Promise<User | undefined>;
  fetchClerkUsers: (userIds: string[]) => Promise<void>;
}

export const useClerkUserStore = create<ClerkUserState>()(
  persist(
    (set, get) => ({
      usersByID: {},
      isLoadingById: {},
      isInitializedById: {},
      fetchClerkUser: async (userId: string) => {
        const currentUser = get().usersByID[userId];
        if (currentUser) {
          return currentUser;
        }
        if (get().isLoadingById[userId]) return;
        set(
          produce((state) => {
            state.isLoadingById[userId] = true;
          })
        );
        let user: User | undefined;
        try {
          user = await client.get<User>(`/api/users/${userId}`);
          set(
            produce((state) => {
              state.usersByID[userId] = user;
            })
          );
        } catch (error) {
          console.error('Error fetching Clerk user:', error);
        }
        set(
          produce((state) => {
            state.isLoadingById[userId] = false;
            state.isInitializedById[userId] = true;
          })
        );
        return user;
      },
      fetchClerkUsers: async (userIds: string[]) => {
        await Promise.all(userIds.map(get().fetchClerkUser));
      },
    }),
    {
      name: 'clerk-user-storage',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
