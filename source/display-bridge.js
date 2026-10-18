/* Load inside the same-origin Xpra HTML5 v21 display page. No application restarts. */
(function (root) {
  'use strict';
  function text(value) {
    if (typeof value === 'string') return value;
    if (value instanceof Uint8Array || Array.isArray(value)) return new TextDecoder().decode(new Uint8Array(value));
    return '';
  }
  function containerFor(metadata, registry) {
    const machine = text(metadata['client-machine']).toLowerCase();
    if (!machine) return null;
    const row = registry.find(row => String(row.hostname || '').toLowerCase() === machine);
    return row && ['A', 'B', 'C'].includes(row.id) ? row.id : null;
  }
  function positions(windows, width, height) {
    const result = [];
    const gap = 10;
    ['A', 'B', 'C'].forEach((id, column) => {
      const list = windows.filter(win => win.container === id);
      const areaWidth = Math.floor(width / 3);
      const columns = list.length > 2 ? 2 : 1;
      const rows = Math.max(1, Math.ceil(list.length / columns));
      list.forEach((win, index) => result.push({
        id: win.id,
        x: column * areaWidth + gap + (index % columns) * Math.floor((areaWidth - gap) / columns),
        y: gap + Math.floor(index / columns) * Math.floor((height - gap) / rows),
        width: Math.max(100, Math.floor((areaWidth - gap) / columns) - gap),
        height: Math.max(80, Math.floor((height - gap) / rows) - gap),
      }));
    });
    return result;
  }
  const api = {text, containerFor, positions};
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }
  let mode = 'unified', registry = [], previousSignature = '';
  const saved = new Map(), widgetState = new Map();
  const getClient = () => (typeof client !== 'undefined' && client) || root.client || root.xpra_client;
  function geometry(win, values) {
    if ([win.x, win.y, win.w, win.h].every((v, index) => v === values[index])) return;
    win.move_resize(...values);
    if (typeof win.handle_resized === 'function') win.handle_resized();
    else if (typeof win.geometry_cb === 'function') win.geometry_cb(win);
  }
  function windows() {
    const c = getClient();
    const mapping = c && c.id_to_window;
    if (!mapping) return [];
    return Object.values(mapping).filter(win => win && !win.tray && !win.override_redirect && typeof win.move_resize === 'function');
  }
  function widgets(win, lock) {
    if (!root.jQuery || !win.div) return;
    const element = root.jQuery(win.div);
    if (!widgetState.has(win.wid)) {
      const state = {};
      for (const name of ['draggable', 'resizable']) {
        if (element.data('ui-' + name)) state[name] = element[name]('option', 'disabled');
      }
      widgetState.set(win.wid, state);
    }
    for (const [name, disabled] of Object.entries(widgetState.get(win.wid))) {
      if (element.data('ui-' + name)) element[name]('option', 'disabled', lock || disabled);
    }
  }
  function apply(force = false) {
    const live = windows();
    const signature = [mode, root.innerWidth, root.innerHeight, ...live.map(win => win.wid + ':' + containerFor(win.metadata || {}, registry))].join('|');
    if (!force && signature === previousSignature) return;
    previousSignature = signature;
    const byId = new Map(live.map(win => [win.wid, win]));
    for (const id of saved.keys()) if (!byId.has(id)) { saved.delete(id); widgetState.delete(id); }
    if (mode === 'monitor') {
      const registered = live.map(win => ({id: win.wid, container: containerFor(win.metadata || {}, registry)}));
      for (const win of live) {
        if (!registered.find(row => row.id === win.wid).container) continue;
        if (!saved.has(win.wid)) saved.set(win.wid, [win.x, win.y, win.w, win.h]);
        widgets(win, true);
      }
      for (const box of positions(registered, root.innerWidth, root.innerHeight)) {
        geometry(byId.get(box.id), [box.x, box.y, box.width, box.height]);
      }
      const unknown = registered.filter(row => !row.container).length;
      root.parent.postMessage({type: 'unified-layout-status', mode, windows: live.length, unregistered: unknown}, root.location.origin);
    } else {
      for (const win of live) {
        widgets(win, false);
        if (saved.has(win.wid)) { geometry(win, saved.get(win.wid)); saved.delete(win.wid); }
      }
      root.parent.postMessage({type: 'unified-layout-status', mode, windows: live.length, unregistered: 0}, root.location.origin);
    }
  }
  root.addEventListener('message', event => {
    if (event.source !== root.parent || event.origin !== root.location.origin) return;
    if (event.data?.type !== 'unified-layout' || !['unified', 'monitor'].includes(event.data.mode)) return;
    mode = event.data.mode;
    apply(true);
  });
  root.addEventListener('resize', () => apply(true));
  async function refreshRegistry() {
    try {
      const response = await fetch('/api/workbench/status', {cache: 'no-store', signal: AbortSignal.timeout(5000)});
      if (!response.ok) return;
      const data = await response.json();
      registry = data.containers || [];
      apply();
    } catch (_) { /* The next sample retries read-only registry lookup. */ }
  }
  refreshRegistry();
  setInterval(refreshRegistry, 10000);
  setInterval(() => apply(), 1000);
  root.UnifiedDisplayBridge = api;
})(typeof window === 'undefined' ? globalThis : window);
