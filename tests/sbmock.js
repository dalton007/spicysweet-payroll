// In-browser stand-in for supabase-js v2, enough for the app's call shapes.
(function(){
  const db = { app_state: {}, weeks: {}, profiles: {}, config: { main: { owner_email: "owner@test.com" } } };
  const users = {}; // email -> {id,password,name}
  let session = null; const authCbs = []; const channels = [];
  const uid = () => "u" + Math.random().toString(36).slice(2, 10);
  const ok = (data) => Promise.resolve({ data, error: null });
  const fail = (m) => Promise.resolve({ data: null, error: { message: m } });
  const fire = (table, evt, row, old) => channels.forEach(ch => ch.handlers.forEach(h => { if (h.cfg.table === table) { try { h.fn({ eventType: evt, new: row, old }); } catch (e) { console.error(e); } } }));
  const me = () => session && db.profiles[session.user.id];
  const role = () => (me() && me().role) || "anon";
  window.__sb = { db, users, setRole: (email, r, team, cn) => { const u = Object.values(users).find(x => x.email === email); db.profiles[u.id] = { ...db.profiles[u.id], role: r, team: team || null, chatter_name: cn || null }; fire("profiles", "UPDATE", db.profiles[u.id]); },
    externalState: (data) => { db.app_state.main = { id: "main", data, updated_at: Date.now() + 5000, device: "other", device_label: "iPhone" }; fire("app_state", "UPDATE", db.app_state.main); },
    log: [] };
  const slice = () => {
    const p = me(); const st = db.app_state.main && db.app_state.main.data; if (!st) return { role: p.role, empty: true };
    const emps = st.employees || []; const name = (p.chatter_name || p.display_name || "").trim().toLowerCase();
    const mine = p.role === "chatter" ? emps.filter(e => (e.name || "").trim().toLowerCase() === name) : emps.filter(e => e.team === p.team);
    const board = emps.map(e => ({ name: e.name, team: e.team, headChatter: e.headChatter, shifts: (e.shifts || []).map(s => ({ date: s.date, hours: s.hours, revenue: s.revenue, fansly: s.fansly, ppvSent: s.ppvSent, msgsSent: s.msgsSent, respMin: s.respMin, creators: s.creators })) }));
    const settings = { ...st.settings }; delete settings.invoices; delete settings.otherExpenses;
    const weeks = Object.values(db.weeks).map(w => ({ payPeriod: w.data.payPeriod, weekStart: w.week_start, savedDate: w.data.savedDate, chatters: Object.fromEntries(Object.entries(w.data.chatters || {}).filter(([k, c]) => p.role === "chatter" ? (c.name || "").trim().toLowerCase() === name : c.team === p.team)) }));
    return { role: p.role, team: p.team, chatterName: p.chatter_name || p.display_name, employees: mine, settings, roster: st.roster || [], board, weeks, updatedAt: db.app_state.main.updated_at };
  };
  function query(table) {
    const q = { _f: [], _op: "select" };
    const run = () => {
      let rows = Object.values(db[table] || {});
      if (table === "profiles" && !["owner", "coowner"].includes(role())) rows = rows.filter(r => r.id === (session && session.user.id));
      if (["app_state", "weeks"].includes(table) && !["owner", "coowner", "manager"].includes(role())) rows = [];
      q._f.forEach(([k, v]) => { rows = rows.filter(r => String(r[k]) === String(v)); });
      return rows;
    };
    q.select = () => q; q.order = () => q;
    q.eq = (k, v) => { q._f.push([k, v]); return q; };
    q.maybeSingle = () => ok(run()[0] || null);
    q.upsert = (obj) => { if (!["owner", "coowner", "manager"].includes(role())) return fail("permission denied"); const key = table === "weeks" ? obj.week_start : obj.id; if (table === "app_state" && role() === "manager" && db.app_state.main) { const o = db.app_state.main.data.settings || {}, n = obj.data.settings || {}; const allowed = ["payPeriod","invoices","otherExpenses","teamGoalAmounts","modelGoalAmounts","autoAwards","announcementTemplate","managerName","timeZone"]; for (const k of new Set([...Object.keys(o), ...Object.keys(n)])) if (!allowed.includes(k) && JSON.stringify(o[k]) !== JSON.stringify(n[k])) return fail("Managers cannot change pay rules (" + k + "). Ask an owner."); } const exists = !!db[table][key]; db[table][key] = { ...obj }; window.__sb.log.push("upsert " + table + "/" + key); fire(table, exists ? "UPDATE" : "INSERT", db[table][key]); return ok(null); };
    q.delete = () => { q._op = "delete"; return { eq: (k, v) => { const rows = Object.values(db[table]).filter(r => String(r[k]) === String(v)); rows.forEach(r => { delete db[table][table === "weeks" ? r.week_start : r.id]; fire(table, "DELETE", null, r); }); return ok(null); } }; };
    q.then = (res, rej) => ok(run()).then(res, rej);
    return q;
  }
  const client = {
    auth: {
      getSession: () => ok({ session }),
      onAuthStateChange: (cb) => { authCbs.push(cb); return { data: { subscription: { unsubscribe() {} } } }; },
      signInWithPassword: ({ email, password }) => { const u = users[email]; if (!u || u.password !== password) return fail("Invalid login credentials"); session = { user: { id: u.id, email } }; authCbs.forEach(cb => cb("SIGNED_IN", session)); return ok({ session }); },
      signUp: ({ email, password, options }) => { if (users[email]) return fail("User already registered"); const id = uid(); users[email] = { id, email, password, name: options.data.display_name }; const owner = db.config.main.owner_email; db.profiles[id] = { id, email, display_name: options.data.display_name, role: email === owner ? "owner" : "pending", team: null, chatter_name: null, created_at: new Date().toISOString() }; return ok({ session: null, user: { id } }); },
      signOut: () => { session = null; authCbs.forEach(cb => cb("SIGNED_OUT", null)); return ok(null); },
      resetPasswordForEmail: () => ok(null), updateUser: () => ok(null),
    },
    from: (t) => query(t),
    rpc: (name, args) => {
      if (!session) return fail("not signed in");
      if (name === "my_profile") return ok(me() || null);
      if (name === "my_role") return ok(role());
      if (name === "my_slice") return ok(slice());
      if (name === "set_role") { if (role() !== "owner") return fail("Only the owner can change roles."); db.profiles[args.p_user] = { ...db.profiles[args.p_user], role: args.p_role, team: args.p_team, chatter_name: args.p_chatter_name }; fire("profiles", "UPDATE", db.profiles[args.p_user]); return ok(null); }
      return fail("unknown rpc " + name);
    },
    channel: (name) => { const ch = { name, handlers: [], on(_e, cfg, fn) { ch.handlers.push({ cfg, fn }); return ch; }, subscribe() { channels.push(ch); return ch; } }; return ch; },
    removeChannel: (ch) => { const i = channels.indexOf(ch); if (i >= 0) channels.splice(i, 1); },
  };
  window.supabase = { createClient: () => client };
  window.claude = undefined;
})();
