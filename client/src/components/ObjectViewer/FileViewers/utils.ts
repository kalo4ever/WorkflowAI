export type FileValueType = {
  content_type?: string;
  data?: string;
  storage_url?: string;
  url?: string;
  name?: string;
};

export function extractFileSrc(file: FileValueType | undefined) {
  if (!file) {
    return undefined;
  }
  if (file.storage_url) {
    return file.storage_url;
  }
  if (file.url) {
    return file.url;
  }
  if (file.data) {
    return `data:${file.content_type};base64,${file.data}`;
  }
  return undefined;
}
