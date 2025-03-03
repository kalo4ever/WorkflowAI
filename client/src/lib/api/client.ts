import {
  EventSourceMessage,
  fetchEventSource,
} from '@microsoft/fetch-event-source';
import { captureException } from '@sentry/nextjs';
import { StreamError } from '@/types/errors';

function extractErrorMessage(parsed: unknown) {
  if (typeof parsed !== 'object' || !parsed) {
    return undefined;
  }

  if ('error' in parsed) {
    if (typeof parsed.error === 'string') {
      return parsed.error;
    }
    if (
      typeof parsed.error === 'object' &&
      !!parsed.error &&
      'message' in parsed.error &&
      typeof parsed.error?.message === 'string'
    ) {
      return parsed.error.message;
    }
    return undefined;
  }
}

export class RequestError extends Error {
  status: number;
  path: string;
  response: Response;

  constructor(status: number, path: string, response: Response) {
    super(`Failed to request ${path}`);

    this.path = path;
    this.status = status;
    this.response = response;
  }

  async humanReadableMessage() {
    try {
      const parsed = await this.response.json();
      return extractErrorMessage(parsed);
    } catch (e) {
      return this.message;
    }
  }
}

export enum Method {
  GET = 'GET',
  POST = 'POST',
  DELETE = 'DELETE',
  PUT = 'PUT',
  PATCH = 'PATCH',
}

async function fetchWrapper<T, R = unknown>(
  path: string,
  {
    method,
    body,
  }: {
    method: Method;
    body?: T;
  }
): Promise<R> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'x-workflowai-source': 'web',
  };
  if (process.env.NEXT_PUBLIC_RELEASE_NAME) {
    headers['x-workflowai-version'] = process.env.NEXT_PUBLIC_RELEASE_NAME;
  }
  const res = await fetch(path, {
    method,
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const error = new RequestError(res.status, path, res);
    captureException(error, {
      tags: { path },
      extra: { path, status: res.status, raw: await res.text() },
    });
    throw error;
  }
  if (res.status === 204) {
    return undefined as R;
  }
  const toJSON = await res.json();
  return toJSON;
}

export async function get<T>(
  path: string,
  query?: URLSearchParams
): Promise<T> {
  const url = query ? `${path}?${query.toString()}` : path;

  return fetchWrapper(url, { method: Method.GET });
}

export async function post<T, R = unknown>(path: string, body: T): Promise<R> {
  return fetchWrapper(path, { method: Method.POST, body });
}

export async function put<T, R = unknown>(path: string, body: T): Promise<R> {
  return fetchWrapper(path, { method: Method.PUT, body });
}

export async function patch<T, R = unknown>(path: string, body: T): Promise<R> {
  return fetchWrapper(path, { method: Method.PATCH, body });
}

export async function del<T = undefined, R = unknown>(
  path: string,
  body?: T
): Promise<R> {
  return fetchWrapper(path, { method: Method.DELETE, body });
}

export async function uploadFile<R = unknown>(
  path: string,
  body: FormData,
  token: string,
  onProgress?: (progress: number) => void
): Promise<R> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable && !!onProgress) {
        const percentComplete = event.loaded / event.total;
        onProgress(percentComplete);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } catch (e) {
          reject(new Error('Invalid response format'));
        }
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`));
      }
    });

    xhr.addEventListener('error', () => reject(new Error('Upload failed')));
    xhr.addEventListener('abort', () => reject(new Error('Upload aborted')));

    xhr.open('POST', path);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.send(body);
  });
}

function parseSSEEvent(eventData: string) {
  let parsed: unknown;
  try {
    parsed = JSON.parse(eventData);
  } catch (e) {
    throw new StreamError('Failed to parse event source message', true, {
      eventData,
    });
  }

  if (typeof parsed !== 'object' || !parsed) {
    throw new StreamError('Invalid event source message', true, { eventData });
  }

  if ('error' in parsed) {
    const msg = extractErrorMessage(parsed);
    throw new StreamError(
      msg ?? 'An unknown error occurred',
      msg === undefined,
      { eventData }
    );
  }

  return parsed;
}

export async function SSEClient<R, T>(
  path: string,
  method: Method,
  token: string | null | undefined,
  body: R,
  onMessage?: (ev: T) => void,
  signal?: AbortSignal
): Promise<T> {
  let lastMessage: T | undefined;

  await fetchEventSource(path, {
    onmessage: (event: EventSourceMessage) => {
      lastMessage = parseSSEEvent(event.data) as T;
      onMessage?.(lastMessage);
    },
    onerror: (e: unknown) => {
      if (e instanceof StreamError) {
        if (e.capture) {
          captureException(e, { extra: { ...e.extra, path } });
        }
      } else {
        captureException(e);
      }
      throw e;
    },
    method,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      'x-workflowai-source': 'web',
      'x-workflowai-version': process.env.NEXT_PUBLIC_RELEASE_NAME ?? 'unknown',
    },
    body:
      method !== Method.GET
        ? JSON.stringify({ ...body, stream: true })
        : undefined,
    openWhenHidden: true,
    // We should not keepalive because we noticed that running audio tasks
    // with keepalive enabled causes unexpected "Failed to fetch" errors.
    keepalive: false,
    signal,
  });

  if (!lastMessage) {
    const err = new Error('No message received');
    captureException(err, { extra: { path } });
    throw err;
  }
  return lastMessage!;
}
