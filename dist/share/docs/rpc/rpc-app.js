/* Cellframe Node RPC interactive docs */
(function () {
  "use strict";

  const STORAGE_KEY = "cf-rpc-docs-server";

  /** @type {Array<{tag:string,method:string,id:string,summary:string,docs:string,subcommand:string,warn?:string,params:Array<{name:string,required?:boolean,flag?:boolean,type?:string,default?:string,description?:string,enum?:string[]}>}>} */
  const RPC_CATALOG = [
    /* version */
    { tag: "version", method: "version", id: "version", summary: "Return node software version", docs: "/version.html", subcommand: "", params: [] },

    /* help */
    { tag: "help", method: "help", id: "help-list", summary: "List available commands", docs: "/help.html", subcommand: "", params: [] },
    { tag: "help", method: "help", id: "help-cmd", summary: "Help for a specific command", docs: "/help.html", subcommand: "", params: [
      { name: "command", required: true, default: "wallet", description: "Put into subcommand (v2) / help;<cmd> (v1)" }
    ] },

    /* wallet */
    { tag: "wallet", method: "wallet", id: "wallet-list", summary: "List wallets on the node", docs: "/wallet.html", subcommand: "list", params: [] },
    { tag: "wallet", method: "wallet", id: "wallet-info", summary: "Wallet / address info", docs: "/wallet.html", subcommand: "info", params: [
      { name: "addr", required: true, default: "", description: "Wallet address" },
      { name: "net", required: false, default: "Backbone", description: "Required with -w, optional with -addr" }
    ] },
    { tag: "wallet", method: "wallet", id: "wallet-outputs", summary: "List UTXO outputs", docs: "/wallet.html", subcommand: "outputs", params: [
      { name: "addr", required: true, default: "" },
      { name: "token", required: true, default: "CELL" },
      { name: "net", required: false, default: "Backbone" }
    ] },
    { tag: "wallet", method: "wallet", id: "wallet-find", summary: "Find local wallet by address", docs: "/wallet.html", subcommand: "find", params: [
      { name: "addr", required: true, default: "" }
    ] },
    { tag: "wallet", method: "wallet", id: "wallet-shared-list", summary: "List shared-funds addresses", docs: "/wallet.html", subcommand: "shared;list", params: [
      { name: "net", required: false, default: "Backbone" }
    ] },

    /* net */
    { tag: "net", method: "net", id: "net-list", summary: "List networks", docs: "/net.html", subcommand: "list", params: [] },
    { tag: "net", method: "net", id: "net-get-status", summary: "Network status", docs: "/net.html", subcommand: "get;status", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] }
    ] },
    { tag: "net", method: "net", id: "net-get-fee", summary: "Network fee info", docs: "/net.html", subcommand: "get;fee", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] }
    ] },
    { tag: "net", method: "net", id: "net-stats-tx", summary: "Transaction stats", docs: "/net.html", subcommand: "stats;tx", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] },
      { name: "prev_day", required: false, default: "1" }
    ] },
    { tag: "net", method: "net", id: "net-link-list", summary: "List network links", docs: "/net.html", subcommand: "link;list", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] }
    ] },
    { tag: "net", method: "net", id: "net-go-online", summary: "Request NET_STATE_ONLINE", docs: "/net.html", subcommand: "go;online", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] }
    ] },
    { tag: "net", method: "net", id: "net-sync", summary: "Request full sync", docs: "/net.html", subcommand: "sync", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] }
    ] },

    /* net_srv */
    { tag: "net_srv", method: "net_srv", id: "net-srv-report", summary: "Service report", docs: "/net_srv.html", subcommand: "report", params: [] },
    { tag: "net_srv", method: "net_srv", id: "net-srv-order-find", summary: "Find service orders", docs: "/net_srv.html", subcommand: "order;find", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] },
      { name: "direction", required: false, default: "", enum: ["", "sell", "buy"] },
      { name: "srv_uid", required: false, default: "" }
    ] },
    { tag: "net_srv", method: "net_srv", id: "net-srv-order-dump", summary: "Dump order by hash", docs: "/net_srv.html", subcommand: "order;dump", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "hash", required: true, default: "" }
    ] },

    /* mempool */
    { tag: "mempool", method: "mempool", id: "mempool-count", summary: "Count mempool datums", docs: "/mempool.html", subcommand: "count", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] }
    ] },
    { tag: "mempool", method: "mempool", id: "mempool-list", summary: "List mempool entries", docs: "/mempool.html", subcommand: "list", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "chain", required: false, default: "main" },
      { name: "limit", required: false, default: "3" },
      { name: "brief", required: false, flag: true, default: "" }
    ] },
    { tag: "mempool", method: "mempool", id: "mempool-check", summary: "Check datum in mempool/chain", docs: "/mempool.html", subcommand: "check", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "datum", required: true, default: "" }
    ] },

    /* tx_history */
    { tag: "tx_history", method: "tx_history", id: "tx-history-count", summary: "Total transaction count", docs: "/tx_history.html", subcommand: "-count", params: [
      { name: "net", required: true, default: "Backbone", enum: ["Backbone", "KelVPN"] }
    ] },
    { tag: "tx_history", method: "tx_history", id: "tx-history-addr", summary: "History for address", docs: "/tx_history.html", subcommand: "", params: [
      { name: "addr", required: true, default: "" },
      { name: "net", required: true, default: "Backbone" },
      { name: "chain", required: false, default: "main" },
      { name: "limit", required: false, default: "5" },
      { name: "head", required: false, flag: true, default: "" }
    ] },
    { tag: "tx_history", method: "tx_history", id: "tx-history-tx", summary: "History for tx hash", docs: "/tx_history.html", subcommand: "", params: [
      { name: "tx", required: true, default: "" },
      { name: "net", required: true, default: "Backbone" },
      { name: "chain", required: false, default: "main" }
    ] },

    /* tx_create_json */
    { tag: "tx_create_json", method: "tx_create_json", id: "tx-create-json", summary: "Create tx from JSON (needs wallet on node)", docs: "/tx_create_json.html", warn: "Write op — public nodes usually reject", subcommand: "", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "tx_obj", required: false, default: "{\"items\":[]}", description: "Inline JSON body" }
    ] },

    /* block */
    { tag: "block", method: "block", id: "block-count", summary: "Block count", docs: "/block.html", subcommand: "count", params: [
      { name: "net", required: true, default: "Backbone" }
    ] },
    { tag: "block", method: "block", id: "block-list", summary: "List recent blocks", docs: "/block.html", subcommand: "list", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "limit", required: false, default: "3" }
    ] },
    { tag: "block", method: "block", id: "block-last", summary: "Last block", docs: "/block.html", subcommand: "last", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "chain", required: true, default: "main" }
    ] },

    /* ledger */
    { tag: "ledger", method: "ledger", id: "ledger-coins", summary: "List token coins", docs: "/ledger.html", subcommand: "list;coins", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "limit", required: false, default: "3" }
    ] },
    { tag: "ledger", method: "ledger", id: "ledger-balance", summary: "List balances", docs: "/ledger.html", subcommand: "list;balance", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "limit", required: false, default: "3" }
    ] },
    { tag: "ledger", method: "ledger", id: "ledger-info", summary: "Ledger tx info by hash", docs: "/ledger.html", subcommand: "info", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "hash", required: true, default: "" }
    ] },

    /* token */
    { tag: "token", method: "token", id: "token-list", summary: "List tokens (may timeout on public RPC)", docs: "/token.html", warn: "Prefer ledger list coins on public nodes", subcommand: "list", params: [
      { name: "net", required: true, default: "Backbone" }
    ] },
    { tag: "token", method: "token", id: "token-info", summary: "Token info by ticker", docs: "/token.html", warn: "May drop connection on public nodes", subcommand: "info", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "name", required: true, default: "CELL" }
    ] },

    /* srv_xchange */
    { tag: "srv_xchange", method: "srv_xchange", id: "xchange-orders", summary: "Legacy open orders", docs: "/srv_xchange.html", subcommand: "orders", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "seller", required: false, default: "" }
    ] },
    { tag: "srv_xchange", method: "srv_xchange", id: "xchange-order-remove", summary: "Remove order (needs wallet)", docs: "/srv_xchange.html", warn: "Write op", subcommand: "order;remove", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "order", required: true, default: "" },
      { name: "w", required: true, default: "" },
      { name: "fee", required: true, default: "0.05" }
    ] },

    /* srv_dex */
    { tag: "srv_dex", method: "srv_dex", id: "dex-pairs", summary: "List DEX pairs", docs: "/srv_xchange.html", subcommand: "pairs", params: [
      { name: "net", required: true, default: "Backbone" }
    ] },
    { tag: "srv_dex", method: "srv_dex", id: "dex-orderbook", summary: "Order book for pair", docs: "/srv_xchange.html", subcommand: "orderbook", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "pair", required: true, default: "CELL/KEL" },
      { name: "depth", required: false, default: "10" }
    ] },
    { tag: "srv_dex", method: "srv_dex", id: "dex-orders", summary: "DEX orders list", docs: "/srv_xchange.html", subcommand: "orders", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "pair", required: false, default: "" },
      { name: "limit", required: false, default: "10" }
    ] },
    { tag: "srv_dex", method: "srv_dex", id: "dex-history", summary: "Trade history", docs: "/srv_xchange.html", subcommand: "history", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "pair", required: false, default: "CELL/KEL" }
    ] },

    /* stake_lock */
    { tag: "stake_lock", method: "stake_lock", id: "stake-hold", summary: "Lock tokens until date (needs wallet)", docs: "/stake_lock.html", warn: "Write op", subcommand: "hold", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "w", required: true, default: "" },
      { name: "token", required: true, default: "CELL" },
      { name: "value", required: true, default: "1.0" },
      { name: "time_staking", required: true, default: "270101", description: "YYMMDD future date" },
      { name: "fee", required: true, default: "0.05" }
    ] },
    { tag: "stake_lock", method: "stake_lock", id: "stake-take", summary: "Unlock stake (needs wallet)", docs: "/stake_lock.html", warn: "Write op", subcommand: "take", params: [
      { name: "net", required: true, default: "Backbone" },
      { name: "w", required: true, default: "" },
      { name: "tx", required: true, default: "" },
      { name: "fee", required: true, default: "0.05" }
    ] }
  ];

  const state = {
    server: "",
    version: 2,
    filter: "",
    expanded: {},
    values: {},
    results: {},
    loading: {},
    errors: {},
    idCounter: 1
  };

  function defaultServer() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) return saved;
    } catch (_) {}
    if (typeof location !== "undefined" && /^https?:$/i.test(location.protocol)) {
      return location.origin;
    }
    return "http://rpc.cellframe.net";
  }

  function initValues() {
    for (const ep of RPC_CATALOG) {
      state.values[ep.id] = {};
      for (const p of ep.params) {
        state.values[ep.id][p.name] = p.default != null ? String(p.default) : "";
      }
    }
  }

  function tags() {
    const set = [];
    for (const ep of RPC_CATALOG) {
      if (!set.includes(ep.tag)) set.push(ep.tag);
    }
    return set;
  }

  function filtered(tag) {
    const q = state.filter.trim().toLowerCase();
    return RPC_CATALOG.filter((ep) => {
      if (ep.tag !== tag) return false;
      if (!q) return true;
      return (
        ep.method.includes(q) ||
        ep.subcommand.toLowerCase().includes(q) ||
        ep.summary.toLowerCase().includes(q) ||
        ep.id.includes(q)
      );
    });
  }

  function buildPayload(ep) {
    const vals = state.values[ep.id] || {};
    const version = Number(state.version) || 2;
    const id = state.idCounter++;

    if (ep.method === "help" && ep.id === "help-cmd") {
      const cmd = (vals.command || "").trim() || "wallet";
      if (version === 1) {
        return { method: "help", params: ["help;" + cmd], id, version: 1 };
      }
      return { method: "help", subcommand: cmd, id, version: 2 };
    }

    if (version === 1) {
      const parts = [ep.method];
      if (ep.subcommand) {
        ep.subcommand.split(";").forEach((t) => {
          if (t) parts.push(t);
        });
      }
      for (const p of ep.params) {
        if (p.name === "command") continue;
        const v = vals[p.name];
        if (p.flag) {
          if (v === true || v === "1" || v === "true" || v === "on" || v === "") {
            /* empty string for checked flag in our UI means include */
            if (v === "" && document.querySelector(`[data-flag="${ep.id}:${p.name}"]`) && !document.querySelector(`[data-flag="${ep.id}:${p.name}"]`).checked)
              continue;
            if (v === "0" || v === "false") continue;
            parts.push("-" + p.name);
          }
          continue;
        }
        if (v == null || String(v).trim() === "") continue;
        parts.push("-" + p.name, String(v).trim());
      }
      return { method: ep.method, params: [parts.join(";")], id, version: 1 };
    }

    /* version 2 */
    const payload = { method: ep.method, id, version: 2 };
    if (ep.subcommand) payload.subcommand = ep.subcommand;
    const argumentsObj = {};
    let hasArgs = false;
    for (const p of ep.params) {
      if (p.name === "command") continue;
      const v = vals[p.name];
      if (p.flag) {
        const el = document.querySelector(`[data-flag="${ep.id}:${p.name}"]`);
        if (el && el.checked) {
          argumentsObj[p.name] = "";
          hasArgs = true;
        }
        continue;
      }
      if (v == null || String(v).trim() === "") continue;
      argumentsObj[p.name] = String(v).trim();
      hasArgs = true;
    }
    if (hasArgs) payload.arguments = argumentsObj;
    return payload;
  }

  function statusColor(code) {
    if (code >= 200 && code < 300) return "var(--color-green)";
    if (code >= 400 && code < 500) return "var(--color-orange)";
    return "var(--color-red)";
  }

  function fmtBody(body) {
    try {
      return JSON.stringify(JSON.parse(body), null, 2);
    } catch (_) {
      return body;
    }
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function tryIt(ep) {
    const id = ep.id;
    state.errors[id] = "";
    state.results[id] = null;

    const vals = state.values[id] || {};
    const missing = ep.params.filter((p) => {
      if (!p.required || p.flag) return false;
      if (p.name === "command") return !(vals.command || "").trim();
      return !(vals[p.name] || "").trim();
    });
    if (missing.length) {
      state.errors[id] = "Required: " + missing.map((p) => p.name).join(", ");
      render();
      return;
    }

    state.loading[id] = true;
    render();

    const payload = buildPayload(ep);
    const server = state.server.replace(/\/+$/, "");
    const t0 = performance.now();
    try {
      const res = await fetch(server || "/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const text = await res.text();
      state.results[id] = {
        status: res.status,
        body: text,
        time: Math.round(performance.now() - t0),
        request: payload
      };
    } catch (e) {
      state.results[id] = {
        status: 0,
        body: String(e && e.message ? e.message : e),
        time: Math.round(performance.now() - t0),
        request: payload
      };
    }
    state.loading[id] = false;
    render();
  }

  function renderParams(ep) {
    if (!ep.params.length) return "<p class=\"api-note\">No parameters</p>";
    const rows = ep.params
      .map((p) => {
        const val = (state.values[ep.id] && state.values[ep.id][p.name]) || "";
        let control;
        if (p.flag) {
          const checked = document.querySelector(`[data-flag="${ep.id}:${p.name}"]`)
            ? document.querySelector(`[data-flag="${ep.id}:${p.name}"]`).checked
            : false;
          control = `<label class="api-flag"><input type="checkbox" data-flag="${escapeHtml(ep.id)}:${escapeHtml(p.name)}" ${checked ? "checked" : ""}> include -${escapeHtml(p.name)}</label>`;
        } else if (p.enum && p.enum.length) {
          control =
            `<select data-param="${escapeHtml(ep.id)}:${escapeHtml(p.name)}">` +
            p.enum
              .map((opt) => `<option value="${escapeHtml(opt)}" ${opt === val ? "selected" : ""}>${escapeHtml(opt || "(empty)")}</option>`)
              .join("") +
            `</select>`;
        } else {
          control = `<input type="text" data-param="${escapeHtml(ep.id)}:${escapeHtml(p.name)}" value="${escapeHtml(val)}" placeholder="${escapeHtml(p.description || "")}">`;
        }
        return `<tr>
          <td><code>${escapeHtml(p.name)}</code></td>
          <td><span class="api-pill">${p.flag ? "flag" : "arg"}</span></td>
          <td>${escapeHtml(p.type || "string")}</td>
          <td>${p.required ? "✓" : ""}</td>
          <td>${control}</td>
        </tr>`;
      })
      .join("");
    return `<div class="api-params-wrap"><table class="api-params">
      <thead><tr><th>Name</th><th>In</th><th>Type</th><th>Req</th><th>Value</th></tr></thead>
      <tbody>${rows}</tbody>
    </table></div>`;
  }

  function renderEndpoint(ep) {
    const open = !!state.expanded[ep.id];
    const pathLabel = ep.subcommand ? `${ep.method} / ${ep.subcommand}` : ep.method;
    let body = "";
    if (open) {
      const preview = buildPayload(ep);
      const result = state.results[ep.id];
      body = `<div class="api-endpoint-body">
        ${ep.warn ? `<p class="api-note" style="color:var(--color-orange)">${escapeHtml(ep.warn)}</p>` : ""}
        <h4>Parameters</h4>
        ${renderParams(ep)}
        <h4>Request preview (API v${state.version})</h4>
        <div class="api-preview"><pre class="api-result-body">${escapeHtml(JSON.stringify(preview, null, 2))}</pre></div>
        <div class="api-actions">
          <button class="api-try" data-try="${escapeHtml(ep.id)}" ${state.loading[ep.id] ? "disabled" : ""}>${state.loading[ep.id] ? "Loading..." : "Try it out"}</button>
          ${state.errors[ep.id] ? `<span class="api-err">${escapeHtml(state.errors[ep.id])}</span>` : ""}
          ${
            result
              ? `<span class="api-status" style="color:${statusColor(result.status)}">${result.status || "ERR"}</span><span class="api-time">${result.time}ms</span>`
              : ""
          }
          <a class="dex-nav-btn" href="${escapeHtml(ep.docs)}" style="margin-left:auto">Full docs →</a>
        </div>
        ${
          result
            ? `<div class="api-result">
                <div class="api-result-head"><span>Response</span><button class="api-copy" data-copy="${escapeHtml(ep.id)}">Copy</button></div>
                <pre class="api-result-body">${escapeHtml(fmtBody(result.body))}</pre>
              </div>`
            : ""
        }
      </div>`;
    }
    return `<div class="api-endpoint ${open ? "api-endpoint--open" : ""}">
      <button class="api-endpoint-header" data-toggle="${escapeHtml(ep.id)}">
        <span class="api-method">POST</span>
        <span class="api-path">${escapeHtml(pathLabel)}</span>
        <span class="api-summary">${escapeHtml(ep.summary)}</span>
        <span class="api-chevron ${open ? "api-chevron--open" : ""}">
          <svg width="18" height="18" viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
      </button>
      ${body}
    </div>`;
  }

  function render() {
    const root = document.getElementById("rpc-root");
    if (!root) return;

    const panels = tags()
      .map((tag) => {
        const eps = filtered(tag);
        if (!eps.length) return "";
        const docs = "/" + tag + ".html";
        return `<section class="api-panel" id="tag-${escapeHtml(tag)}">
          <div class="api-panel-head">
            <h2>${escapeHtml(tag)}</h2>
            <a href="${escapeHtml(docs)}">${escapeHtml(tag)}.html</a>
          </div>
          <div class="api-endpoints">${eps.map(renderEndpoint).join("")}</div>
        </section>`;
      })
      .join("");

    const refLinks = [
      "version", "help", "wallet", "net", "tx_history", "mempool", "srv_xchange",
      "stake_lock", "net_srv", "tx_create_json", "block", "ledger", "token"
    ]
      .map((n) => `<a href="/${n}.html">${n}</a>`)
      .join("");

    root.innerHTML = `
      <div class="api-shell">
        <nav class="dex-top-nav" aria-label="Page navigation">
          <a class="dex-nav-brand" href="/" aria-label="Cellframe">
            <img src="/logo.svg" alt="Cellframe DEX" decoding="async" />
          </a>
          <span class="dex-nav-btn" style="cursor:default">Node RPC</span>
        </nav>

        <header class="api-hero">
          <div class="api-hero-badge">Developer</div>
          <h1>Node RPC Reference</h1>
          <p class="api-hero-lead">
            Interactive JSON-RPC for Cellframe Node CLI server. Try requests in the browser
            (Swagger-style). Use API version 2 for <code>subcommand</code> + <code>arguments</code>
            (no semicolon string), or version 1 for legacy <code>params[0]</code>.
          </p>
          <ul class="api-meta" aria-label="Page summary">
            <li><span class="api-meta-value">v${state.version}</span><span class="api-meta-label">api</span></li>
            <li><span class="api-meta-value">${RPC_CATALOG.length}</span><span class="api-meta-label">endpoints</span></li>
            <li><span class="api-meta-value">${tags().length}</span><span class="api-meta-label">modules</span></li>
          </ul>
        </header>

        <div class="api-controls">
          <div class="api-server">
            <span class="api-server-label">Server</span>
            <input id="rpc-server" type="text" value="${escapeHtml(state.server)}" />
          </div>
          <div class="api-version">
            <span class="api-version-label">API</span>
            <select id="rpc-version">
              <option value="2" ${state.version === 2 ? "selected" : ""}>v2 · subcommand + arguments</option>
              <option value="1" ${state.version === 1 ? "selected" : ""}>v1 · params string</option>
            </select>
          </div>
          <input id="rpc-filter" class="api-filter" type="text" placeholder="Filter endpoints..." value="${escapeHtml(state.filter)}" />
        </div>

        ${panels}

        <section class="api-panel">
          <div class="api-panel-head"><h2>Reference pages</h2></div>
          <p class="api-note">Deep documentation for schemas, errors, and response field differences between API v1 and v2.</p>
          <div class="api-refs" style="margin-top:12px">${refLinks}</div>
        </section>
      </div>
    `;

    bind();
  }

  function bind() {
    const serverInput = document.getElementById("rpc-server");
    if (serverInput) {
      serverInput.addEventListener("change", () => {
        state.server = serverInput.value.trim();
        try {
          localStorage.setItem(STORAGE_KEY, state.server);
        } catch (_) {}
      });
      serverInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          state.server = serverInput.value.trim();
          try {
            localStorage.setItem(STORAGE_KEY, state.server);
          } catch (_) {}
        }
      });
    }

    const versionSelect = document.getElementById("rpc-version");
    if (versionSelect) {
      versionSelect.addEventListener("change", () => {
        state.version = Number(versionSelect.value) || 2;
        render();
      });
    }

    const filterInput = document.getElementById("rpc-filter");
    if (filterInput) {
      filterInput.addEventListener("input", () => {
        state.filter = filterInput.value;
        render();
        const el = document.getElementById("rpc-filter");
        if (el) {
          el.focus();
          const len = el.value.length;
          el.setSelectionRange(len, len);
        }
      });
    }

    document.querySelectorAll("[data-toggle]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-toggle");
        state.expanded[id] = !state.expanded[id];
        render();
      });
    });

    document.querySelectorAll("[data-param]").forEach((input) => {
      const key = input.getAttribute("data-param");
      const [epId, name] = key.split(":");
      const handler = () => {
        if (!state.values[epId]) state.values[epId] = {};
        state.values[epId][name] = input.value;
        /* live-update preview without full remount of inputs focus loss:
           small defer — full render is ok for select; for text use lighter update */
      };
      input.addEventListener("change", () => {
        handler();
        render();
      });
      if (input.tagName === "INPUT") {
        input.addEventListener("input", () => {
          handler();
          const preview = input.closest(".api-endpoint-body");
          if (!preview) return;
          const ep = RPC_CATALOG.find((e) => e.id === epId);
          if (!ep) return;
          const pre = preview.querySelector(".api-preview .api-result-body");
          if (pre) pre.textContent = JSON.stringify(buildPayload(ep), null, 2);
        });
      }
    });

    document.querySelectorAll("[data-flag]").forEach((input) => {
      input.addEventListener("change", () => {
        const ep = RPC_CATALOG.find((e) => e.id === input.getAttribute("data-flag").split(":")[0]);
        if (!ep) return;
        const preview = input.closest(".api-endpoint-body");
        const pre = preview && preview.querySelector(".api-preview .api-result-body");
        if (pre) pre.textContent = JSON.stringify(buildPayload(ep), null, 2);
      });
    });

    document.querySelectorAll("[data-try]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const ep = RPC_CATALOG.find((e) => e.id === btn.getAttribute("data-try"));
        if (ep) tryIt(ep);
      });
    });

    document.querySelectorAll("[data-copy]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-copy");
        const body = state.results[id] && state.results[id].body;
        if (body != null) navigator.clipboard.writeText(body);
      });
    });
  }

  state.server = defaultServer();
  state.version = 2;
  initValues();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
  } else {
    render();
  }
})();
