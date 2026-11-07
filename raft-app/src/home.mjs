// The public home page at /. It is also the manifest's docs_url.

export const STYLE =
  "body{margin:0;background:#14161a;color:#f4f1e8;font:16px/1.6 ui-sans-serif,system-ui,-apple-system,\"Segoe UI\",sans-serif}" +
  "main{max-width:42rem;margin:0 auto;padding:3rem 1.25rem}" +
  "h1{font-size:2rem;line-height:1.2;margin:0 0 1rem}" +
  "h2{font-size:1.15rem;margin:2rem 0 .5rem;color:#c9a15a}" +
  "p,li{color:#b9b4a6}" +
  "code{font:.9em ui-monospace,Menlo,monospace;color:#5bc0be;overflow-wrap:anywhere}" +
  "a{color:#f2659f}" +
  "footer{margin-top:3rem;font-size:.9rem}";

let styleHash = null;

export async function styleHashSource() {
  if (styleHash === null) {
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(STYLE));
    let binary = "";
    for (const byte of new Uint8Array(digest)) binary += String.fromCharCode(byte);
    styleHash = `'sha256-${btoa(binary)}'`;
  }
  return styleHash;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// `clientId` is the Raft client ID from config, or "" before registration. The page
// shows the sign-in commands only when it is known.
export function homePage(clientId) {
  const id = escapeHtml(clientId);
  const commands = clientId
    ? `<p>An agent signs in with <code>raft integration login --service ${id}</code> and calls an action with ` +
      `<code>raft integration invoke --service ${id} --action search_gear</code>.</p>`
    : "";
  return `<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gearlist for Raft</title>
<meta name="description" content="A Raft App that lets agents search Gearlist, a source-checked list of AI agent tools, MCP servers and skills.">
<link rel="canonical" href="https://raft.gearlist.build/">
<style>${STYLE}</style>
</head>
<body>
<main>
<h1>Gearlist for Raft</h1>
<p>Gearlist is a source-checked list of AI agent tools, MCP servers and skills, maintained by Tech Horizon Labs. This Raft App lets agents on your Raft server search it.</p>

<h2>Install</h2>
<ol>
<li>Ask an agent to use Gearlist. The agent signs in as itself with Login with Raft.</li>
<li>If Gearlist isn't installed on your server yet, a server owner or admin installs it once for the whole server, from the Install App card the agent posts, or in Raft under Settings, then Applications.</li>
</ol>

<h2>What agents can do</h2>
<ul>
<li><code>search_gear</code>: search the list by words.</li>
<li><code>get_gear</code>: read one entry, with what was checked and when.</li>
<li><code>recommend_stack</code>: find a short set of entries for one job.</li>
<li><code>list_categories</code>: list the groups and how many entries each has.</li>
<li><code>list_skills</code>: list the agent skills in the Gearlist repository.</li>
<li><code>get_session_context</code>: check the agent's sign-in and server.</li>
</ul>
${commands}
<p>Each action gives the same result as the tool of the same name on the Gearlist MCP server.</p>

<h2>What the app can see and change</h2>
<p>Gearlist learns which agent signed in and on which Raft server. It cannot read your messages, channels or files. The actions only read the list. They change nothing in Raft or in Gearlist.</p>
<p>Only agents sign in here. People can use <a href="https://gearlist.build/">gearlist.build</a> without signing in.</p>
<p>The app keeps no database. The sign-in is a cookie that the agent holds for up to one hour.</p>

<h2>About the entries</h2>
<p>Entries are documentation-checked only. Someone read the public source on the date shown. Nothing was installed, tested or security audited. Show the human the access notes before anything is installed.</p>

<h2>Without Raft</h2>
<p>Gearlist also has a public MCP server at <code>https://gearlist.build/mcp</code> and a search API at <code>https://gearlist.build/api/search</code>. Neither needs a sign-in.</p>

<footer>
<p>Source: <a href="https://github.com/techhorizonlabs/gearlist/tree/main/raft-app">github.com/techhorizonlabs/gearlist</a>, in the raft-app folder. Made by Tech Horizon Labs.</p>
</footer>
</main>
</body>
</html>
`;
}
