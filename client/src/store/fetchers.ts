'use client';

/* eslint-disable max-lines */
// It's ok if this file is long, it's a collection of hooks that fetch data
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useAuth } from '@/lib/AuthContext';
import { USER_SLUG_PREFIX } from '@/lib/auth_utils';
import { useDebounce } from '@/lib/hooks/useDebounce';
import { TENANT_PLACEHOLDER } from '@/lib/routeFormatter';
import { sortVersions } from '@/lib/versionUtils';
import { isNullish } from '@/types';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { CodeLanguage } from '@/types/snippets';
import { ChatMessage, FieldQuery, VersionV1 } from '@/types/workflowAI';
import { useAIModels } from './ai_models';
import { useApiKeys } from './api_keys';
import { useClerkOrganizationStore } from './clerk_organisations';
import { useClerkUserStore } from './clerk_users';
import { useOrganizationSettings } from './organization_settings';
import { usePayments } from './payments';
import { useRunCompletions } from './run_completions';
import {
  SuggestedAgent,
  buildSuggestedAgentPreviewScopeKey,
  useSuggestedAgentPreview,
  useSuggestedAgents,
} from './suggested_agents';
import { useTasks } from './task';
import { useTaskEvaluation } from './task_evaluation';
import { useTaskPreview } from './task_preview';
import { useReviewBenchmark } from './task_review_benchmark';
import { useTaskRunReviews } from './task_run_reviews';
import { useTaskRunTranscriptions } from './task_run_transcriptions';
import { useTaskRuns } from './task_runs';
import { useTaskRunsSearchFields } from './task_runs_search_fields';
import { useTaskSchemas } from './task_schemas';
import { buildSnippetScopeKey, useTaskSnippets } from './task_snippets';
import { useTaskStats } from './task_stats';
import { tokenScopeKey, useToken } from './token';
import {
  buildScopeKey,
  buildSearchTaskRunsScopeKey,
  buildTaskPreviewScopeKey,
  buildTaskStatsScopeKey,
  buildVersionScopeKey,
  getOrUndef,
} from './utils';
import {
  getVersionsPerEnvironment,
  mapMajorVersionsToVersions,
  useVersions,
} from './versions';

type TUseOrFetchAllAiModelsProps = {
  tenant: TenantID | undefined;
  taskId: TaskID;
  taskSchemaId: TaskSchemaID;
};

export function useOrFetchAllAiModels(props: TUseOrFetchAllAiModelsProps) {
  const { tenant, taskId, taskSchemaId } = props;
  const scope = buildScopeKey({ tenant, taskId, taskSchemaId });
  const models = useAIModels((state) => state.modelsByScope.get(scope));
  const isLoading = useAIModels((state) => state.isLoadingByScope.get(scope));
  const isInitialized = useAIModels((state) =>
    state.isInitializedByScope.get(scope)
  );
  const fetchModels = useAIModels((state) => state.fetchModels);

  useEffect(() => {
    if (!isInitialized) {
      fetchModels(tenant, taskId, taskSchemaId);
    }
  }, [isInitialized, fetchModels, tenant, taskId, taskSchemaId]);

  const findIconURLForModel = useCallback(
    (modelId?: string) => {
      if (!modelId || !models) {
        return undefined;
      }

      const model = models.find((model) => model.id === modelId);

      if (!model) {
        return undefined;
      }

      return model.icon_url;
    },
    [models]
  );

  return {
    models: models ?? [],
    isLoading,
    isInitialized,
    findIconURLForModel,
  };
}

export const useOrFetchTaskRuns = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID | undefined,
  searchParams?: string
) => {
  const scope = buildScopeKey({ tenant, taskId, taskSchemaId, searchParams });
  const taskRuns = useTaskRuns((state) => state.taskRunsByScope.get(scope));
  const isLoading = useTaskRuns((state) => state.isLoadingByScope.get(scope));
  const isInitialized = useTaskRuns(
    (state) => state.isInitializedByScope.get(scope) === true
  );
  const fetchTaskRuns = useTaskRuns((state) => state.fetchTaskRuns);
  const count = useTaskRuns((state) => state.countByScope.get(scope));

  useEffect(() => {
    if (!taskSchemaId) {
      return;
    }
    fetchTaskRuns({ tenant, taskId, taskSchemaId, searchParams });
  }, [taskId, searchParams, fetchTaskRuns, taskSchemaId, tenant]);

  return {
    taskRuns,
    isLoading,
    isInitialized,
    count,
  };
};

export const useOrSearchTaskRuns = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  limit: number,
  offset: number,
  fieldQueries: Array<FieldQuery> | undefined
) => {
  const scope = buildSearchTaskRunsScopeKey({
    tenant,
    taskId,
    limit,
    offset,
    fieldQueries,
  });

  const taskRunItems = useTaskRuns((state) =>
    state.taskRunItemsV1ByScope.get(scope)
  );
  const isLoading = useTaskRuns((state) => state.isLoadingByScope.get(scope));
  const isInitialized = useTaskRuns(
    (state) => state.isInitializedByScope.get(scope) === true
  );
  const searchTaskRuns = useTaskRuns((state) => state.searchTaskRuns);
  const count = useTaskRuns((state) => state.countByScope.get(scope));

  useEffect(() => {
    searchTaskRuns({
      tenant,
      taskId,
      limit,
      offset,
      fieldQueries,
    });
  }, [taskId, fieldQueries, limit, offset, searchTaskRuns, tenant]);

  return {
    taskRunItems,
    isLoading,
    isInitialized,
    count,
  };
};

export const useOrFetchTaskRunsSearchFields = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID
) => {
  const scope = buildScopeKey({ tenant, taskId, taskSchemaId });

  const searchFields = useTaskRunsSearchFields((state) =>
    state.searchFieldsByScope.get(scope)
  );
  const isLoading = useTaskRunsSearchFields((state) =>
    state.isLoadingByScope.get(scope)
  );
  const isInitialized = useTaskRunsSearchFields(
    (state) => state.isInitializedByScope.get(scope) === true
  );
  const fetchSearchFields = useTaskRunsSearchFields(
    (state) => state.fetchSearchFields
  );

  useEffect(() => {
    fetchSearchFields({
      tenant,
      taskId,
      taskSchemaId,
    });
  }, [taskId, fetchSearchFields, taskSchemaId, tenant]);

  return {
    searchFields,
    isLoading,
    isInitialized,
  };
};

export function latestTaskRunInputSearchParams() {
  const params = new URLSearchParams();
  params.set('limit', '1');
  params.set('exclude_fields', 'task_output');
  params.append('exclude_fields', 'llm_completions');
  return params.toString();
}

export const useOrFetchLatestTaskRun = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID
) => {
  const searchParams = useMemo(latestTaskRunInputSearchParams, []);

  const { taskRuns, isInitialized, isLoading } = useOrFetchTaskRuns(
    tenant,
    taskId,
    taskSchemaId,
    searchParams
  );

  const fetchTaskRuns = useTaskRuns((state) => state.fetchTaskRuns);

  useEffect(() => {
    // We make sure to fetch the latest task runs when the component unmounts
    // So that when the component mounts again, we don't have a race condition
    // where the latest task runs are not fetched yet, but the component wants to access them
    return () => {
      fetchTaskRuns({ tenant, taskId, taskSchemaId, searchParams });
    };
  }, [taskId, searchParams, fetchTaskRuns, taskSchemaId, tenant]);

  return {
    taskRun: taskRuns?.[0],
    isInitialized,
    isLoading,
  };
};

export const useOrFetchTaskRun = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskRunId: string | undefined
) => {
  const taskRun = useTaskRuns((state) =>
    getOrUndef(state.taskRunsById, taskRunId)
  );
  const isLoading = useTaskRuns((state) =>
    getOrUndef(state.isLoadingById, taskRunId)
  );
  const isInitialized = useTaskRuns(
    (state) => getOrUndef(state.isInitializedById, taskRunId) === true
  );
  const fetchTaskRun = useTaskRuns((state) => state.fetchTaskRun);

  const refresh = useCallback(() => {
    if (taskRunId) {
      fetchTaskRun(tenant, taskId, taskRunId);
    }
  }, [fetchTaskRun, tenant, taskId, taskRunId]);

  useEffect(() => {
    if (!isInitialized) {
      refresh();
    }
  }, [isInitialized, fetchTaskRun, refresh]);

  return {
    taskRun,
    isLoading,
    isInitialized,
    refresh,
  };
};

export const useOrFetchRunV1 = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  runId: string | undefined
) => {
  const run = useTaskRuns((state) => getOrUndef(state.runV1ById, runId));

  const isLoading = useTaskRuns((state) =>
    getOrUndef(state.isRunV1LoadingById, runId)
  );

  const isInitialized = useTaskRuns(
    (state) => getOrUndef(state.isRunV1InitializedById, runId) === true
  );

  const fetchRun = useTaskRuns((state) => state.fetchRunV1);

  const refresh = useCallback(() => {
    if (runId) {
      fetchRun(tenant, taskId, runId);
    }
  }, [fetchRun, tenant, taskId, runId]);

  useEffect(() => {
    if (!isInitialized) {
      refresh();
    }
  }, [isInitialized, fetchRun, refresh]);

  return {
    run,
    isLoading,
    isInitialized,
    refresh,
  };
};

export const useOrFetchTaskRunTranscriptions = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskRunId: string | undefined
) => {
  const transcriptions = useTaskRunTranscriptions((state) =>
    getOrUndef(state.transcriptionsById, taskRunId)
  );
  const isLoading = useTaskRunTranscriptions((state) =>
    getOrUndef(state.isLoadingById, taskRunId)
  );
  const isInitialized = useTaskRunTranscriptions(
    (state) => getOrUndef(state.isInitializedById, taskRunId) === true
  );
  const fetchTaskRunTranscriptions = useTaskRunTranscriptions(
    (state) => state.fetchTaskRunTranscriptions
  );

  useEffect(() => {
    if (taskRunId) {
      fetchTaskRunTranscriptions(tenant, taskId, taskRunId);
    }
  }, [isInitialized, taskRunId, fetchTaskRunTranscriptions, tenant, taskId]);

  return {
    transcriptions,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchTaskRunReviews = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskRunId: string | undefined
) => {
  const reviews = useTaskRunReviews((state) =>
    getOrUndef(state.reviewsById, taskRunId)
  );
  const isLoading = useTaskRunReviews((state) =>
    getOrUndef(state.isLoadingById, taskRunId)
  );
  const isInitialized = useTaskRunReviews(
    (state) => getOrUndef(state.isInitializedById, taskRunId) === true
  );
  const fetchTaskRunReviews = useTaskRunReviews(
    (state) => state.fetchTaskRunReviews
  );

  useEffect(() => {
    if (taskRunId && !isInitialized) {
      fetchTaskRunReviews(tenant, taskId, taskRunId);
    }
  }, [isInitialized, taskRunId, fetchTaskRunReviews, tenant, taskId]);

  const shouldRefetch = useMemo(() => {
    if (!reviews || reviews.length === 0) {
      return true;
    }

    const isThereUserReview = reviews.some(
      (review) => review.created_by.reviewer_type === 'user'
    );

    if (isThereUserReview) {
      return false;
    }

    return true;
  }, [reviews]);

  useEffect(() => {
    if (shouldRefetch) {
      const intervalId = setInterval(() => {
        if (taskRunId) {
          fetchTaskRunReviews(tenant, taskId, taskRunId);
        }
      }, 2000);

      return () => clearInterval(intervalId);
    }
  }, [shouldRefetch, fetchTaskRunReviews, tenant, taskId, taskRunId]);

  return {
    reviews,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchCurrentTaskSchema = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID | undefined
) => {
  const scopeKey = buildScopeKey({ tenant, taskId, taskSchemaId });
  const taskSchema = useTaskSchemas((state) =>
    state.taskSchemasByScope.get(scopeKey)
  );
  const isLoading = useTaskSchemas((state) =>
    state.isTaskSchemaLoadingByScope.get(scopeKey)
  );
  const isInitialized = useTaskSchemas(
    (state) => !!state.isTaskSchemaInitializedByScope.get(scopeKey)
  );
  const fetchTaskSchema = useTaskSchemas((state) => state.fetchTaskSchema);

  useEffect(() => {
    if (!taskId || !taskSchemaId) {
      return;
    }
    fetchTaskSchema(tenant, taskId, taskSchemaId);
  }, [fetchTaskSchema, taskId, taskSchemaId, tenant]);

  return {
    taskSchema,
    isLoading,
    isInitialized,
  };
};

// When receiving _ as the tenant, the backend considers that the request is for the tenant associated with the token
export const CURRENT_TENANT = '_' as TenantID;

export const useOrFetchTasks = (tenant: TenantID) => {
  const tasks = useTasks((state) => state.tasksByTenant.get(tenant) ?? []);
  const isLoading = useTasks(
    (state) => state.isLoadingTasksByTenant.get(tenant) ?? false
  );
  const isInitialized = useTasks(
    (state) => state.isInitialiazedTasksByTenant.get(tenant) === true
  );
  const fetchTasks = useTasks((state) => state.fetchTasks);

  useEffect(() => {
    fetchTasks(tenant);
  }, [fetchTasks, tenant]);

  return {
    tasks,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchTask = (
  tenant: TenantID | undefined,
  taskId: TaskID | undefined,
  forceRefetch: boolean = false
) => {
  const tasksByScope = useTasks((state) => state.tasksByScope);
  const isLoadingByScope = useTasks((state) => state.isLoadingTaskByScope);
  const isInitializedByScope = useTasks(
    (state) => state.isInitialiazedTaskByScope
  );
  const fetchTask = useTasks((state) => state.fetchTask);

  const scopeKey = buildScopeKey({ tenant, taskId: taskId ?? ('_' as TaskID) });

  const task = tasksByScope.get(scopeKey);
  const isLoading = isLoadingByScope.get(scopeKey);
  const isInitialized = isInitializedByScope.get(scopeKey) === true;

  // Use useEffect's dependency array to ensure the force fetch only happens on first mount
  useEffect(() => {
    if (taskId && (!isInitialized || forceRefetch)) {
      fetchTask(tenant, taskId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId, tenant]); // Deliberately exclude forceRefetch to ensure it only runs on mount

  return { task, isLoading, isInitialized };
};

const getTokenExpirationTime = (
  token: string | undefined
): number | undefined => {
  if (!token) return undefined;

  try {
    const [, payload] = token.split('.');
    const { exp } = JSON.parse(atob(payload));
    return exp * 1000; // Convert to milliseconds
  } catch (error) {
    console.error('Error decoding token:', error);
    return undefined;
  }
};

export const useOrFetchToken = () => {
  const { user, tenantId } = useAuth();
  const tokenScope = useMemo(
    () => tokenScopeKey({ userID: user?.id, orgID: tenantId }),
    [user?.id, tenantId]
  );

  const token = useToken((state) => state.tokenByScope.get(tokenScope));
  const isLoading = useToken((state) => state.isLoadingByScope.get(tokenScope));
  const fetchToken = useToken((state) => state.fetchToken);

  useEffect(() => {
    const refresh = () => {
      fetchToken({ userID: user?.id, orgID: tenantId });
    };

    // Initial fetch if no token
    if (!token) {
      refresh();
      return;
    }

    // Check expiration and schedule refresh
    const expirationTime = getTokenExpirationTime(token);
    if (!expirationTime) {
      refresh();
      return;
    }

    const timeUntilExpiration = expirationTime - Date.now();

    // Refresh immediately if token expires in less than 5 minutes
    if (timeUntilExpiration <= 5 * 60 * 1000) {
      refresh();
      return;
    }

    // Otherwise schedule refresh for 5 minutes before expiration
    const timeoutId = setTimeout(refresh, timeUntilExpiration - 5 * 60 * 1000);
    return () => clearTimeout(timeoutId);
  }, [token, fetchToken, user?.id, tenantId]);

  return {
    token,
    isLoading,
  };
};

export const useOrFetchTaskSnippet = (
  tenant: TenantID,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID,
  language: CodeLanguage,
  exampleTaskRunInput: Record<string, unknown> | undefined,
  iteration?: number,
  environment?: string,
  apiUrl?: string,
  secondaryInput?: Record<string, unknown>
) => {
  const scopeKey = buildSnippetScopeKey(
    taskId,
    taskSchemaId,
    language,
    iteration,
    environment,
    exampleTaskRunInput
  );
  const taskSnippet = useTaskSnippets((state) =>
    state.taskSnippetsByScope.get(scopeKey)
  );
  const isLoading = useTaskSnippets((state) =>
    state.isLoadingByScope.get(scopeKey)
  );
  const isInitialized = useTaskSnippets(
    (state) => state.isInitializedByScope.get(scopeKey) === true
  );
  const fetchSnippet = useTaskSnippets((state) => state.fetchSnippet);

  useEffect(() => {
    fetchSnippet(
      tenant,
      taskId,
      taskSchemaId,
      language,
      exampleTaskRunInput,
      iteration,
      environment,
      apiUrl,
      secondaryInput
    );
  }, [
    fetchSnippet,
    tenant,
    taskId,
    taskSchemaId,
    language,
    exampleTaskRunInput,
    iteration,
    environment,
    apiUrl,
    secondaryInput,
  ]);

  return {
    taskSnippet,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchOrganizationSettings = (pollingInterval?: number) => {
  const organizationSettings = useOrganizationSettings(
    (state) => state.settings
  );
  const isLoading = useOrganizationSettings((state) => state.isLoading);
  const isInitialized = useOrganizationSettings((state) => state.isInitialized);
  const fetchOrganizationSettings = useOrganizationSettings(
    (state) => state.fetchOrganizationSettings
  );

  useEffect(() => {
    if (organizationSettings === undefined) {
      fetchOrganizationSettings();
    }

    if (!pollingInterval) {
      return;
    }

    const intervalId = setInterval(() => {
      fetchOrganizationSettings();
    }, pollingInterval);

    return () => {
      clearInterval(intervalId);
    };
  }, [organizationSettings, fetchOrganizationSettings, pollingInterval]);

  const noCreditsLeft = useMemo(() => {
    if (!organizationSettings) {
      return false;
    }
    return (organizationSettings.current_credits_usd ?? 0) <= 0;
  }, [organizationSettings]);

  return {
    organizationSettings,
    isLoading,
    isInitialized,
    noCreditsLeft,
  };
};

export const useOrFetchProviderSchemas = () => {
  const providerSchemas = useOrganizationSettings(
    (state) => state.providerSchemas
  );
  const isLoading = useOrganizationSettings(
    (state) => state.isLoadingProviderSchemas
  );
  const fetchProviderSchemas = useOrganizationSettings(
    (state) => state.fetchProviderSchemas
  );

  useEffect(() => {
    if (providerSchemas === undefined) {
      fetchProviderSchemas();
    }
  }, [providerSchemas, fetchProviderSchemas]);

  return {
    providerSchemas,
    isLoading,
  };
};

export const useOrFetchReviewBenchmark = (
  tenant: TenantID,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID
) => {
  const scopeKey = buildScopeKey({
    tenant,
    taskId,
    taskSchemaId,
  });

  const benchmark = useReviewBenchmark((state) =>
    state.benchmarkByScope.get(scopeKey)
  );

  const isLoading = useReviewBenchmark((state) =>
    state.isLoadingByScope.get(scopeKey)
  );
  const isInitialized = useReviewBenchmark(
    (state) => state.isInitializedByScope.get(scopeKey) === true
  );

  const fetchBenchmark = useReviewBenchmark((state) => state.fetchBenchmark);

  useEffect(() => {
    fetchBenchmark(tenant, taskId, taskSchemaId);
  }, [fetchBenchmark, taskId, taskSchemaId, tenant]);

  return {
    benchmark,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchTaskStats = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  createdAfter?: Date,
  createdBefore?: Date
) => {
  const scopeKey = buildTaskStatsScopeKey({
    tenant,
    taskId,
    createdAfter,
    createdBefore,
  });

  const taskStats = useTaskStats((state) =>
    state.taskStatsByScope.get(scopeKey)
  );

  const isLoading = useTaskStats((state) =>
    state.isLoadingByScope.get(scopeKey)
  );
  const isInitialized = useTaskStats(
    (state) => state.isInitializedByScope.get(scopeKey) === true
  );

  const fetchTaskStats = useTaskStats((state) => state.fetchTaskStats);

  useEffect(() => {
    fetchTaskStats(tenant, taskId, createdAfter, createdBefore);
  }, [fetchTaskStats, taskId, createdAfter, createdBefore, tenant]);

  return {
    taskStats,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchClerkUsers = (userIds: string[]) => {
  const usersByID = useClerkUserStore((state) => state.usersByID);
  const fetchClerkUsers = useClerkUserStore((state) => state.fetchClerkUsers);
  const isInitializedById = useClerkUserStore(
    (state) => state.isInitializedById
  );

  useEffect(() => {
    const filteredUserIds = userIds.filter(
      (userId) => !isInitializedById[userId]
    );
    fetchClerkUsers(filteredUserIds);
  }, [fetchClerkUsers, userIds, isInitializedById]);

  return {
    usersByID,
  };
};

export const useOrFetchClerkOrganization = (
  organizationId: string | undefined
) => {
  const organization = useClerkOrganizationStore((state) =>
    organizationId ? state.clerkOrganizationsById[organizationId] : undefined
  );
  const isLoading = useClerkOrganizationStore((state) =>
    organizationId ? state.isLoadingById[organizationId] : false
  );
  const isInitialized = useClerkOrganizationStore((state) =>
    organizationId ? state.isInitializedById[organizationId] : false
  );
  const fetchClerkOrganization = useClerkOrganizationStore(
    (state) => state.fetchClerkOrganization
  );

  useEffect(() => {
    // Not fetching if the organizationId is the placeholder or a user slug
    if (
      !organizationId ||
      organizationId === TENANT_PLACEHOLDER ||
      organizationId.startsWith(USER_SLUG_PREFIX)
    ) {
      return;
    }
    if (!isInitialized) {
      fetchClerkOrganization(organizationId);
    }
  }, [organizationId, isInitialized, fetchClerkOrganization]);

  return {
    organization,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchApiKeys = (tenant: TenantID | undefined) => {
  const apiKeys = useApiKeys((state) => state.apiKeys);
  const isLoading = useApiKeys((state) => state.isLoading);
  const isInitialized = useApiKeys((state) => state.isInitialized);
  const fetchApiKeys = useApiKeys((state) => state.fetchApiKeys);

  useEffect(() => {
    if (!tenant) {
      return;
    }
    fetchApiKeys(tenant);
  }, [fetchApiKeys, tenant]);

  return {
    apiKeys,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchTaskPreview = (
  tenant: TenantID | undefined,
  schemaId: TaskSchemaID,
  chatMessages: ChatMessage[] | undefined,
  inputSchema: Record<string, unknown>,
  outputSchema: Record<string, unknown>,
  previouseInputPreview: Record<string, unknown> | undefined,
  previouseOutputPreview: Record<string, unknown> | undefined,
  token: string | undefined,
  isPaused: boolean
) => {
  const scopeKey = buildTaskPreviewScopeKey({
    inputSchema,
    outputSchema,
  });

  const generatedInput = useTaskPreview((state) =>
    state.generatedInputByScope.get(scopeKey)
  );

  const generatedOutput = useTaskPreview((state) =>
    state.generatedOutputByScope.get(scopeKey)
  );

  const finalGeneratedInput = useTaskPreview((state) =>
    state.finalGeneratedInputByScope.get(scopeKey)
  );

  const finalGeneratedOutput = useTaskPreview((state) =>
    state.finalGeneratedOutputByScope.get(scopeKey)
  );

  const inputBySchemaId = useTaskPreview((state) =>
    state.inputBySchemaId.get(schemaId)
  );

  const outputBySchemaId = useTaskPreview((state) =>
    state.outputBySchemaId.get(schemaId)
  );

  const generateTaskPreviewIsLoading = useTaskPreview((state) =>
    state.isLoadingByScope.get(scopeKey)
  );

  const [internalIsLoading, setInternalIsLoading] = useState(false);

  const isLoading = useMemo(() => {
    return generateTaskPreviewIsLoading || internalIsLoading;
  }, [generateTaskPreviewIsLoading, internalIsLoading]);

  const isInitialized = useTaskPreview(
    (state) => state.isInitialiazedByScope.get(scopeKey) === true
  );

  const generateTaskPreview = useTaskPreview(
    (state) => state.generateTaskPreview
  );

  const previewRef = useRef({
    input: previouseInputPreview,
    output: previouseOutputPreview,
  });

  if (!!previouseInputPreview) {
    previewRef.current.input = previouseInputPreview;
  }

  if (!!previouseOutputPreview) {
    previewRef.current.output = previouseOutputPreview;
  }

  const debouncedInputSchema = useDebounce(inputSchema, 500);
  const debouncedOutputSchema = useDebounce(outputSchema, 500);
  const debouncedChatMessages = useDebounce(chatMessages, 500);

  useEffect(() => {
    setInternalIsLoading(true);
  }, [inputSchema, outputSchema, chatMessages]);

  useEffect(() => {
    if (isPaused) {
      return;
    }

    if (!debouncedInputSchema || !debouncedOutputSchema) {
      return;
    }

    try {
      generateTaskPreview(
        tenant,
        debouncedChatMessages,
        debouncedInputSchema,
        debouncedOutputSchema,
        previewRef.current.input,
        previewRef.current.output,
        token
      );
    } catch (error) {
      console.error('Error parsing debounced schemas:', error);
    } finally {
      setInternalIsLoading(false);
    }
  }, [
    generateTaskPreview,
    tenant,
    debouncedChatMessages,
    debouncedInputSchema,
    debouncedOutputSchema,
    token,
    isPaused,
  ]);

  return {
    generatedInput,
    generatedOutput,
    finalGeneratedInput,
    finalGeneratedOutput,
    inputBySchemaId,
    outputBySchemaId,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchVersions = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID | undefined = undefined,
  enablePolling: boolean = false,
  skipFetchIfInitialized: boolean = false
) => {
  const scopeKey = buildScopeKey({
    tenant,
    taskId,
    taskSchemaId,
  });

  const majorVersions = useVersions(
    (state) => state.versionsByScope.get(scopeKey) || []
  );

  const isLoading = useVersions((state) =>
    state.isLoadingVersionsByScope.get(scopeKey)
  );

  const isInitialized = useVersions(
    (state) => state.isInitializedVersionsByScope.get(scopeKey) === true
  );

  const versions = useMemo(() => {
    const result = mapMajorVersionsToVersions(majorVersions);
    return sortVersions(result);
  }, [majorVersions]);

  const versionsPerEnvironment = useMemo(() => {
    return getVersionsPerEnvironment(versions);
  }, [versions]);

  const deployedVersions = useMemo(() => {
    const result: VersionV1[] = [];
    versions.forEach((version) => {
      if (!version.deployments || version.deployments.length === 0) {
        return;
      }
      result.push(version);
    });
    return result;
  }, [versions]);

  const fetchVersions = useVersions((state) => state.fetchVersions);

  const skipFetch = skipFetchIfInitialized && isInitialized;

  useEffect(() => {
    if (skipFetch || !taskId) {
      return;
    }

    fetchVersions(tenant, taskId, taskSchemaId);

    if (enablePolling) {
      const intervalId = setInterval(() => {
        fetchVersions(tenant, taskId, taskSchemaId);
      }, 10000);

      return () => clearInterval(intervalId);
    }
  }, [fetchVersions, taskId, tenant, enablePolling, skipFetch, taskSchemaId]);

  return {
    majorVersions,
    versions,
    versionsPerEnvironment,
    deployedVersions,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchVersion = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  versionId: string | undefined
) => {
  const scopeKey = buildVersionScopeKey({
    tenant,
    taskId,
    versionId,
  });

  const version = useVersions((state) => state.versionByScope.get(scopeKey));

  const isLoading = useVersions((state) =>
    state.isLoadingVersionByScope.get(scopeKey)
  );

  const isInitialized = useVersions(
    (state) => state.isInitializedVersionByScope.get(scopeKey) === true
  );

  const fetchVersion = useVersions((state) => state.fetchVersion);

  useEffect(() => {
    if (!versionId) {
      return;
    }
    fetchVersion(tenant, taskId, versionId);
  }, [fetchVersion, taskId, tenant, versionId]);

  return {
    version,
    isLoading,
    isInitialized,
  };
};

export const useIsSavingVersion = (versionId: string | undefined) => {
  const isSavingVersion = useVersions((state) =>
    !!versionId ? state.isSavingVersion.get(versionId) : false
  );
  return isSavingVersion;
};

export const useOrFetchEvaluationInputs = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID
) => {
  const scopeKey = buildScopeKey({
    tenant,
    taskId,
    taskSchemaId,
  });

  const evaluationInputs = useTaskEvaluation((state) =>
    state.evaluationInputsByScope.get(scopeKey)
  );

  const isLoading = useTaskEvaluation((state) =>
    state.isLoadingEvaluationInputsByScope.get(scopeKey)
  );

  const isInitialized = useTaskEvaluation(
    (state) => state.isInitializedEvaluationInputsByScope.get(scopeKey) === true
  );

  const fetchEvaluationInputs = useTaskEvaluation(
    (state) => state.fetchEvaluationInputs
  );

  useEffect(() => {
    fetchEvaluationInputs(tenant, taskId, taskSchemaId);
  }, [fetchEvaluationInputs, taskId, tenant, taskSchemaId]);

  return {
    evaluationInputs,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchEvaluation = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskSchemaId: TaskSchemaID
) => {
  const scopeKey = buildScopeKey({
    tenant,
    taskId,
    taskSchemaId,
  });

  const evaluation = useTaskEvaluation((state) =>
    state.evaluationByScope.get(scopeKey)
  );

  const isLoading = useTaskEvaluation((state) =>
    state.isLoadingEvaluationByScope.get(scopeKey)
  );

  const isInitialized = useTaskEvaluation(
    (state) => state.isInitializedEvaluationByScope.get(scopeKey) === true
  );

  const fetchEvaluation = useTaskEvaluation((state) => state.fetchEvaluation);

  useEffect(() => {
    fetchEvaluation(tenant, taskId, taskSchemaId);
  }, [fetchEvaluation, taskId, tenant, taskSchemaId]);

  return {
    evaluation,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchSuggestedAgentsIfNeeded = (companyURL?: string) => {
  const suggestedAgents = useSuggestedAgents((state) =>
    !!companyURL ? state.suggestedAgentsByURL[companyURL] : undefined
  );

  const streamedAgents = useSuggestedAgents((state) =>
    !!companyURL ? state.streamedAgentsByURL[companyURL] : undefined
  );

  const messages = useSuggestedAgents((state) =>
    !!companyURL ? state.messagesByURL[companyURL] : undefined
  );

  const isLoading = useSuggestedAgents(
    (state) => !!companyURL && state.isLoadingByURL[companyURL]
  );

  const isInitialized = useSuggestedAgents(
    (state) => !!companyURL && state.isInitializedByURL[companyURL]
  );

  const fetchSuggestedAgents = useSuggestedAgents(
    (state) => state.fetchSuggestedAgents
  );

  const reset = useSuggestedAgents((state) => state.reset);

  const resetToInitialState = useSuggestedAgents(
    (state) => state.resetToInitialState
  );

  const agentsExistRef = useRef<boolean>(false);
  agentsExistRef.current = Boolean(suggestedAgents?.length);

  useEffect(() => {
    if (!companyURL || agentsExistRef.current) {
      return;
    }
    fetchSuggestedAgents(companyURL);
  }, [fetchSuggestedAgents, companyURL]);

  return {
    suggestedAgents,
    streamedAgents:
      !!streamedAgents && streamedAgents.length > 0
        ? streamedAgents
        : undefined,
    messages,
    isLoading,
    isInitialized,
    resetToInitialState,
    reset,
  };
};

export const useOrFetchSuggestedTaskPreview = (
  agent: SuggestedAgent | undefined
) => {
  const scopeKey = buildSuggestedAgentPreviewScopeKey({ agent });

  const preview = useSuggestedAgentPreview((state) =>
    !!scopeKey ? state.previewByScope.get(scopeKey) : undefined
  );

  const isLoading = useSuggestedAgentPreview((state) =>
    !!scopeKey ? state.isLoadingByScope.get(scopeKey) ?? false : false
  );
  const isInitialized = useSuggestedAgentPreview((state) =>
    !!scopeKey ? state.isInitializedByScope.get(scopeKey) ?? false : false
  );

  const fetchSuggestedTaskPreview = useSuggestedAgentPreview(
    (state) => state.fetchSuggestedTaskPreviewIfNeeded
  );

  const previewExistRef = useRef<boolean>(false);
  previewExistRef.current = !!preview;

  useEffect(() => {
    if (!agent || previewExistRef.current) {
      return;
    }
    fetchSuggestedTaskPreview(agent);
  }, [fetchSuggestedTaskPreview, agent]);

  return {
    preview,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchPayments = (tenant: TenantID | undefined) => {
  const paymentMethod = usePayments((state) => state.paymentMethod);
  const stripeCustomerId = usePayments((state) => state.stripeCustomerId);

  const isLoading = usePayments((state) => state.isLoading);

  const isCreateCustomerInitialized = usePayments(
    (state) => state.isCreateCustomerInitialized
  );

  const isPaymentMethodInitialized = usePayments(
    (state) => state.isPaymentMethodInitialized
  );

  const isInitialized =
    isCreateCustomerInitialized && isPaymentMethodInitialized;

  const createCustomer = usePayments((state) => state.createCustomer);
  const getPaymentMethod = usePayments((state) => state.getPaymentMethod);

  useEffect(() => {
    if (isNullish(stripeCustomerId)) {
      createCustomer(tenant);
    }
  }, [tenant, stripeCustomerId, createCustomer]);

  useEffect(() => {
    if (!isNullish(stripeCustomerId)) {
      getPaymentMethod(tenant);
    }
  }, [getPaymentMethod, tenant, stripeCustomerId]);

  return {
    paymentMethod,
    stripeCustomerId,
    isLoading,
    isInitialized,
  };
};

export const useOrFetchRunCompletions = (
  tenant: TenantID | undefined,
  taskId: TaskID,
  taskRunId: string
) => {
  const completions = useRunCompletions((state) =>
    state.runCompletionsById.get(taskRunId)
  );

  const isLoading = useRunCompletions(
    (state) => state.isLoadingById.get(taskRunId) ?? false
  );

  const isInitialized = useRunCompletions(
    (state) => state.isInitializedById.get(taskRunId) ?? false
  );

  const fetchRunCompletions = useRunCompletions(
    (state) => state.fetchRunCompletion
  );

  useEffect(() => {
    fetchRunCompletions(tenant, taskId, taskRunId);
  }, [fetchRunCompletions, tenant, taskId, taskRunId]);

  return {
    completions,
    isLoading,
    isInitialized,
  };
};
