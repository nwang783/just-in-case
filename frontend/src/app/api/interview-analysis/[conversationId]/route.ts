import { NextResponse } from "next/server";
import { forwardToBackend } from "../../../../lib/backend";

type RouteParams = {
  params: {
    conversationId?: string;
  };
};

export async function GET(_request: Request, { params }: RouteParams) {
  const conversationId = params.conversationId;
  if (!conversationId) {
    return NextResponse.json({ message: "conversationId is required" }, { status: 400 });
  }

  try {
    const { response, payload } = await forwardToBackend(
      `/api/interviews/${encodeURIComponent(conversationId)}/analysis`,
    );
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
