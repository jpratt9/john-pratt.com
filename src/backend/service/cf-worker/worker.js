export default {
  async fetch(request, env) {
    const auth = request.headers.get("Authorization");
    if (!env.AUTH_TOKEN || auth !== `Bearer ${env.AUTH_TOKEN}`) {
      return new Response(JSON.stringify({ error: "unauthorized" }), { status: 401, headers: { "content-type": "application/json" } });
    }
    const url = new URL(request.url).searchParams.get("url");
    if (!url) {
      return new Response(JSON.stringify({ error: "missing ?url= parameter" }), { status: 400, headers: { "content-type": "application/json" } });
    }
    try {
      const resp = await fetch(url);
      return new Response(resp.body, {
        status: resp.status,
        headers: { "content-type": resp.headers.get("content-type") || "application/octet-stream" }
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), {
        status: 500, headers: { "content-type": "application/json" }
      });
    }
  }
};
