/**
 * RAG (Retrieval Augmented Generation) API client.
 * Provides methods for collection management and search.
 * Document ingestion is handled via CLI commands.
 */

import { apiClient } from "./api-client";

export const RAG_API_ROUTES = {
  COLLECTIONS: "/v1/rag/collections",
  COLLECTIONS_INFO: (name: string) => `/v1/rag/collections/${name}/info`,
  COLLECTIONS_CREATE: (name: string) => `/v1/rag/collections/${name}`,
  COLLECTIONS_DELETE: (name: string) => `/v1/rag/collections/${name}`,
  COLLECTIONS_DOCUMENT_DELETE: (name: string, documentId: string) =>
    `/v1/rag/collections/${name}/documents/${documentId}`,
  SEARCH: "/v1/rag/search",
} as const;

export interface RAGCollectionList {
  items: string[];
}

export interface RAGCollectionInfo {
  name: string;
  total_vectors: number;
  dim: number;
  indexing_status: string;
}

export interface RAGSearchRequest {
  query: string;
  collection_name?: string;
  collection_names?: string[];
  limit?: number;
  min_score?: number;
  filter?: string;
}

export interface RAGSearchResult {
  content: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  metadata: Record<string, any>;
  score: number;
  parent_doc_id: string;
}

export interface RAGSearchResponse {
  results: RAGSearchResult[];
}

export const isRagEnabled = (): boolean => {
  return process.env.NEXT_PUBLIC_RAG_ENABLED === "true";
};

export async function listCollections(): Promise<RAGCollectionList> {
  return apiClient.get<RAGCollectionList>(RAG_API_ROUTES.COLLECTIONS);
}

export async function getCollectionInfo(
  collectionName: string
): Promise<RAGCollectionInfo> {
  return apiClient.get<RAGCollectionInfo>(
    RAG_API_ROUTES.COLLECTIONS_INFO(collectionName)
  );
}

export async function createCollection(
  collectionName: string
): Promise<{ message: string }> {
  return apiClient.post<{ message: string }>(
    RAG_API_ROUTES.COLLECTIONS_CREATE(collectionName)
  );
}

export async function deleteCollection(collectionName: string): Promise<void> {
  return apiClient.delete(RAG_API_ROUTES.COLLECTIONS_DELETE(collectionName));
}

export async function deleteDocument(
  collectionName: string,
  documentId: string
): Promise<void> {
  return apiClient.delete(
    RAG_API_ROUTES.COLLECTIONS_DOCUMENT_DELETE(collectionName, documentId)
  );
}

export async function searchDocuments(
  request: RAGSearchRequest
): Promise<RAGSearchResponse> {
  return apiClient.post<RAGSearchResponse>(RAG_API_ROUTES.SEARCH, request);
}
