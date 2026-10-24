// Serves kolasaar.com/para/sa/* from the Pages project kolasaar-para-sa (Saudi beauty comparison).
// Only this path is routed here; every other kolasaar.com path (including /para/tn/*) is untouched.
export default {
  async fetch(request) {
    const url = new URL(request.url);
    url.hostname = "kolasaar-para-sa.pages.dev";
    url.protocol = "https:";
    url.port = "";
    return fetch(new Request(url.toString(), request), { redirect: "manual" });
  },
};
