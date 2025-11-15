import { NextResponse } from "next/server";
import { forwardToBackend } from "../../../lib/backend";

export async function POST(request: Request) {
  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return NextResponse.json({ message: "Invalid JSON payload" }, { status: 400 });
  }

  try {
    const { response, payload: data } = await forwardToBackend("/api/sessions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        message: "Unable to reach backend service",
        details: error instanceof Error ? error.message : "unknown error",
      },
      { status: 502 },
    );
  }
}
