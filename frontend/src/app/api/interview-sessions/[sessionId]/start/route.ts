import { NextResponse } from "next/server";
import { forwardToBackend } from "../../../../../lib/backend";

type Params = {
  params: {
    sessionId: string;
  };
};

export async function POST(_: Request, { params }: Params) {
  const { sessionId } = params;
  if (!sessionId) {
    return NextResponse.json({ message: "Session ID is required" }, { status: 400 });
  }

  try {
    const { response, payload } = await forwardToBackend(`/api/sessions/${sessionId}/start`, {
      method: "POST",
    });
    return NextResponse.json(payload, { status: response.status });
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
