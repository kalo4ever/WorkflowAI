export interface Page<T> {
  items: T[];
  page_token?: string;
  count?: number;
}
