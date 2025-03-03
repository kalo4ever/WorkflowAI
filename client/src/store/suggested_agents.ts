import { produce } from 'immer';
import { create } from 'zustand';
import { Method, SSEClient } from '@/lib/api/client';
import { API_URL } from '@/lib/constants';
import { Provider } from '../types/workflowAI/models';

function isBrowser(): boolean {
  return typeof window !== 'undefined';
}

export type ProviderConfig = {
  provider: Provider;
};

export type SuggestedAgent = {
  agent_description: string;
  department: string;
  explanation: string;
  input_specifications: string;
  output_specifications: string;
};

function filterUsableStreamedAgents(
  streamedAgents: SuggestedAgent[] | undefined
) {
  if (!streamedAgents) {
    return undefined;
  }

  return streamedAgents.filter((agent) => {
    return (
      !!agent.agent_description &&
      !!agent.department &&
      !!agent.explanation &&
      !!agent.input_specifications &&
      !!agent.output_specifications
    );
  });
}

export type SuggestedAgentsChatMessage = {
  role?: 'USER' | 'ASSISTANT';
  content_str?: string;
  suggested_agents?: SuggestedAgent[];
};

export type SuggestedAgentsRequest = {
  messages: SuggestedAgentsChatMessage[];
};

export type SuggestedAgentsResponse = {
  assistant_message?: SuggestedAgentsChatMessage;
};

interface SuggestedAgentsState {
  isLoadingByURL: Record<string, boolean>;
  isInitializedByURL: Record<string, boolean>;

  initialSuggestedAgentsByURL: Record<string, SuggestedAgent[]>;
  initialMessagesByURL: Record<string, SuggestedAgentsChatMessage[]>;

  suggestedAgentsByURL: Record<string, SuggestedAgent[]>;
  messagesByURL: Record<string, SuggestedAgentsChatMessage[]>;

  streamedAgentsByURL: Record<string, SuggestedAgent[]>;

  resetToInitialState: (companyURL: string) => void;
  reset: (companyURL: string) => void;
  fetchSuggestedAgents: (
    companyURL: string,
    messages?: SuggestedAgentsChatMessage[]
  ) => Promise<void>;
  sendMessage: (companyURL: string, text: string) => Promise<void>;
}

const loadSuggestedAgentsFromStorage = (): Partial<SuggestedAgentsState> => {
  if (!isBrowser()) {
    return {};
  }

  try {
    const stored = localStorage.getItem('persistedSuggestedAgents');
    if (stored) {
      const parsed = JSON.parse(stored);
      return {
        isInitializedByURL: parsed.isInitializedByURL || {},

        initialSuggestedAgentsByURL: parsed.initialSuggestedAgentsByURL || {},
        initialMessagesByURL: parsed.initialMessagesByURL || {},

        suggestedAgentsByURL: parsed.suggestedAgentsByURL || {},
        messagesByURL: parsed.messagesByURL || {},
      };
    }
  } catch (error) {
    console.error('Error loading suggested agents from storage:', error);
  }
  return {};
};

export const useSuggestedAgents = create<SuggestedAgentsState>((set, get) => ({
  isLoadingByURL: {},
  isInitializedByURL: loadSuggestedAgentsFromStorage().isInitializedByURL || {},

  initialSuggestedAgentsByURL:
    loadSuggestedAgentsFromStorage().initialSuggestedAgentsByURL || {},

  initialMessagesByURL:
    loadSuggestedAgentsFromStorage().initialMessagesByURL || {},

  suggestedAgentsByURL:
    loadSuggestedAgentsFromStorage().suggestedAgentsByURL || {},

  messagesByURL: loadSuggestedAgentsFromStorage().messagesByURL || {},

  streamedAgentsByURL: {},

  reset: (companyURL: string) => {
    set(
      produce((state: SuggestedAgentsState) => {
        state.isInitializedByURL[companyURL] = false;
        state.suggestedAgentsByURL[companyURL] = [];
        state.messagesByURL[companyURL] = [];
        state.initialSuggestedAgentsByURL[companyURL] = [];
        state.initialMessagesByURL[companyURL] = [];

        const item = JSON.stringify({
          isInitializedByURL: false,
          suggestedAgentsByURL: [],
          messagesByURL: [],
          initialSuggestedAgentsByURL: [],
          initialMessagesByURL: [],
        });

        localStorage.setItem('persistedSuggestedAgents', item);
      })
    );
  },

  resetToInitialState: (companyURL: string) => {
    set(
      produce((state: SuggestedAgentsState) => {
        state.suggestedAgentsByURL[companyURL] = [
          ...(state.initialSuggestedAgentsByURL[companyURL] || []),
        ];

        state.messagesByURL[companyURL] = [
          ...(state.initialMessagesByURL[companyURL] || []),
        ];

        const item = JSON.stringify({
          isInitializedByURL: state.isInitializedByURL,
          suggestedAgentsByURL: state.suggestedAgentsByURL,
          messagesByURL: state.messagesByURL,
          initialSuggestedAgentsByURL: state.initialSuggestedAgentsByURL,
          initialMessagesByURL: state.initialMessagesByURL,
        });

        localStorage.setItem('persistedSuggestedAgents', item);
      })
    );
  },

  fetchSuggestedAgents: async (
    companyURL: string,
    messages?: SuggestedAgentsChatMessage[]
  ) => {
    const initialFetch = !messages;

    const isLoading = get().isLoadingByURL[companyURL];
    const suggestedAgents = get().suggestedAgentsByURL[companyURL];

    if (!!isLoading && !!initialFetch) {
      return;
    }

    if (!!suggestedAgents && suggestedAgents.length > 0 && !!initialFetch) {
      return;
    }

    set(
      produce((state: SuggestedAgentsState) => {
        state.isLoadingByURL[companyURL] = true;
        state.streamedAgentsByURL[companyURL] = [];
      })
    );

    const firstMessage: SuggestedAgentsChatMessage = {
      role: 'USER',
      content_str: `I'm working in ${companyURL}`,
    };

    const areThereMessages = !!messages && messages.length > 0;
    const messagesToSend = areThereMessages ? messages : [firstMessage];

    const request: SuggestedAgentsRequest = {
      messages: messagesToSend,
    };

    const updateMessages = (response: SuggestedAgentsResponse) => {
      const updatedMessages = !!response.assistant_message
        ? [...messagesToSend, response.assistant_message]
        : messagesToSend;

      set(
        produce((state: SuggestedAgentsState) => {
          state.messagesByURL[companyURL] = updatedMessages;

          const agents = filterUsableStreamedAgents(
            response.assistant_message?.suggested_agents
          );

          if (!!agents && agents.length > 0) {
            state.streamedAgentsByURL[companyURL] = agents;
          } else {
            delete state.streamedAgentsByURL[companyURL];
          }
        })
      );
    };

    try {
      const response = await SSEClient<
        SuggestedAgentsRequest,
        SuggestedAgentsResponse
      >(
        `${API_URL}/agents/home/messages`,
        Method.POST,
        undefined,
        request,
        updateMessages
      );

      set(
        produce((state: SuggestedAgentsState) => {
          const agents = response.assistant_message?.suggested_agents;
          const updatedMessages = !!response.assistant_message
            ? [...messagesToSend, response.assistant_message]
            : messagesToSend;

          if (!!agents) {
            state.suggestedAgentsByURL[companyURL] = agents;
            if (!!initialFetch) {
              state.initialSuggestedAgentsByURL[companyURL] = agents;
            }
          } else {
            delete state.suggestedAgentsByURL[companyURL];
            if (!!initialFetch) {
              delete state.initialSuggestedAgentsByURL[companyURL];
            }
          }

          state.messagesByURL[companyURL] = updatedMessages;
          if (!!initialFetch) {
            state.initialMessagesByURL[companyURL] = updatedMessages;
          }

          state.isInitializedByURL[companyURL] = true;
          delete state.streamedAgentsByURL[companyURL];

          localStorage.setItem(
            'persistedSuggestedAgents',
            JSON.stringify({
              isInitializedByURL: state.isInitializedByURL,

              suggestedAgentsByURL: state.suggestedAgentsByURL,
              messagesByURL: state.messagesByURL,

              initialSuggestedAgentsByURL: state.initialSuggestedAgentsByURL,
              initialMessagesByURL: state.initialMessagesByURL,
            })
          );
        })
      );
    } finally {
      set(
        produce((state: SuggestedAgentsState) => {
          state.isLoadingByURL[companyURL] = false;
          state.isInitializedByURL[companyURL] = true;
          delete state.streamedAgentsByURL[companyURL];
        })
      );
    }
  },

  sendMessage: async (companyURL: string, text: string) => {
    const messages = get().messagesByURL[companyURL];
    const newMessages: SuggestedAgentsChatMessage[] = [
      ...messages,
      { role: 'USER', content_str: text },
    ];
    await get().fetchSuggestedAgents(companyURL, newMessages);
  },
}));

export function buildSuggestedAgentPreviewScopeKey(props: {
  agent: SuggestedAgent | undefined;
}) {
  if (!props.agent) {
    return undefined;
  }
  return `${props.agent.department}-${props.agent.agent_description}-${props.agent.explanation}-${props.agent.input_specifications}-${props.agent.output_specifications}`;
}

export type SuggestedAgentPreview = {
  agent_output_example: Record<string, unknown>;
  agent_input_example: Record<string, unknown>;
  agent_input_schema: Record<string, unknown>;
  agent_output_schema: Record<string, unknown>;
};

export type SuggestedAgentPreviewRequest = {
  suggested_agent: SuggestedAgent;
};

interface SuggestedAgentPreviewState {
  isLoadingByScope: Map<string, boolean>;
  isInitializedByScope: Map<string, boolean>;
  previewByScope: Map<string, SuggestedAgentPreview>;

  fetchSuggestedTaskPreviewIfNeeded: (agent: SuggestedAgent) => Promise<void>;
}

const loadPreviewFromStorage = (): Partial<SuggestedAgentPreviewState> => {
  if (!isBrowser()) {
    return {};
  }

  try {
    const stored = localStorage.getItem('suggestedAgentPreviews');
    if (stored) {
      const parsed = JSON.parse(stored);
      return {
        previewByScope: new Map(Object.entries(parsed.previewByScope || {})),
        isInitializedByScope: new Map(
          Object.entries(parsed.isInitializedByScope || {})
        ),
      };
    }
  } catch (error) {
    console.error('Error loading agent previews from storage:', error);
  }
  return {};
};

export const useSuggestedAgentPreview = create<SuggestedAgentPreviewState>(
  (set, get) => ({
    isLoadingByScope: new Map(),
    isInitializedByScope:
      loadPreviewFromStorage().isInitializedByScope || new Map(),
    previewByScope: loadPreviewFromStorage().previewByScope || new Map(),

    fetchSuggestedTaskPreviewIfNeeded: async (agent: SuggestedAgent) => {
      const scopeKey = buildSuggestedAgentPreviewScopeKey({ agent });

      if (!!scopeKey && !!get().isLoadingByScope.get(scopeKey)) {
        return;
      }

      if (
        !!scopeKey &&
        !!get().previewByScope.get(scopeKey) &&
        !!get().isInitializedByScope.get(scopeKey)
      ) {
        return;
      }

      set(
        produce((state: SuggestedAgentPreviewState) => {
          if (!scopeKey) {
            return;
          }
          state.isLoadingByScope.set(scopeKey, true);
        })
      );

      const onMessage = (message: SuggestedAgentPreview) => {
        set(
          produce((state: SuggestedAgentPreviewState) => {
            if (!scopeKey) {
              return;
            }
            state.previewByScope.set(scopeKey, message);
          })
        );
      };

      try {
        const response = await SSEClient<
          SuggestedAgentPreviewRequest,
          SuggestedAgentPreview
        >(
          `${API_URL}/agents/home/agents/preview`,
          Method.POST,
          undefined,
          {
            suggested_agent: agent,
          },
          onMessage
        );

        set(
          produce((state: SuggestedAgentPreviewState) => {
            if (!scopeKey) {
              return;
            }
            state.previewByScope.set(scopeKey, response);
            state.isInitializedByScope.set(scopeKey, true);

            localStorage.setItem(
              'suggestedAgentPreviews',
              JSON.stringify({
                previewByScope: Object.fromEntries(state.previewByScope),
                isInitializedByScope: Object.fromEntries(
                  state.isInitializedByScope
                ),
              })
            );
          })
        );
      } finally {
        if (!scopeKey) {
          return;
        }
        set(
          produce((state: SuggestedAgentPreviewState) => {
            state.isLoadingByScope.set(scopeKey, false);
            state.isInitializedByScope.set(scopeKey, true);
          })
        );
      }
    },
  })
);
