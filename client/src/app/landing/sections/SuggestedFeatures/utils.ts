export function looksLikeURL(input: string): boolean {
  // Remove protocol if present for the regex test
  const withoutProtocol = input.replace(/^https?:\/\//i, '');
  return !input.includes(' ') && /^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$/.test(withoutProtocol);
}

export function cleanURL(url: string): string {
  // Remove leading/trailing whitespace
  const trimmedUrl = url.trim().toLowerCase();

  if (!looksLikeURL(trimmedUrl)) {
    return url;
  }

  try {
    // Add https:// if no protocol is present
    const urlWithProtocol = /^(https?:\/\/)/i.test(trimmedUrl) ? trimmedUrl : `https://${trimmedUrl}`;

    const parsedUrl = new URL(urlWithProtocol);
    // Remove www. prefix if present and return just the hostname
    return parsedUrl.hostname.replace(/^www\./i, '');
  } catch {
    return url;
  }
}

export function isValidURL(url: string): boolean {
  if (!looksLikeURL(url)) {
    return false;
  }

  try {
    // Try parsing with https:// if no protocol is present
    const urlToTest = /^(https?:\/\/)/i.test(url) ? url : `https://${url}`;
    new URL(urlToTest);

    const parts = url.split('.');
    return parts.length >= 2 && parts[parts.length - 1].length >= 2;
  } catch {
    return false;
  }
}
