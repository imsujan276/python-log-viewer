"""
Self-contained HTML / CSS / JS template for the log viewer UI.

The single placeholder ``{{BASE_URL}}`` is replaced at render time with
the mount prefix (e.g. ``/logs``, ``/log_viewer``, or just `` ``).

The template has **zero** external dependencies – no CDN links.
"""

from __future__ import annotations

_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Log Viewer</title>
<style>
  :root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --text-muted: #8b949e;
    --accent: #58a6ff;
    --info: #58a6ff;
    --warning: #d29922;
    --error: #f85149;
    --debug: #8b949e;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* ---- Header / toolbar ---- */
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
  }
  header h1 {
    font-size: 16px;
    font-weight: 600;
    color: var(--accent);
    white-space: nowrap;
  }
  .controls {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    flex: 1;
  }
  .controls input[type="text"],
  .controls select {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 12px;
    color: var(--text);
    font-size: 13px;
    font-family: inherit;
    outline: none;
    transition: border-color 0.2s;
  }
  .controls input[type="text"] { width: 200px; }
  .controls input[type="text"]:focus,
  .controls select:focus { border-color: var(--accent); }
  .controls select { cursor: pointer; }
  .controls label {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 13px;
    color: var(--text-muted);
    cursor: pointer;
    white-space: nowrap;
  }
  .controls input[type="checkbox"] { accent-color: var(--accent); }
  .btn {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 14px;
    color: var(--text);
    font-size: 13px;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .btn:hover { border-color: var(--accent); color: var(--accent); }
  .btn-danger { color: var(--error); border-color: var(--border); }
  .btn-danger:hover { border-color: var(--error); color: var(--error); background: rgba(248,81,73,0.1); }
  .btn-warn { color: var(--warning); border-color: var(--border); }
  .btn-warn:hover { border-color: var(--warning); color: var(--warning); background: rgba(210,153,34,0.1); }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; pointer-events: none; }

  /* ---- Toast notification ---- */
  .toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 10px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-family: inherit;
    color: var(--text);
    background: var(--surface);
    border: 1px solid var(--border);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    z-index: 1000;
    opacity: 0;
    transform: translateY(10px);
    transition: opacity 0.3s, transform 0.3s;
  }
  .toast.show { opacity: 1; transform: translateY(0); }
  .toast.success { border-color: #3fb950; }
  .toast.error { border-color: var(--error); }

  /* ---- Confirm modal ---- */
  .modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    z-index: 999;
    align-items: center;
    justify-content: center;
  }
  .modal-overlay.active { display: flex; }
  .modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 24px;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
  }
  .modal h3 { font-size: 15px; margin-bottom: 10px; }
  .modal p { font-size: 13px; color: var(--text-muted); margin-bottom: 18px; line-height: 1.5; }
  .modal-actions { display: flex; gap: 10px; justify-content: flex-end; }

  /* ---- Main layout: sidebar + log pane ---- */
  .main-layout {
    flex: 1;
    display: flex;
    overflow: hidden;
  }

  /* ---- Sidebar ---- */
  .sidebar {
    width: 300px;
    min-width: 240px;
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .sidebar-header {
    padding: 12px 14px 8px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border);
  }
  .file-list {
    flex: 1;
    overflow-y: auto;
    padding: 6px 0;
  }
  .folder-group { margin-bottom: 2px; }
  .folder-header {
    padding: 8px 10px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    user-select: none;
    transition: color 0.15s;
  }
  .folder-header:hover { color: var(--text); }
  .folder-header .folder-icon { font-size: 10px; transition: transform 0.2s; display: inline-block; }
  .folder-header.collapsed .folder-icon { transform: rotate(-90deg); }
  .folder-children { overflow: hidden; }
  .folder-children.collapsed { display: none; }
  .file-item {
    padding: 6px 10px 6px 28px;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
    transition: background 0.15s;
    border-left: 3px solid transparent;
  }
  .file-item:hover { background: rgba(88,166,255,0.06); }
  .file-item.active {
    background: rgba(88,166,255,0.1);
    border-left-color: var(--accent);
    color: var(--accent);
  }
  .file-item .file-name {
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    word-break: break-all;
    line-height: 1.4;
    min-width: 0;
  }
  .file-item .file-size {
    font-size: 11px;
    color: var(--text-muted);
    flex-shrink: 0;
    white-space: nowrap;
    padding-top: 1px;
  }

  /* ---- Status bar ---- */
  .status-bar {
    font-size: 12px;
    color: var(--text-muted);
    margin-left: auto;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .status-bar .dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #3fb950;
    animation: pulse 2s infinite;
  }
  .status-bar .dot.paused { background: var(--warning); animation: none; }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  /* ---- Log pane ---- */
  .log-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0;
  }
  .log-pane-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 20px;
    font-size: 13px;
    color: var(--text-muted);
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .log-pane-header .file-icon { font-size: 14px; }
  .log-pane-header .active-file-name {
    color: var(--accent);
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  #log-container {
    flex: 1;
    overflow-y: auto;
    padding: 12px 20px;
  }
  .log-line {
    padding: 3px 0;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-all;
    border-bottom: 1px solid transparent;
  }
  .log-line:hover { background: rgba(88,166,255,0.04); }
  .log-line.level-INFO .level-tag { color: var(--info); }
  .log-line.level-WARNING .level-tag { color: var(--warning); }
  .log-line.level-ERROR .level-tag { color: var(--error); }
  .log-line.level-DEBUG .level-tag { color: var(--debug); }

  /* ---- Colorized log-level backgrounds ---- */
  body.colorize .log-line.level-INFO    { background: rgba(56,139,253,0.06); border-left: 3px solid rgba(56,139,253,0.3); padding-left: 8px; }
  body.colorize .log-line.level-WARNING { background: rgba(210,153,34,0.07); border-left: 3px solid rgba(210,153,34,0.35); padding-left: 8px; }
  body.colorize .log-line.level-ERROR   { background: rgba(248,81,73,0.08); border-left: 3px solid rgba(248,81,73,0.4); padding-left: 8px; }
  body.colorize .log-line.level-DEBUG   { background: rgba(139,148,158,0.05); border-left: 3px solid rgba(139,148,158,0.25); padding-left: 8px; }
  body.colorize .log-line.level-INFO:hover    { background: rgba(56,139,253,0.1); }
  body.colorize .log-line.level-WARNING:hover { background: rgba(210,153,34,0.12); }
  body.colorize .log-line.level-ERROR:hover   { background: rgba(248,81,73,0.13); }
  body.colorize .log-line.level-DEBUG:hover   { background: rgba(139,148,158,0.08); }
  .log-line .timestamp { color: var(--text-muted); }
  .log-line .logger-name { color: #d2a8ff; }
  .log-line .highlight { background: rgba(210,153,34,0.3); border-radius: 2px; padding: 0 2px; }
  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
    font-size: 14px;
  }

  /* ---- Log loader ---- */
  .log-loader {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
    font-size: 14px;
    gap: 10px;
  }
  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ---- Pagination ---- */
  .pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 20px;
    background: var(--surface);
    border-top: 1px solid var(--border);
    font-size: 13px;
    color: var(--text-muted);
    flex-shrink: 0;
  }
  .pagination .btn { padding: 4px 12px; font-size: 12px; }
  .pagination .page-info { white-space: nowrap; }

  /* ---- Sidebar toggle button (small screens) ---- */
  .sidebar-toggle {
    display: none;
    background: none;
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-size: 18px;
    padding: 4px 8px;
    cursor: pointer;
    line-height: 1;
    transition: border-color 0.2s, color 0.2s;
  }
  .sidebar-toggle:hover { border-color: var(--accent); color: var(--accent); }

  /* ---- Sidebar overlay (small screens) ---- */
  .sidebar-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 49;
  }
  .sidebar-overlay.active { display: block; }

  /* ---- Responsive ---- */
  @media (max-width: 768px) {
    .sidebar-toggle { display: inline-flex; }
    .sidebar {
      position: fixed;
      top: 0;
      left: 0;
      bottom: 0;
      z-index: 50;
      transform: translateX(-100%);
      transition: transform 0.25s ease;
      width: 280px;
      min-width: 0;
    }
    .sidebar.open { transform: translateX(0); }
  }
</style>
</head>
<body class="{{BODY_CLASS}}">

<header>
  <button class="sidebar-toggle" id="sidebar-toggle" onclick="toggleSidebar()" title="Toggle sidebar">&#9776;</button>
  <h1>&#128203; Log Viewer</h1>
  <div class="controls">
    <input type="text" id="search" placeholder="Search logs..." />
    <select id="level-filter">
      <option value="">All Levels</option>
      <option value="DEBUG">DEBUG</option>
      <option value="INFO">INFO</option>
      <option value="WARNING">WARNING</option>
      <option value="ERROR">ERROR</option>
    </select>
    <select id="lines-limit">
      <option value="100" {{LINES_100_SELECTED}}>Last 100</option>
      <option value="250" {{LINES_250_SELECTED}}>Last 250</option>
      <option value="500" {{LINES_500_SELECTED}}>Last 500</option>
      <option value="1000" {{LINES_1000_SELECTED}}>Last 1000</option>
      <option value="0" {{LINES_0_SELECTED}}>All</option>
    </select>
    <select id="refresh-interval">
      <option value="5000" {{REFRESH_5000_SELECTED}}>Refresh: 5s</option>
      <option value="10000" {{REFRESH_10000_SELECTED}}>Refresh: 10s</option>
      <option value="30000" {{REFRESH_30000_SELECTED}}>Refresh: 30s</option>
      <option value="60000" {{REFRESH_60000_SELECTED}}>Refresh: 1m</option>
      <option value="0" {{REFRESH_0_SELECTED}}>Manual Refresh</option>
    </select>
    <label><input type="checkbox" id="auto-scroll" {{AUTO_SCROLL_CHECKED}} /> Auto-scroll</label>
    <button class="btn" onclick="fetchLogs()">&#8635; Refresh</button>
    <button class="btn btn-warn" id="btn-clear" onclick="confirmAction('clear')" disabled>&#128465; Clear</button>
    <button class="btn btn-danger" id="btn-delete" onclick="confirmAction('delete')" disabled>&#10005; Delete</button>
    <span class="status-bar">
      <span class="dot" id="status-dot"></span>
      <span id="status-text">Live</span> &middot;
      <span id="line-count">0</span> entries
    </span>
  </div>
</header>

<div class="sidebar-overlay" id="sidebar-overlay" onclick="toggleSidebar()"></div>

<div class="main-layout">
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">Log Files</div>
    <div class="file-list" id="file-list">
      <div class="empty-state" style="padding:20px;font-size:12px;">Loading&hellip;</div>
    </div>
  </aside>

  <div class="log-pane">
    <div class="log-pane-header" id="log-pane-header" style="display:none;">
      <span class="file-icon">&#128196;</span>
      <span class="active-file-name" id="active-file-label"></span>
    </div>
    <div id="log-container">
      <div class="empty-state" id="empty-state">Select a log file to view</div>
    </div>
    <div class="pagination" id="pagination" style="display:none;">
      <button class="btn" id="btn-first" onclick="goPage(1)" title="First page (newest)">&#8676; First</button>
      <button class="btn" id="btn-prev" onclick="goPage(currentPage - 1)">&#8592; Previous</button>
      <span class="page-info" id="page-info">Page 1 of 1</span>
      <button class="btn" id="btn-next" onclick="goPage(currentPage + 1)">Next &#8594;</button>
      <button class="btn" id="btn-last" onclick="goPage(totalPages)" title="Last page (oldest)">Last &#8677;</button>
    </div>
  </div>
</div>

<!-- Confirm modal -->
<div class="modal-overlay" id="modal-overlay">
  <div class="modal">
    <h3 id="modal-title">Confirm</h3>
    <p id="modal-message">Are you sure?</p>
    <div class="modal-actions">
      <button class="btn" onclick="closeModal()">Cancel</button>
      <button class="btn btn-danger" id="modal-confirm" onclick="executeAction()">Confirm</button>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
  const BASE = '{{BASE_URL}}'.replace(/\/+$/, '');
  const sidebarEl = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebar-overlay');
  const container = document.getElementById('log-container');
  const emptyState = document.getElementById('empty-state');
  const fileListEl = document.getElementById('file-list');
  const searchInput = document.getElementById('search');
  const levelFilter = document.getElementById('level-filter');
  const linesLimit = document.getElementById('lines-limit');
  const refreshSelect = document.getElementById('refresh-interval');
  const autoScrollCb = document.getElementById('auto-scroll');
  const lineCountEl = document.getElementById('line-count');
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');

  const btnClear = document.getElementById('btn-clear');
  const btnDelete = document.getElementById('btn-delete');
  const modalOverlay = document.getElementById('modal-overlay');
  const modalTitle = document.getElementById('modal-title');
  const modalMessage = document.getElementById('modal-message');
  const modalConfirmBtn = document.getElementById('modal-confirm');
  const toastEl = document.getElementById('toast');
  const logPaneHeader = document.getElementById('log-pane-header');
  const activeFileLabel = document.getElementById('active-file-label');

  let refreshTimer = null;
  let activeFile = '';
  let pendingAction = null;
  let currentPage = 1;
  let totalPages = 1;
  let forceScrollToBottom = false;

  function toggleSidebar() {
    sidebarEl.classList.toggle('open');
    sidebarOverlay.classList.toggle('active');
  }
  function closeSidebar() {
    sidebarEl.classList.remove('open');
    sidebarOverlay.classList.remove('active');
  }

  function getFileFromURL() {
    const path = window.location.pathname;
    let basePath = (BASE || '').replace(/\/+$/, '');
    if (path === basePath || path === basePath + '/') return '';
    if (path.startsWith(basePath + '/')) {
      return decodeURIComponent(path.substring(basePath.length + 1));
    }
    return '';
  }

  function showLogLoader() {
    container.innerHTML = '<div class="log-loader"><div class="spinner"></div><span>Loading\u2026</span></div>';
    emptyState.style.display = 'none';
    var pg = document.getElementById('pagination');
    if (pg) pg.style.display = 'none';
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  function detectLevel(text) {
    if (text.includes('ERROR:') || text.includes('ERROR ')) return 'ERROR';
    if (text.includes('WARNING:') || text.includes('WARNING ')) return 'WARNING';
    if (text.includes('DEBUG:') || text.includes('DEBUG ')) return 'DEBUG';
    if (text.includes('INFO:') || text.includes('INFO ')) return 'INFO';
    return '';
  }

  function formatLine(raw) {
    const search = searchInput.value.trim();
    let text = raw
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)/g, '<span class="timestamp">$1</span>')
      .replace(/ - ([\w.]+)/g, ' - <span class="logger-name">$1</span>')
      .replace(/\b(INFO|WARNING|ERROR|DEBUG):/g, '<span class="level-tag">$1:</span>');
    if (search) {
      const escaped = search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      text = text.replace(new RegExp('(' + escaped + ')', 'gi'), '<span class="highlight">$1</span>');
    }
    return text;
  }

  function scrollToBottomNow() {
    // Run twice (now + next frame) to account for layout changes such as pagination.
    container.scrollTop = container.scrollHeight;
    requestAnimationFrame(() => {
      container.scrollTop = container.scrollHeight;
    });
  }

  function toggleFolder(btn) {
    btn.classList.toggle('collapsed');
    const children = btn.nextElementSibling;
    if (children) children.classList.toggle('collapsed');
    const folder = btn.getAttribute('data-folder');
    if (folder) {
      if (btn.classList.contains('collapsed')) collapsedFolders.add(folder);
      else collapsedFolders.delete(folder);
    }
  }

  const collapsedFolders = new Set();

  async function fetchFiles() {
    try {
      const resp = await fetch(BASE + '/api/files');
      const data = await resp.json();
      if (!data.files.length) {
        fileListEl.innerHTML = '<div class="empty-state" style="padding:20px;font-size:12px;">No log files found</div>';
        return;
      }

      const groups = {};
      data.files.forEach(f => {
        const sep = f.name.lastIndexOf('/');
        const folder = sep !== -1 ? f.name.substring(0, sep) : '';
        const fileName = sep !== -1 ? f.name.substring(sep + 1) : f.name;
        if (!groups[folder]) groups[folder] = [];
        groups[folder].push({ full: f.name, display: fileName, size: f.size });
      });

      let html = '';
      Object.keys(groups).sort().forEach(folder => {
        const files = groups[folder];
        const isCollapsed = collapsedFolders.has(folder);
        if (folder) {
          html += '<div class="folder-group">'
            + '<div class="folder-header' + (isCollapsed ? ' collapsed' : '') + '" data-folder="' + folder + '" onclick="toggleFolder(this)">'
            + '<span class="folder-icon">&#9660;</span> &#128193; ' + folder + '/'
            + '</div>'
            + '<div class="folder-children' + (isCollapsed ? ' collapsed' : '') + '">';
        }
        files.forEach(f => {
          const cls = f.full === activeFile ? ' active' : '';
          html += '<div class="file-item' + cls + '" data-file="' + f.full + '">'
            + '<span class="file-name">' + f.display + '</span>'
            + '<span class="file-size">' + formatBytes(f.size) + '</span>'
            + '</div>';
        });
        if (folder) {
          html += '</div></div>';
        }
      });
      fileListEl.innerHTML = html;

      if (!activeFile && data.files.length) {
        var urlFile = getFileFromURL();
        if (urlFile && data.files.some(function(f){ return f.name === urlFile; })) {
          selectFile(urlFile, false);
        } else {
          selectFile(data.files[0].name);
        }
      }
    } catch (e) {
      console.error('Failed to fetch file list:', e);
    }
  }

  function selectFile(name, pushHistory) {
    if (pushHistory === undefined) pushHistory = true;
    activeFile = name;
    currentPage = 1;
    document.querySelectorAll('.file-item').forEach(el => {
      el.classList.toggle('active', el.dataset.file === name);
    });
    activeFileLabel.textContent = name;
    logPaneHeader.style.display = name ? 'flex' : 'none';
    updateActionButtons();
    closeSidebar();
    if (pushHistory) {
      var newUrl = (BASE || '') + '/' + name.split('/').map(encodeURIComponent).join('/');
      history.pushState({file: name}, '', newUrl);
    }
    showLogLoader();
    fetchLogs();
  }

  fileListEl.addEventListener('click', (e) => {
    const item = e.target.closest('.file-item');
    if (item) selectFile(item.dataset.file);
  });

  async function fetchLogs() {
    if (!activeFile) return;
    try {
      const shouldForceScrollToBottom = forceScrollToBottom;
      forceScrollToBottom = false;
      const lines = parseInt(linesLimit.value);
      const params = new URLSearchParams({ file: activeFile, lines: lines, page: currentPage });
      const level = levelFilter.value;
      const search = searchInput.value.trim();
      if (level) params.set('level', level);
      if (search) params.set('search', search);

      const resp = await fetch(BASE + '/api/content?' + params.toString());
      const data = await resp.json();
      lineCountEl.textContent = data.total;
      totalPages = data.total_pages || 1;
      currentPage = data.page || 1;

      if (!data.lines.length) {
        container.innerHTML = '';
        emptyState.style.display = 'flex';
        emptyState.textContent = 'No log entries found.';
        container.appendChild(emptyState);
        updatePagination();
        return;
      }

      emptyState.style.display = 'none';

      const scrollThreshold = 200;
      const wasNearBottom = (container.scrollHeight - container.scrollTop - container.clientHeight) < scrollThreshold;

      container.innerHTML = data.lines.map(line => {
        const lvl = detectLevel(line);
        return '<div class="log-line' + (lvl ? ' level-' + lvl : '') + '">' + formatLine(line) + '</div>';
      }).join('');

      if (shouldForceScrollToBottom) {
        // Page navigation should land at the newest visible entry immediately.
        scrollToBottomNow();
      } else if (autoScrollCb.checked && wasNearBottom && currentPage === 1) {
        scrollToBottomNow();
      }

      updatePagination();
    } catch (e) {
      console.error('Failed to fetch logs:', e);
    }
  }

  function updatePagination() {
    var pg = document.getElementById('pagination');
    if (totalPages <= 1) { pg.style.display = 'none'; return; }
    pg.style.display = 'flex';
    document.getElementById('page-info').textContent = 'Page ' + currentPage + ' of ' + totalPages;
    document.getElementById('btn-first').disabled = currentPage <= 1;
    document.getElementById('btn-prev').disabled = currentPage <= 1;
    document.getElementById('btn-next').disabled = currentPage >= totalPages;
    document.getElementById('btn-last').disabled = currentPage >= totalPages;
  }

  function goPage(p) {
    if (p < 1 || p > totalPages) return;
    currentPage = p;
    forceScrollToBottom = true;
    showLogLoader();
    fetchLogs();
  }

  function startRefresh() {
    if (refreshTimer) clearInterval(refreshTimer);
    const interval = parseInt(refreshSelect.value);
    if (interval > 0) {
      refreshTimer = setInterval(() => { fetchLogs(); fetchFiles(); }, interval);
      statusDot.classList.remove('paused');
      statusText.textContent = 'Live';
    } else {
      statusDot.classList.add('paused');
      statusText.textContent = 'Paused';
    }
  }

  let searchTimeout;
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    currentPage = 1;
    searchTimeout = setTimeout(fetchLogs, 400);
  });
  levelFilter.addEventListener('change', () => { currentPage = 1; fetchLogs(); });
  linesLimit.addEventListener('change', () => { currentPage = 1; fetchLogs(); });
  refreshSelect.addEventListener('change', startRefresh);

  function updateActionButtons() {
    const hasFile = !!activeFile;
    btnClear.disabled = !hasFile;
    btnDelete.disabled = !hasFile;
  }

  function showToast(message, type) {
    type = type || 'success';
    toastEl.textContent = message;
    toastEl.className = 'toast ' + type + ' show';
    setTimeout(() => { toastEl.classList.remove('show'); }, 3000);
  }

  function confirmAction(action) {
    if (!activeFile) return;
    pendingAction = action;
    if (action === 'clear') {
      modalTitle.textContent = 'Clear log file';
      modalMessage.textContent = 'This will erase all content in "' + activeFile + '" but keep the file. Continue?';
      modalConfirmBtn.className = 'btn btn-warn';
      modalConfirmBtn.textContent = 'Clear';
    } else {
      modalTitle.textContent = 'Delete log file';
      modalMessage.textContent = 'This will permanently delete "' + activeFile + '". This cannot be undone. Continue?';
      modalConfirmBtn.className = 'btn btn-danger';
      modalConfirmBtn.textContent = 'Delete';
    }
    modalOverlay.classList.add('active');
  }

  function closeModal() {
    modalOverlay.classList.remove('active');
    pendingAction = null;
  }

  async function executeAction() {
    if (!pendingAction || !activeFile) return;
    const action = pendingAction;
    closeModal();
    try {
      let resp;
      if (action === 'clear') {
        resp = await fetch(BASE + '/api/clear?file=' + encodeURIComponent(activeFile), { method: 'POST' });
      } else {
        resp = await fetch(BASE + '/api/file?file=' + encodeURIComponent(activeFile), { method: 'DELETE' });
      }
      const data = await resp.json();
      if (data.success) {
        showToast(data.message, 'success');
        if (action === 'delete') {
          activeFile = '';
          activeFileLabel.textContent = '';
          logPaneHeader.style.display = 'none';
          updateActionButtons();
          history.pushState({}, '', BASE || '/');
        }
        await fetchFiles();
        if (activeFile) fetchLogs();
        else {
          container.innerHTML = '';
          emptyState.style.display = 'flex';
          emptyState.textContent = 'Select a log file to view';
          container.appendChild(emptyState);
          lineCountEl.textContent = '0';
          document.getElementById('pagination').style.display = 'none';
        }
      } else {
        showToast(data.error || 'Operation failed', 'error');
      }
    } catch (e) {
      showToast('Request failed: ' + e.message, 'error');
    }
  }

  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeModal();
  });

  window.addEventListener('popstate', function() {
    var file = getFileFromURL();
    if (file && file !== activeFile) {
      activeFile = file;
      currentPage = 1;
      document.querySelectorAll('.file-item').forEach(function(el) {
        el.classList.toggle('active', el.dataset.file === file);
      });
      activeFileLabel.textContent = file;
      logPaneHeader.style.display = 'flex';
      updateActionButtons();
      showLogLoader();
      fetchLogs();
    } else if (!file && activeFile) {
      activeFile = '';
      activeFileLabel.textContent = '';
      logPaneHeader.style.display = 'none';
      updateActionButtons();
      container.innerHTML = '';
      emptyState.style.display = 'flex';
      emptyState.textContent = 'Select a log file to view';
      container.appendChild(emptyState);
      lineCountEl.textContent = '0';
      document.getElementById('pagination').style.display = 'none';
    }
  });

  fetchFiles();
  startRefresh();
</script>
</body>
</html>"""


def render_html(
    base_url: str = "",
    *,
    auto_refresh: bool = True,
    refresh_timer: int = 5000,
    auto_scroll: bool = True,
    colorize: bool = True,
    default_lines: int = 100,
) -> str:
    """Return the complete HTML page with placeholders filled in.

    Parameters
    ----------
    base_url:
        URL prefix the JS ``fetch`` calls use (e.g. ``/logs``).
    auto_refresh:
        Whether to enable auto-refresh by default.
    refresh_timer:
        Default refresh interval in ms (only used when *auto_refresh* is True).
    auto_scroll:
        Whether to auto-scroll to the bottom on refresh.
    colorize:
        Whether to show coloured log-level backgrounds.
    default_lines:
        Default line-limit option shown in the UI. Supported values:
        ``100``, ``250``, ``500``, ``1000``, ``0`` (all).
    """
    selected = str(refresh_timer) if auto_refresh else "0"
    allowed_line_limits = {"0", "100", "250", "500", "1000"}
    selected_lines = str(default_lines)
    if selected_lines not in allowed_line_limits:
        selected_lines = "100"

    html = _TEMPLATE
    for val in ("0", "1000", "3000", "5000", "10000", "30000", "60000"):
        placeholder = "{{REFRESH_%s_SELECTED}}" % val
        html = html.replace(placeholder, "selected" if selected == val else "")
    for val in ("0", "100", "250", "500", "1000"):
        placeholder = "{{LINES_%s_SELECTED}}" % val
        html = html.replace(placeholder, "selected" if selected_lines == val else "")

    html = html.replace("{{AUTO_SCROLL_CHECKED}}", "checked" if auto_scroll else "")
    html = html.replace("{{BODY_CLASS}}", "colorize" if colorize else "")
    html = html.replace("{{BASE_URL}}", base_url.rstrip("/"))

    return html
