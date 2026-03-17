{%- if cookiecutter.enable_rag and cookiecutter.use_frontend %}
{% raw %}import { NextRequest, NextResponse } from "next/server";
import { backendFetch, BackendApiError } from "@/lib/server-api";

// POST /api/v1/rag/search - Search documents
export async function POST(request: NextRequest) {
  const authEnabled = process.env.NEXT_PUBLIC_AUTH_ENABLED === "true";
  let accessToken: string | undefined;

  if (authEnabled) {
    accessToken = request.cookies.get("access_token")?.value;
    if (!accessToken) {
      return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }
  }

  try {
    const body = await request.json();
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (accessToken) {
      headers["Authorization"] = `Bearer ${accessToken}`;
    }

    const data = await backendFetch("/api/v1/rag/search", {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    return NextResponse.json(data);
  } catch (error) {
    if (error instanceof BackendApiError) {
      return NextResponse.json(
        { detail: error.message || "Failed to search documents" },
        { status: error.status }
      );
    }
    return NextResponse.json({ detail: "Internal server error" }, { status: 500 });
  }
}
{% endraw %}
{%- else %}
// RAG search route - not configured (enable_rag is false or frontend is disabled)
{%- endif %}
