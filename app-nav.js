/* Formulary OS — shared nav bar, session/login state, and assistant.
   Drop <script src="app-nav.js"></script> before </body> on any page. */
(function () {
  var SKEY = 'fos_session';
  function getSession(){ try { return JSON.parse(localStorage.getItem(SKEY)) || null; } catch(e){ return null; } }
  var here = (location.pathname.split('/').pop() || 'start.html').toLowerCase();
  var sess = getSession();

  // ---- access ----
  // OPEN_MODE: no password/login required while we're building. Sign in / Log out
  // and the help assistant still WORK and are fully demonstrable — they just aren't
  // enforced. Flip to false when the system is ready to require real logins.
  var OPEN_MODE = true;
  var PROTECTED = ['admin.html', 'portal.html', 'client-order.html', 'inventory.html', 'settings.html'];
  if (!OPEN_MODE && PROTECTED.indexOf(here) >= 0 && !sess) { location.replace('login.html'); return; }
  // Only when actually signed in as a client, keep them in their own area (role demo).
  if (sess && sess.role === 'Client' && ['admin.html','inventory.html','settings.html','start.html'].indexOf(here) >= 0) { location.replace('client-order.html'); return; }

  var PAGES = [
    { f: 'start.html',     label: 'Home',          ic: '⌂' },
    { f: 'index.html',     label: 'Storefront',    ic: '🏛' },
    { f: 'portal.html',    label: 'Client Portal', ic: '🔐' },
    { f: 'admin.html',     label: 'Back Office',   ic: '⚙' },
    { f: 'inventory.html', label: 'Inventory',     ic: '📦' },
    { f: 'settings.html',  label: 'Settings',      ic: '⚙' }
  ];
  var CLIENT_PAGES = [
    { f: 'client-order.html', label: 'My Orders',          ic: '📋' },
    { f: 'portal.html',       label: 'Reorder & Messages', ic: '🔐' },
    { f: 'index.html',        label: 'Storefront',         ic: '🏛' }
  ];
  var pageset = (sess && sess.role === 'Client') ? CLIENT_PAGES : PAGES;
  var links = pageset.map(function (p) {
    var on = p.f.toLowerCase() === here ? ' on' : '';
    return '<a class="fosnav-link' + on + '" href="' + p.f + '"><span class="fi">' + p.ic + '</span><span class="fl">' + p.label + '</span></a>';
  }).join('');

  var right;
  if (sess) {
    var sub = sess.role + (sess.brand ? ' · ' + sess.brand : '');
    right = '<span class="fosnav-user" title="' + sub + '"><span class="dot"></span>' + sess.name +
            ' <em>' + sub + '</em></span><a class="fosnav-out" href="#" id="fosLogout">Log out</a>';
  } else {
    right = '<a class="fosnav-out signin" href="login.html">Sign in →</a>';
  }

  var bar = document.createElement('div');
  bar.className = 'fosnav';
  bar.innerHTML =
    '<div class="fosnav-in">' +
      '<a class="fosnav-brand" href="start.html"><span class="fosnav-mark">CF</span> Formulary OS</a>' +
      '<nav class="fosnav-links">' + links + '</nav>' +
      '<div class="fosnav-right">' + right + '</div>' +
    '</div>';

  var css =
  '.fosnav{background:#1d1c1a;color:#f4efe6;font-family:Inter,system-ui,sans-serif;border-bottom:1px solid #000;position:relative;z-index:9000}' +
  '.fosnav-in{max-width:1340px;margin:0 auto;display:flex;align-items:center;gap:14px;padding:8px 16px;flex-wrap:wrap}' +
  '.fosnav-brand{display:flex;align-items:center;gap:8px;color:#f4efe6;text-decoration:none;font-family:Fraunces,Georgia,serif;font-size:.98rem;white-space:nowrap}' +
  '.fosnav-mark{width:24px;height:24px;border:1.4px solid #a98a5c;color:#a98a5c;border-radius:50%;display:grid;place-items:center;font-family:Inter,sans-serif;font-size:.6rem;font-weight:700}' +
  '.fosnav-links{display:flex;gap:4px;flex-wrap:wrap;margin-left:4px}' +
  '.fosnav-link{display:flex;align-items:center;gap:6px;color:#cfc9bf;text-decoration:none;font-size:.82rem;font-weight:500;padding:6px 12px;border-radius:100px;transition:background .15s,color .15s}' +
  '.fosnav-link:hover{background:#2c2a24;color:#fff}.fosnav-link.on{background:#3a4b3f;color:#fff}.fosnav-link .fi{font-size:.92rem;line-height:1}' +
  '.fosnav-right{margin-left:auto;display:flex;align-items:center;gap:10px}' +
  '.fosnav-user{display:flex;align-items:center;gap:7px;font-size:.8rem;color:#e8e4da;white-space:nowrap}' +
  '.fosnav-user .dot{width:7px;height:7px;border-radius:50%;background:#4caf7d;flex:none}' +
  '.fosnav-user em{font-style:normal;color:#9c958a;font-size:.74rem}' +
  '.fosnav-out{color:#cfc9bf;text-decoration:none;font-size:.8rem;font-weight:600;border:1px solid #3a382f;padding:5px 12px;border-radius:100px}' +
  '.fosnav-out:hover{background:#2c2a24;color:#fff}.fosnav-out.signin{background:#3a4b3f;color:#fff;border-color:#3a4b3f}' +
  '@media(max-width:900px){.fosnav-user em{display:none}}' +
  '@media(max-width:780px){.fosnav-link .fl{display:none}.fosnav-link{padding:7px 9px}.fosnav-user{display:none}}' +
  '.fos-toast{position:fixed;bottom:26px;left:50%;transform:translateX(-50%) translateY(18px);background:#1d1c1a;color:#fff;padding:11px 18px;border-radius:100px;font-family:Inter,sans-serif;font-size:.85rem;z-index:100000;opacity:0;transition:.3s;box-shadow:0 12px 34px rgba(0,0,0,.32)}.fos-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}' +
  /* assistant */
  '.fosai-b{position:fixed;bottom:22px;right:22px;background:#1d1c1a;color:#f4efe6;padding:.8em 1.3em;border-radius:100px;font-family:Inter,sans-serif;font-weight:600;font-size:.86rem;cursor:pointer;box-shadow:0 10px 30px rgba(0,0,0,.3);z-index:9500;border:1px solid #3a382f}' +
  '.fosai-p{position:fixed;bottom:22px;right:22px;width:360px;max-width:calc(100vw - 28px);height:480px;max-height:calc(100vh - 40px);background:#fffdfa;color:#1d1c1a;border:1px solid #e2dacd;border-radius:18px;box-shadow:0 22px 60px rgba(0,0,0,.3);display:none;flex-direction:column;overflow:hidden;z-index:9600;font-family:Inter,sans-serif}' +
  '.fosai-p.open{display:flex}.fosai-b.hide{display:none}' +
  '.fosai-h{background:#3a4b3f;color:#fff;padding:13px 15px;display:flex;justify-content:space-between;align-items:center}' +
  '.fosai-h b{font-family:Fraunces,serif;font-weight:500;font-size:1.05rem}.fosai-h b small{display:block;font-family:Inter;font-size:.64rem;opacity:.8;letter-spacing:.04em}' +
  '.fosai-h .x{cursor:pointer;opacity:.85}' +
  '.fosai-log{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:9px;background:#f4efe6}' +
  '.fosai-msg{max-width:84%;padding:9px 12px;border-radius:13px;font-size:.85rem;line-height:1.4}' +
  '.fosai-msg.them{background:#ece5d9;align-self:flex-start;border-bottom-left-radius:4px}' +
  '.fosai-msg.you{background:#3a4b3f;color:#fff;align-self:flex-end;border-bottom-right-radius:4px}' +
  '.fosai-bar{display:flex;gap:8px;padding:11px;border-top:1px solid #e2dacd;background:#fffdfa}' +
  '.fosai-bar input{flex:1;border:1px solid #e2dacd;border-radius:100px;padding:.6em .9em;font-family:inherit;font-size:.85rem;background:#f4efe6}' +
  '.fosai-bar button{background:#3a4b3f;color:#fff;border:none;border-radius:50%;width:36px;height:36px;cursor:pointer;font-size:1.05rem;flex:none}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  function mount() {
    if (!document.body) { document.addEventListener('DOMContentLoaded', mount); return; }
    document.body.insertBefore(bar, document.body.firstChild);
    var lo = document.getElementById('fosLogout');
    if (lo) lo.onclick = function (e) { e.preventDefault(); localStorage.removeItem(SKEY); location.href = 'login.html'; };
    if (!document.getElementById('aibubble') && !document.getElementById('fosaiB')) mountAssistant();
  }
  mount();

  window.fosToast = function (msg) {
    var t = document.createElement('div'); t.className = 'fos-toast'; t.textContent = msg; document.body.appendChild(t);
    setTimeout(function(){t.classList.add('show');},10);
    setTimeout(function(){t.classList.remove('show');setTimeout(function(){t.remove();},320);},2300);
  };

  // ---------- built-in assistant (only if the page has none) ----------
  function mountAssistant(){
    var b = document.createElement('div'); b.className='fosai-b'; b.id='fosaiB'; b.innerHTML='✦ Ask Formulary OS';
    var p = document.createElement('div'); p.className='fosai-p'; p.id='fosaiP';
    p.innerHTML =
      '<div class="fosai-h"><b>Formulary OS Assistant<small>'+(sess?('Signed in · '+sess.role):'How can I help?')+'</small></b><span class="x">✕</span></div>'+
      '<div class="fosai-log" id="fosaiLog"><div class="fosai-msg them">Hi'+(sess?(' '+sess.name.split(" ")[0]):'')+' — ask me how to find inventory, reorder, log out, or run any part of the system.</div></div>'+
      '<div class="fosai-bar"><input id="fosaiIn" placeholder="Ask anything…" /><button id="fosaiSend">→</button></div>';
    document.body.appendChild(b); document.body.appendChild(p);
    function toggle(o){ p.classList.toggle('open',o); b.classList.toggle('hide',o); }
    b.onclick=function(){toggle(true);}; p.querySelector('.x').onclick=function(){toggle(false);};
    var KB=[
      {k:['inventory','stock','lot','where is','on hand'],a:"Open <b>Inventory</b> from the top bar — 199 live lots from inFlow. Search any name or lot number, and use − / + to adjust counts."},
      {k:['reorder','order more','buy','restock'],a:"In the <b>Client Portal</b>, the Reorder tab lists your products at your wholesale pricing — set quantities and place the order."},
      {k:['purchase order','po','supplier order','vendor order'],a:"<b>Back Office → Purchase Orders</b>. Receiving a PO auto-creates the lot in Inventory."},
      {k:['batch','manufacturing','production','make'],a:"<b>Back Office → Manufacturing</b> runs batches — it pulls the formula, deducts raw materials, and stamps the finished-good lot."},
      {k:['settings','company','units','roles','reorder point'],a:"Open <b>Settings</b> from the top bar to adjust company info, locations, units, inventory rules, team roles, and integrations."},
      {k:['log out','logout','sign out','switch user'],a:"Use <b>Log out</b> at the top-right, then sign back in as anyone from the login screen."},
      {k:['meredith','daily rou','client','brand portal'],a:"Sign in as <b>Meredith Baurband</b> on the login page to enter the <b>Daily Rou</b> client portal — her products, reorders, invoices, and projects."},
      {k:['invoice','pay','wire','affirm','payment'],a:"Invoices live in the portal under <b>Invoices</b>; pay by wire (no fee) or Affirm. Staff confirm wires in Back Office → Orders."},
      {k:['quickbooks','accounting','tax'],a:"Accounting stays in <b>QuickBooks</b> — Formulary OS reports against it but never replaces it."},
      {k:['help','what can you','hi','hello','start'],a:"I help you run Formulary OS. Try: <i>inventory</i>, <i>purchase orders</i>, <i>reorder</i>, <i>settings</i>, or <i>log out</i>."}
    ];
    function answer(q){ q=(q||'').toLowerCase(); for(var i=0;i<KB.length;i++){for(var j=0;j<KB[i].k.length;j++){if(q.indexOf(KB[i].k[j])>=0)return KB[i].a;}} return "I can point you anywhere in Formulary OS — try <i>inventory</i>, <i>reorder</i>, <i>purchase orders</i>, <i>settings</i>, or <i>log out</i>."; }
    var log=p.querySelector('#fosaiLog'), inp=p.querySelector('#fosaiIn');
    function add(t,c){ var d=document.createElement('div'); d.className='fosai-msg '+c; d.innerHTML=t; log.appendChild(d); log.scrollTop=log.scrollHeight; }
    function send(){ var v=inp.value.trim(); if(!v)return; add(v,'you'); inp.value=''; setTimeout(function(){add(answer(v),'them');},250); }
    p.querySelector('#fosaiSend').onclick=send;
    inp.addEventListener('keydown',function(e){ if(e.key==='Enter')send(); });
  }
})();
