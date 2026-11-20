// The web client of the fixture product, written against the generated typed client (openapi-fetch style).
import type { Client } from "./client";

export async function createNote(client: Client, tenantId: string, text: string) {
  return client.POST("/v1/tenants/{tenant_id}/notes", { params: { path: { tenant_id: tenantId } }, body: { text } });
}

export async function readNote(client: Client, tenantId: string, noteId: string) {
  return client.GET("/v1/tenants/{tenant_id}/notes/{note_id}", { params: { path: { tenant_id: tenantId, note_id: noteId } } });
}
