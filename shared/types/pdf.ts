export interface PdfExportPayload {
  file_name: string;
  download_url: string;
  storage_path: string;
  expires_at?: string | null;
}
