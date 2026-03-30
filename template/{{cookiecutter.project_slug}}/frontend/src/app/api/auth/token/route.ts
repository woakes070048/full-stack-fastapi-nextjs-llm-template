{% raw %}import { NextRequest, NextResponse } from "next/server";
import { backendFetch } from "@/lib/server-api";

/**
 * Token proxy endpoint for WebSocket authentication.
 *
 * This endpoint reads the httpOnly access_token cookie and returns it
 * as JSON so that client-side code can use it for WebSocket connections.
 *
 * The token is validated with the backend before being returned.
 */
export async function GET(request: NextRequest) {
  const accessToken = request.cookies.get("access_token")?.value;

  if (!accessToken) {
    return NextResponse.json(
      { error: "No access token found" },
      { status: 401 }
    );
  }

  // Validate token with backend
  try {
    await backendFetch("/api/v1/auth/me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
  } catch {
    return NextResponse.json(
      { error: "Invalid or expired token" },
      { status: 401 }
    );
  }

  return NextResponse.json({ access_token: accessToken });
}{% endraw %}
