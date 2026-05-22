export interface Source {
  name: string;
  label: string;
  description: string;
  query: string;
  total_records: number;
  last_sync: string | null;
  status: 'idle' | 'syncing' | 'error';
  progress?: number;
}
