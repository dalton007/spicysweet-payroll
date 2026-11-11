// Spicy Sweet Payroll — desktop shell.
// Opens the hosted app in its own window, with native dialogs for every file it saves.
const { app, BrowserWindow, shell, Menu, dialog } = require("electron");
const path = require("path");
const fs = require("fs");

const APP_URL = "https://dalton007.github.io/spicysweet-payroll/";
const HOME_HOSTS = ["dalton007.github.io", "ctsbigebqkyggntjevqq.supabase.co"];

app.setName("Spicy Sweet Payroll");
if (process.platform === "win32") app.setAppUserModelId("com.spicysweet.payroll");

const statePath = () => path.join(app.getPath("userData"), "window.json");
let win = null;

function createWindow() {
  let st = {};
  try { st = JSON.parse(fs.readFileSync(statePath(), "utf8")); } catch (err) {}
  win = new BrowserWindow({
    width: st.width || 1440,
    height: st.height || 900,
    x: st.x,
    y: st.y,
    minWidth: 820,
    minHeight: 600,
    title: "Spicy Sweet Payroll",
    icon: path.join(__dirname, "icon.png"),
    backgroundColor: "#FFF7FB",
    autoHideMenuBar: true,
    show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true, spellcheck: false },
  });
  // a plain Chrome user agent so sign-in pages treat this like a normal browser
  const ua = win.webContents.getUserAgent().replace(/ ?Electron\/[\d.]+/, "").replace(/ ?spicy-sweet-payroll\/[\d.]+/, "");
  win.webContents.setUserAgent(ua);

  win.on("page-title-updated", (e) => e.preventDefault()); // keep our name, not the page's
  win.once("ready-to-show", () => win.show());
  // always fetch a fresh page — GitHub Pages caches index.html for ten minutes
  const fresh = () => APP_URL + "?v=" + Date.now();
  win.webContents.session.clearCache().finally(() => win.loadURL(fresh()));

  const saveBounds = () => { try { fs.writeFileSync(statePath(), JSON.stringify(win.getBounds())); } catch (err) {} };
  win.on("resize", saveBounds);
  win.on("move", saveBounds);
  win.on("closed", () => { win = null; });

  // links that leave claude.ai open in the system browser
  win.webContents.setWindowOpenHandler(({ url }) => {
    try {
      const u = new URL(url);
      if (!HOME_HOSTS.includes(u.hostname)) { shell.openExternal(url); return { action: "deny" }; }
    } catch (err) {}
    return { action: "allow" };
  });
  win.webContents.on("will-navigate", (e, url) => {
    try {
      const u = new URL(url);
      if (!HOME_HOSTS.includes(u.hostname)) {
        e.preventDefault();
        shell.openExternal(url);
      }
    } catch (err) {}
  });
  win.webContents.on("did-fail-load", (e, code, desc) => {
    if (code === -3) return; // aborted (navigation replaced)
    dialog.showMessageBox(win, {
      type: "warning",
      title: "Can't reach the app",
      message: "Spicy Sweet Payroll needs an internet connection.",
      detail: `The app couldn't load (${desc}). Check your connection, then choose Reload from the View menu or press Ctrl/Cmd+R.`,
    });
  });
}

const isMac = process.platform === "darwin";
const menu = Menu.buildFromTemplate([
  ...(isMac ? [{ label: "Spicy Sweet Payroll", submenu: [{ role: "about" }, { type: "separator" }, { role: "hide" }, { role: "hideOthers" }, { type: "separator" }, { role: "quit" }] }] : []),
  { label: "Edit", submenu: [{ role: "undo" }, { role: "redo" }, { type: "separator" }, { role: "cut" }, { role: "copy" }, { role: "paste" }, { role: "selectAll" }] },
  {
    label: "View",
    submenu: [
      { label: "Back to Payroll", accelerator: "CmdOrCtrl+Shift+H", click: () => win && win.loadURL(APP_URL + "?v=" + Date.now()) },
      { label: "Reload (fresh copy)", accelerator: "CmdOrCtrl+R", click: () => win && win.webContents.session.clearCache().finally(() => win.loadURL(APP_URL + "?v=" + Date.now())) },
      { type: "separator" },
      { role: "resetZoom" }, { role: "zoomIn" }, { role: "zoomOut" },
      { type: "separator" },
      { role: "togglefullscreen" },
    ],
  },
  { label: "Window", submenu: [{ role: "minimize" }, { role: "close" }] },
  {
    label: "Help",
    submenu: [
      { label: "Open in your browser instead", click: () => shell.openExternal(APP_URL) },
      { label: "Clear sign-in and app data on this computer…", click: async () => {
          if (!win) return;
          const r = await dialog.showMessageBox(win, { type: "question", buttons: ["Cancel", "Clear"], defaultId: 0, cancelId: 0, title: "Clear local data", message: "Sign out and clear this computer's copy of the app data?", detail: "Your data stays in your Spicy Sweet account and comes back when you sign in again." });
          if (r.response === 1) { await win.webContents.session.clearStorageData(); win.loadURL(APP_URL + "?v=" + Date.now()); }
        } },
    ],
  },
]);
Menu.setApplicationMenu(menu);

app.whenReady().then(() => {
  createWindow();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on("window-all-closed", () => { if (!isMac) app.quit(); });
