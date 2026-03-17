{%- if cookiecutter.enable_rag and cookiecutter.use_frontend %}
"use client";

import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Button, Card, Input, Badge } from "@/components/ui";
import { Database, Search, Trash2, FileText, RefreshCw } from "lucide-react";
import {
  listCollections,
  getCollectionInfo,
  deleteCollection,
  searchDocuments,
  type RAGCollectionInfo,
  type RAGSearchResult,
} from "@/lib/rag-api";

interface CollectionWithInfo {
  name: string;
  info: RAGCollectionInfo | null;
}

export default function RAGPage() {
  const [collections, setCollections] = useState<CollectionWithInfo[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<RAGSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [filterType, setFilterType] = useState<string>("");
  const [filterMinScore, setFilterMinScore] = useState<string>("");

  const fetchCollections = async () => {
    setIsLoading(true);
    try {
      const data = await listCollections();
      const withInfo: CollectionWithInfo[] = [];
      for (const name of data.items) {
        try {
          const info = await getCollectionInfo(name);
          withInfo.push({ name, info });
        } catch {
          withInfo.push({ name, info: null });
        }
      }
      setCollections(withInfo);
      if (withInfo.length > 0 && !selectedCollection) {
        setSelectedCollection(withInfo[0].name);
      }
    } catch {
      toast.error("Failed to load collections");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchCollections(); }, []);

  const handleDeleteCollection = async (name: string) => {
    if (!confirm(`Delete collection "${name}" and all its documents?`)) return;
    try {
      await deleteCollection(name);
      toast.success(`Collection "${name}" deleted`);
      setCollections((prev) => prev.filter((c) => c.name !== name));
      if (selectedCollection === name) {
        setSelectedCollection("");
        setSearchResults([]);
      }
    } catch {
      toast.error("Failed to delete collection");
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || (!selectedCollection && collections.length === 0)) return;
    setIsSearching(true);
    try {
      let filter = "";
      if (filterType) { filter = `filetype == "${filterType}"`; }

      const isAllCollections = selectedCollection === "__all__";
      const data = await searchDocuments({
        query: searchQuery,
        ...(isAllCollections
          ? { collection_names: collections.map((c) => c.name) }
          : { collection_name: selectedCollection }),
        limit: 10,
        min_score: filterMinScore ? parseFloat(filterMinScore) : undefined,
        filter: filter || undefined,
      });
      setSearchResults(data.results);
      if (data.results.length === 0) { toast.info("No results found"); }
    } catch {
      toast.error("Search failed");
    } finally {
      setIsSearching(false);
    }
  };

  const availableTypes = [...new Set(
    searchResults.map((r) => r.metadata?.filetype).filter(Boolean)
  )];

  return (
    <div className="container mx-auto max-w-6xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Knowledge Base</h1>
          <p className="text-sm text-muted-foreground">Manage RAG collections and search documents</p>
        </div>
        <Button variant="outline" size="sm" onClick={fetchCollections} disabled={isLoading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Collections */}
        <div className="lg:col-span-1">
          <h2 className="mb-3 text-sm font-semibold text-muted-foreground uppercase tracking-wide">Collections</h2>
          {isLoading ? (
            <Card className="p-6 text-center text-sm text-muted-foreground">Loading...</Card>
          ) : collections.length === 0 ? (
            <Card className="p-6 text-center">
              <Database className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">No collections yet</p>
              <p className="mt-1 text-xs text-muted-foreground">Use CLI to ingest documents</p>
            </Card>
          ) : (
            <div className="space-y-2">
              {collections.length > 1 && (
                <Card
                  className={`cursor-pointer p-3 transition-colors hover:bg-accent ${selectedCollection === "__all__" ? "border-primary bg-accent" : ""}`}
                  onClick={() => { setSelectedCollection("__all__"); setSearchResults([]); }}
                >
                  <p className="text-sm font-medium">All collections</p>
                  <p className="text-xs text-muted-foreground">Search across {collections.length} collections</p>
                </Card>
              )}
              {collections.map((col) => (
                <Card
                  key={col.name}
                  className={`cursor-pointer p-3 transition-colors hover:bg-accent ${selectedCollection === col.name ? "border-primary bg-accent" : ""}`}
                  onClick={() => { setSelectedCollection(col.name); setSearchResults([]); }}
                >
                  <div className="flex items-center justify-between">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{col.name}</p>
                      {col.info && <p className="text-xs text-muted-foreground">{col.info.total_vectors.toLocaleString()} vectors</p>}
                    </div>
                    <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0 text-destructive hover:text-destructive"
                      onClick={(e) => { e.stopPropagation(); handleDeleteCollection(col.name); }}>
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Search */}
        <div className="lg:col-span-2">
          <h2 className="mb-3 text-sm font-semibold text-muted-foreground uppercase tracking-wide">Search</h2>
          <Card className="p-4">
            <div className="flex gap-2">
              <Input
                placeholder={
                  selectedCollection === "__all__" ? "Search across all collections..."
                  : selectedCollection ? `Search in "${selectedCollection}"...`
                  : "Select a collection first"
                }
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                disabled={!selectedCollection}
              />
              <Button onClick={handleSearch} disabled={!selectedCollection || isSearching || !searchQuery.trim()}>
                <Search className="mr-2 h-4 w-4" />
                {isSearching ? "..." : "Search"}
              </Button>
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <span className="text-xs text-muted-foreground">Filters:</span>
              <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="rounded-md border bg-background px-2 py-1 text-xs">
                <option value="">All types</option>
                <option value="pdf">PDF</option>
                <option value="docx">DOCX</option>
                <option value="md">Markdown</option>
                <option value="txt">Text</option>
                {availableTypes.filter((t) => !["pdf", "docx", "md", "txt"].includes(t as string)).map((t) => (
                  <option key={t} value={t}>{String(t).toUpperCase()}</option>
                ))}
              </select>
              <select value={filterMinScore} onChange={(e) => setFilterMinScore(e.target.value)} className="rounded-md border bg-background px-2 py-1 text-xs">
                <option value="">Min score: any</option>
                <option value="0.3">Score &ge; 0.3</option>
                <option value="0.5">Score &ge; 0.5</option>
                <option value="0.7">Score &ge; 0.7</option>
                <option value="0.9">Score &ge; 0.9</option>
              </select>
              {(filterType || filterMinScore) && (
                <button onClick={() => { setFilterType(""); setFilterMinScore(""); }} className="text-xs text-primary hover:underline">Clear filters</button>
              )}
            </div>
          </Card>

          {searchResults.length > 0 && (
            <div className="mt-4 space-y-3">
              {searchResults.map((result, i) => (
                <Card key={i} className="p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs font-medium text-muted-foreground">{result.metadata?.filename || "Unknown"}</span>
                    {result.metadata?.page_num && <Badge variant="outline" className="text-xs">Page {result.metadata.page_num}</Badge>}
                    {result.metadata?.collection && <Badge variant="outline" className="text-xs">{result.metadata.collection}</Badge>}
                    <Badge variant="secondary" className="ml-auto text-xs">Score: {result.score.toFixed(3)}</Badge>
                  </div>
                  <p className="text-sm leading-relaxed">{result.content}</p>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
{%- else %}
export default function RAGPage() {
  return null;
}
{%- endif %}
