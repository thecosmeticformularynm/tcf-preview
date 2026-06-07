/* ---------------------------------------------------------------------------
   TCF client + staff registry  (prototype / test mode)
   Any customer can sign in on the website; each one only ever sees THEIR brand.
   In production this is replaced by Shopify customer accounts + the B2B app —
   this file is the stand-in directory so the login & portal work end-to-end now.
   To add a client: copy a block, set brand/name/emails, and fill `order` when
   their first run is confirmed (empty order = portal shows an "in setup" state).
--------------------------------------------------------------------------- */
(function (w) {
  // Staff sign in to the back office. Any @thecosmeticformulary.com / @paulyinc.com also = staff.
  w.TCF_STAFF = [
    "pauly@thecosmeticformulary.com", "pauly@paulyinc.com",
    "sales@thecosmeticformulary.com", "design@thecosmeticformulary.com",
    "sanders@thecosmeticformulary.com", "office@thecosmeticformulary.com"
  ];

  w.TCF_CLIENTS = {
    dailyrou: {
      brand: "Daily Rou", name: "Meredith Baurband",
      emails: ["meredithbauerband@gmail.com", "meredith@dailyrouskin.com", "sbermaniop@gmail.com"],
      order: [
        {n:"SPF 50 — Tinted Mineral",       t:"OTC Mineral Sunscreen", size:"1.7 oz", stage:"Formula Development", progress:40, note:"In development — pending formula sign-off.", ordered:1500, fulfilled:0,   price:8.90,  due:"Jun 12, 2026", paid:0,       msrp:45},
        {n:"SPF 50 — Sheer (Untinted)",     t:"OTC Mineral Sunscreen", size:"1.7 oz", stage:"Formula Development", progress:40, note:"In development — pending formula sign-off.", ordered:1500, fulfilled:0,   price:8.90,  due:"Jun 12, 2026", paid:0,       msrp:45},
        {n:"Essential C — Vitamin C 30% THD", t:"Serum",               size:"1 oz",   stage:"In Production",       progress:75, note:"Approved. In production for restock.",     ordered:250,  fulfilled:100, price:22.15, due:"Jun 16, 2026", paid:2768.75, msrp:105},
        {n:"Hydrating Cream Cleanser",      t:"Cleanser",              size:"6 oz",   stage:"In Production",       progress:75, note:"Approved. In production for restock.",     ordered:250,  fulfilled:100, price:7.40,  due:"Jun 12, 2026", paid:925.00,  msrp:40},
        {n:"Gentle Cleansing Oil",          t:"Cleanser",              size:"4 oz",   stage:"In Production",       progress:75, note:"Approved. In production for restock.",     ordered:250,  fulfilled:100, price:9.85,  due:"Jun 12, 2026", paid:1231.25, msrp:55},
        {n:"Brightening Cleansing Gel",     t:"Cleanser",              size:"6 oz",   stage:"In Production",       progress:75, note:"Approved. In production for restock.",     ordered:250,  fulfilled:100, price:7.15,  due:"Jun 12, 2026", paid:893.75,  msrp:45}
      ]
    },
    nittbeauty: {
      brand: "Nitt Beauty", name: "Gamze Gurlevik",
      emails: ["contact@nittbeauty.com", "gamze@nittbeauty.com"],
      order: []   // portal active; order details appear once first run is confirmed
    },
    halo42: {
      brand: "Halo42", name: "Tim Quinn",
      emails: ["timquinn@halo42.com"],
      order: []
    },
    saltspa: {
      brand: "Charleston Salt Spa", name: "Andrew Moss",
      emails: ["amoss4261@gmail.com"],
      order: []
    },
    nevoo: {
      brand: "NeVoo", name: "Molly Smith",
      emails: ["charlestonheadspa@gmail.com"],
      order: []
    }
  };

  // Resolve an email -> {type:'client', id, client} | {type:'staff'} | null
  w.TCF_lookup = function (email) {
    email = (email || "").trim().toLowerCase();
    if (!email) return null;
    for (var id in w.TCF_CLIENTS) {
      var c = w.TCF_CLIENTS[id];
      for (var i = 0; i < c.emails.length; i++) {
        if (c.emails[i].toLowerCase() === email) return { type: "client", id: id, client: c };
      }
    }
    if (w.TCF_STAFF.indexOf(email) >= 0 || /@(thecosmeticformulary|paulyinc)\.com$/.test(email)) {
      return { type: "staff" };
    }
    return null;
  };
})(window);
