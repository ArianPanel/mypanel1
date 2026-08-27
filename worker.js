export default {
  async fetch(request, env, ctx) {
    // HTTP checks (Non-WebSocket requests)
    if (request.headers.get("Upgrade") !== "websocket") {
      return new Response("Welcome to Spider Panel Worker", {
        status: 200,
        headers: { "Content-Type": "text/plain" }
      });
    }

    // WebSocket Connection
    const upgradeHeader = request.headers.get("Upgrade");
    if (upgradeHeader !== "websocket") {
      return new Response("Expected WebSocket", { status: 400 });
    }

    const url = new URL(request.url);
    const path = url.pathname;
    const providedUUID = path.split('/')[1];

    // Validate UUID against KV store
    const userKey = `user:${providedUUID}`;
    const userData = await env.KV.get(userKey, "json");

    if (!userData) {
      return new Response("Unauthorized: Invalid UUID", { status: 403 });
    }

    // Check User Quota (if exists in KV)
    if (userData.limit_bytes && userData.used_bytes >= userData.limit_bytes) {
      return new Response("403 Forbidden: Quota Exceeded", { status: 403 });
    }

    // WebSocket Pairing
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);

    server.accept();

    // Handle Messages
    server.addEventListener("message", (event) => {
      // Note: In a fully functional relay, this would parse the VLESS protocol header
      // and forward the data to the target via cloudflare:sockets.
      // This simplified version only echoes back to display it's working.
      server.send("Spider Panel Worker Active - Connection Validated");
    });

    server.addEventListener("close", (evt) => {
      // Log close or handle cleanup
    });

    return new Response(null, {
      status: 101,
      webSocket: client,
    });
  }
};
