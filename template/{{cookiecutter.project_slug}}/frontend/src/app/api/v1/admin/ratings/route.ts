{%- if cookiecutter.use_jwt %}
import { NextRequest, NextResponse } from "next/server";
import { backendFetch, BackendApiError } from "@/lib/server-api";

export async function GET(request: NextRequest) {
  try {
    const accessToken = request.cookies.get("access_token")?.value;

    if (!accessToken) {
      return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }

    const searchParams = request.nextUrl.searchParams;
    const skip = searchParams.get("skip") || "0";
    const limit = searchParams.get("limit") || "50";
    const ratingFilter = searchParams.get("rating_filter");
    const withCommentsOnly = searchParams.get("with_comments_only") === "true";

    let url = `/api/v1/admin/ratings?skip=${skip}&limit=${limit}`;
    if (ratingFilter) url += `&rating_filter=${ratingFilter}`;
    if (withCommentsOnly) url += `&with_comments_only=true`;

    const data = await backendFetch(url, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    return NextResponse.json(data);
  } catch (error) {
    if (error instanceof BackendApiError) {
      return NextResponse.json(
        { detail: error.message || "Failed to fetch ratings" },
        { status: error.status }
      );
    }
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    );
  }
}
{%- endif %}
