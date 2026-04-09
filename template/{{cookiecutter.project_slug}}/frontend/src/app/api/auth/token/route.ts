{% raw %}import { NextRequest, NextResponse } from "next/server";
import { backendFetch } from "@/lib/server-api";

/**
 * Token proxy endpoint for WebSocket authentication.
 *
 * This endpoint reads the httpOnly access_token cookie and returns it
 * as JSON so that client-side code can use it for WebSocket connections.
 *
 * The token is validated with the backend before being returned.
 *
 * SECURITY NOTE: This endpoint converts an httpOnly cookie into a JSON
 * response readable by JavaScript. This is a deliberate tradeoff: WebSocket
 * connections require the token in a URL parameter or header, but httpOnly
 * cookies are not accessible from JS. The Origin header check below restricts
 * access to same-origin requests, limiting exposure to XSS attacks.
 */
export async function GET(request: NextRequest) {
  // Restrict to same-origin requests to limit XSS exposure
  const origin = request.headers.get("origin");
  const host = request.headers.get("host");
  if (origin && host) {
    try {
      const originUrl = new URL(origin);
      if (originUrl.host !== host) {
        return NextResponse.json({ error: "Forbidden" }, { status: 403 });
      }
    } catch {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }
  }

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
