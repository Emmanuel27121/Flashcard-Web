export const API_BASE = "http://localhost:8000";

// your upload endpoint (from your backend)
export const UPLOAD_URL = `${API_BASE}/api/uploadfile/`;

export async function uploadPdf(file, chunkSize = 1) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${UPLOAD_URL}?chunk_size=${chunkSize}`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }

  return res.json(); // { job_id, ... }
}

export async function getStatus(jobId) {
  const res = await fetch(`${API_BASE}/api/status/${jobId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Status check failed");
  }
  return res.json(); // { job_id, status, message, ... }
}

export async function getCards(jobId) {
  const res = await fetch(`${API_BASE}/api/cards/${jobId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Fetching cards failed");
  }
  return res.json(); // array of {id, question, answer}
}

export function downloadCsvUrl(jobId) {
  return `${API_BASE}/api/download/${jobId}.csv`;
}
