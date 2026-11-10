/* =========================================================
   RISE JOE — interactions & motion
   ========================================================= */
(() => {
  "use strict";
  window.__rjReady = true;
  const d = document;
  const root = d.documentElement;
  const $ = (s, c = d) => c.querySelector(s);
  const $$ = (s, c = d) => Array.from(c.querySelectorAll(s));
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  const hasGsap = !!(window.gsap && window.ScrollTrigger) && !reduce;
  const store = {
    get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* ignore */ } }
  };

  if (!hasGsap) root.classList.remove("anim");
  else gsap.registerPlugin(ScrollTrigger);

  /* ---------- Smooth scroll ---------- */
  let lenis = null;
  if (hasGsap && window.Lenis && !("ontouchstart" in window && window.innerWidth < 900)) {
    lenis = new Lenis({ lerp: 0.095, smoothWheel: true, wheelMultiplier: 1 });
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }
  const scrollToEl = (el, offset = -90) => {
    if (!el) return;
    if (lenis) lenis.scrollTo(el, { offset, duration: 1.6 });
    else window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY + offset, behavior: reduce ? "auto" : "smooth" });
  };

  /* ---------- Year ---------- */
  $$("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));

  /* ---------- Header / progress ---------- */
  const header = $(".header");
  const bar = $(".progress i");
  let lastY = window.scrollY;
  const onScroll = () => {
    const y = window.scrollY;
    if (header) {
      header.classList.toggle("is-scrolled", y > 30);
      const menuOpen = root.classList.contains("menu-open");
      if (!menuOpen) header.classList.toggle("is-hidden", y > lastY && y > 420);
    }
    if (bar) {
      const max = d.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = `scaleX(${max > 0 ? Math.min(1, y / max) : 0})`;
    }
    lastY = y;
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu ---------- */
  const burger = $(".burger");
  const setMenu = (open) => {
    root.classList.toggle("menu-open", open);
    burger && burger.setAttribute("aria-expanded", String(open));
    if (lenis) open ? lenis.stop() : lenis.start();
    d.body.classList.toggle("is-locked", open);
    if (open) header && header.classList.remove("is-hidden");
  };
  burger && burger.addEventListener("click", () => setMenu(!root.classList.contains("menu-open")));
  d.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
  $$(".menu__links a").forEach((a, i) => {
    $$("span, small", a).forEach((s) => (s.style.transitionDelay = `${0.25 + i * 0.06}s`));
  });

  /* ---------- Page transitions ---------- */
  const curtain = $(".curtain");
  const isInternal = (a) => {
    const href = a.getAttribute("href");
    if (!href || href.startsWith("#") || a.target === "_blank" || a.hasAttribute("download")) return false;
    if (/^(mailto:|tel:|https?:\/\/wa\.me|javascript:)/i.test(href)) return false;
    const url = new URL(a.href, location.href);
    if (url.origin !== location.origin) return false;
    if (url.pathname === location.pathname && url.hash) return false;
    return true;
  };
  if (curtain && hasGsap) {
    if (root.classList.contains("is-entering")) {
      gsap.fromTo(curtain, { yPercent: 0, visibility: "visible" }, { yPercent: -100, duration: 1.05, ease: "expo.inOut", delay: 0.05,
        onComplete: () => { root.classList.remove("is-entering"); gsap.set(curtain, { yPercent: 100, visibility: "hidden" }); } });
    }
    d.addEventListener("click", (e) => {
      const a = e.target.closest("a");
      if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || !isInternal(a)) return;
      e.preventDefault();
      setMenu(false);
      store.set("rj-transition", "1");
      gsap.fromTo(curtain, { yPercent: 100, visibility: "visible" }, { yPercent: 0, duration: 0.75, ease: "expo.inOut", onComplete: () => (location.href = a.href) });
    });
    window.addEventListener("pageshow", (e) => { if (e.persisted) { gsap.set(curtain, { yPercent: 100, visibility: "hidden" }); root.classList.remove("is-entering"); } });
  }

  /* ---------- In-page anchors / presets ---------- */
  d.addEventListener("click", (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const id = a.getAttribute("href");
    if (id.length < 2) return;
    const target = $(id);
    if (!target) return;
    e.preventDefault();
    setMenu(false);
    const preset = a.getAttribute("data-preset");
    if (preset) applyPreset(preset);
    scrollToEl(target);
  });
  function applyPreset(str) {
    str.split("&").forEach((pair) => {
      const [name, value] = pair.split("=");
      $$(`[name="${name}"]`).forEach((input) => {
        if (input.type === "radio" || input.type === "checkbox") input.checked = input.value === value;
        else input.value = value;
        input.dispatchEvent(new Event("change", { bubbles: true }));
      });
    });
  }

  /* ---------- Custom cursor ---------- */
  if (finePointer && !reduce) {
    const ring = d.createElement("div"); ring.className = "cursor"; ring.innerHTML = "<span></span>";
    const dot = d.createElement("div"); dot.className = "cursor-dot";
    d.body.append(ring, dot);
    const label = ring.firstChild;
    let mx = innerWidth / 2, my = innerHeight / 2, rx = mx, ry = my, shown = false;
    window.addEventListener("mousemove", (e) => {
      mx = e.clientX; my = e.clientY;
      dot.style.transform = `translate(${mx}px, ${my}px)`;
      if (!shown) { shown = true; ring.style.opacity = dot.style.opacity = 1; }
    }, { passive: true });
    d.addEventListener("mouseleave", () => { shown = false; ring.style.opacity = dot.style.opacity = 0; });
    const loop = () => {
      rx += (mx - rx) * 0.17; ry += (my - ry) * 0.17;
      ring.style.transform = `translate(${rx}px, ${ry}px)`;
      requestAnimationFrame(loop);
    };
    loop();
    d.addEventListener("mouseover", (e) => {
      const t = e.target;
      const view = t.closest("[data-cursor]");
      ring.classList.remove("is-hover", "is-view", "is-text");
      if (view) { ring.classList.add("is-view"); label.textContent = view.getAttribute("data-cursor"); return; }
      if (t.closest("input, textarea")) { ring.classList.add("is-text"); return; }
      if (t.closest("a, button, label, .chip, select, [role=button]")) ring.classList.add("is-hover");
    });
  }

  /* ---------- Magnetic ---------- */
  if (finePointer && !reduce) {
    $$("[data-magnetic]").forEach((el) => {
      const strength = parseFloat(el.getAttribute("data-magnetic")) || 0.3;
      el.addEventListener("mousemove", (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width / 2) * strength;
        const y = (e.clientY - r.top - r.height / 2) * strength;
        el.style.transform = `translate(${x}px, ${y}px)`;
      });
      el.addEventListener("mouseleave", () => { el.style.transform = ""; });
    });
  }

  /* ---------- Spotlight & tilt ---------- */
  $$(".spot").forEach((el) => {
    el.addEventListener("pointermove", (e) => {
      const r = el.getBoundingClientRect();
      el.style.setProperty("--mx", `${e.clientX - r.left}px`);
      el.style.setProperty("--my", `${e.clientY - r.top}px`);
    });
  });
  if (finePointer && !reduce) {
    $$("[data-tilt]").forEach((el) => {
      const max = parseFloat(el.getAttribute("data-tilt")) || 6;
      el.style.transformStyle = "preserve-3d";
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `perspective(1100px) rotateY(${px * max}deg) rotateX(${-py * max}deg) translateZ(0)`;
      });
      el.addEventListener("pointerleave", () => { el.style.transform = ""; });
    });
  }

  /* ---------- Statement words ---------- */
  const statements = $$("[data-fill]");
  statements.forEach((el) => {
    const walk = (node) => {
      Array.from(node.childNodes).forEach((n) => {
        if (n.nodeType === 3) {
          const frag = d.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach((part) => {
            if (!part) return;
            if (/^\s+$/.test(part)) frag.append(d.createTextNode(part));
            else { const s = d.createElement("span"); s.className = "word"; s.textContent = part; frag.append(s); }
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
  });

  /* ---------- FAQ ---------- */
  $$(".faq__item").forEach((item) => {
    const q = $(".faq__q", item), a = $(".faq__a", item);
    q.addEventListener("click", () => {
      const open = !item.classList.contains("is-open");
      $$(".faq__item.is-open", item.parentElement).forEach((o) => {
        if (o !== item) { o.classList.remove("is-open"); $(".faq__a", o).style.height = "0px"; $(".faq__q", o).setAttribute("aria-expanded", "false"); }
      });
      item.classList.toggle("is-open", open);
      q.setAttribute("aria-expanded", String(open));
      a.style.height = open ? a.scrollHeight + "px" : "0px";
      setTimeout(() => hasGsap && ScrollTrigger.refresh(), 650);
    });
  });

  /* ---------- Services filter ---------- */
  const grid = $("[data-filter-grid]");
  if (grid) {
    const cards = $$(".svc", grid);
    const chips = $$("[data-filter]");
    const search = $("[data-search]");
    const empty = $(".empty-state");
    let cat = "all";
    const apply = () => {
      const q = (search && search.value.trim().toLowerCase()) || "";
      let shown = 0;
      cards.forEach((c) => {
        const okCat = cat === "all" || (c.getAttribute("data-cat") || "").split(" ").includes(cat);
        const okQ = !q || (c.getAttribute("data-keywords") + " " + c.textContent).toLowerCase().includes(q);
        const ok = okCat && okQ;
        c.classList.toggle("is-hidden", !ok);
        if (ok) shown++;
      });
      empty && empty.classList.toggle("is-visible", shown === 0);
      if (hasGsap) {
        gsap.fromTo(cards.filter((c) => !c.classList.contains("is-hidden")), { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, stagger: 0.05, ease: "expo.out", overwrite: true });
        ScrollTrigger.refresh();
      }
    };
    chips.forEach((ch) => ch.addEventListener("click", () => {
      chips.forEach((c) => { c.classList.toggle("is-active", c === ch); c.setAttribute("aria-pressed", String(c === ch)); });
      cat = ch.getAttribute("data-filter");
      apply();
    }));
    search && search.addEventListener("input", apply);
  }

  /* ---------- Forms ---------- */
  $$("form[data-enquiry]").forEach(initForm);
  function initForm(form) {
    const ts = $('input[name="_ts"]', form);
    if (ts) ts.value = String(Date.now());
    const conditionals = $$("[data-when]", form);
    const valueOf = (name) => {
      const els = $$(`[name="${name}"]`, form);
      if (!els.length) return [];
      if (els[0].type === "radio" || els[0].type === "checkbox") return els.filter((e) => e.checked).map((e) => e.value);
      return [els[0].value];
    };
    const refresh = () => {
      conditionals.forEach((el) => {
        const [name, vals] = el.getAttribute("data-when").split(":");
        const wanted = vals.split("|");
        const show = valueOf(name).some((v) => wanted.includes(v));
        el.classList.toggle("is-shown", show);
        $$("input, select, textarea", el).forEach((i) => (i.disabled = !show));
      });
    };
    form.addEventListener("change", refresh);
    refresh();

    const fieldOf = (el) => el.closest(".field");
    const validate = () => {
      let firstBad = null;
      $$(".field", form).forEach((f) => f.classList.remove("is-invalid"));
      $$("[required]", form).forEach((el) => {
        if (el.disabled) return;
        let bad = false;
        if (el.type === "checkbox" && el.name === "consent") bad = !el.checked;
        else if (el.type === "radio") bad = !$$(`[name="${el.name}"]`, form).some((r) => r.checked);
        else if (el.type === "email") bad = !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(el.value.trim());
        else bad = !el.value.trim();
        if (bad) { const f = fieldOf(el); f && f.classList.add("is-invalid"); if (!firstBad) firstBad = el; }
      });
      // choice groups flagged as required (checkbox sets)
      $$("[data-required-group]", form).forEach((g) => {
        if (g.closest("[data-when]") && !g.closest("[data-when]").classList.contains("is-shown")) return;
        if (!$$("input:checked", g).length) { const f = fieldOf(g); f && f.classList.add("is-invalid"); if (!firstBad) firstBad = g; }
      });
      return firstBad;
    };
    form.addEventListener("input", (e) => { const f = fieldOf(e.target); f && f.classList.remove("is-invalid"); });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const status = $(".form__status", form);
      status.className = "form__status";
      const bad = validate();
      if (bad) { scrollToEl(fieldOf(bad) || bad, -140); return; }
      const btn = $('button[type="submit"]', form);
      btn.classList.add("is-loading");
      const label = $("span", btn).firstChild;
      const original = label.textContent;
      label.textContent = "Sending ";
      try {
        const res = await fetch(form.getAttribute("action"), { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.ok) throw new Error(data.message || "We couldn't send your enquiry just now.");
        const wrap = form.closest(".form-card") || form.parentElement;
        const success = $(".form-success", wrap);
        const refEl = $("[data-ref]", success);
        if (refEl && data.ref) { refEl.textContent = data.ref; refEl.parentElement.hidden = false; }
        if (hasGsap) {
          gsap.to(form, { opacity: 0, y: -20, duration: 0.5, ease: "power2.in", onComplete: () => { form.style.display = "none"; success.classList.add("is-visible"); ScrollTrigger.refresh(); } });
        } else { form.style.display = "none"; success.classList.add("is-visible"); }
        scrollToEl(wrap, -120);
      } catch (err) {
        status.className = "form__status is-error";
        status.innerHTML = `${err.message} Please try again, or reach us directly on <a href="${form.getAttribute("data-fallback") || "contact"}" style="text-decoration:underline">WhatsApp</a>.`;
      } finally {
        btn.classList.remove("is-loading");
        label.textContent = original;
      }
    });
  }
  $$("[data-form-reset]").forEach((b) => b.addEventListener("click", () => {
    const wrap = b.closest(".form-card");
    const form = $("form", wrap);
    form.reset(); form.style.display = ""; form.style.opacity = 1; form.style.transform = "";
    $(".form-success", wrap).classList.remove("is-visible");
    form.dispatchEvent(new Event("change"));
    const ts = $('input[name="_ts"]', form); if (ts) ts.value = String(Date.now());
  }));

  /* ---------- Hero constellation canvas ---------- */
  $$("canvas[data-constellation]").forEach((canvas) => {
    const ctx = canvas.getContext("2d");
    const host = canvas.parentElement;
    let w = 0, h = 0, dpr = 1, pts = [], running = true, raf = 0;
    const mouse = { x: -9999, y: -9999 };
    const density = parseFloat(canvas.getAttribute("data-constellation")) || 1;
    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = host.clientWidth; h = host.clientHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const n = Math.min(120, Math.round((w * h) / 13000 * density));
      pts = Array.from({ length: n }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.25, vy: (Math.random() - 0.5) * 0.25,
        r: Math.random() * 1.6 + 0.4, tw: Math.random() * Math.PI * 2
      }));
    };
    const LINK = 140;
    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i];
        if (!reduce) {
          p.x += p.vx; p.y += p.vy; p.tw += 0.02;
          const dx = mouse.x - p.x, dy = mouse.y - p.y, dist = Math.hypot(dx, dy);
          if (dist < 200) { p.x -= dx * 0.004; p.y -= dy * 0.004; }
          if (p.x < -20) p.x = w + 20; if (p.x > w + 20) p.x = -20;
          if (p.y < -20) p.y = h + 20; if (p.y > h + 20) p.y = -20;
        }
        for (let j = i + 1; j < pts.length; j++) {
          const q = pts[j];
          const dx = p.x - q.x, dy = p.y - q.y, dd = dx * dx + dy * dy;
          if (dd < LINK * LINK) {
            const a = (1 - Math.sqrt(dd) / LINK) * 0.22;
            ctx.strokeStyle = `rgba(214,168,76,${a})`; ctx.lineWidth = 0.6;
            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke();
          }
        }
        const md = Math.hypot(mouse.x - p.x, mouse.y - p.y);
        if (md < 180) {
          ctx.strokeStyle = `rgba(245,220,154,${(1 - md / 180) * 0.45})`; ctx.lineWidth = 0.7;
          ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(mouse.x, mouse.y); ctx.stroke();
        }
        const glow = 0.55 + Math.sin(p.tw) * 0.35;
        ctx.fillStyle = `rgba(245,220,154,${glow})`;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fill();
      }
      if (running && !reduce) raf = requestAnimationFrame(draw);
    };
    host.addEventListener("pointermove", (e) => { const r = canvas.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top; });
    host.addEventListener("pointerleave", () => { mouse.x = mouse.y = -9999; });
    let rt; window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { resize(); if (reduce) draw(); }, 150); });
    resize(); draw();
    new IntersectionObserver(([en]) => {
      const vis = en.isIntersecting;
      if (vis && !running) { running = true; cancelAnimationFrame(raf); draw(); }
      else if (!vis) running = false;
    }).observe(host);
  });

  /* ---------- Hero glow follows pointer ---------- */
  const glow = $(".hero__glow");
  if (glow && finePointer && !reduce) {
    const host = glow.parentElement;
    let gx = 0, gy = 0, tx = 0, ty = 0;
    host.addEventListener("pointermove", (e) => {
      const r = host.getBoundingClientRect();
      tx = (e.clientX - r.left - r.width / 2) * 0.35; ty = (e.clientY - r.top - r.height * 0.4) * 0.35;
    });
    (function loop() { gx += (tx - gx) * 0.05; gy += (ty - gy) * 0.05; glow.style.transform = `translate(calc(-50% + ${gx}px), calc(-50% + ${gy}px))`; requestAnimationFrame(loop); })();
  }

  /* ---------- Motion (GSAP) ---------- */
  if (!hasGsap) {
    $$(".step").forEach((s) => s.classList.add("is-active"));
    $$(".statement .word").forEach((w) => w.classList.add("is-lit"));
    return;
  }

  const intro = () => {
    const hero = $(".hero, .page-hero");
    const tl = gsap.timeline({ defaults: { ease: "expo.out" } });
    if (hero) {
      tl.to($$("[data-split] .line-inner", hero), { y: 0, duration: 1.5, stagger: 0.11 }, 0.1)
        .to($$("[data-hero]", hero), { opacity: 1, y: 0, duration: 1.3, stagger: 0.09 }, 0.45);
      const mark = $(".hero__mark", hero);
      if (mark) tl.from(mark, { opacity: 0, scale: 0.85, rotate: -8, duration: 2.4 }, 0);
    }
    return tl;
  };

  const preloader = $(".preloader");
  if (preloader && !root.classList.contains("no-preload")) {
    store.set("rj-loaded", "1");
    const count = $(".preloader__count", preloader);
    const n = { v: 0 };
    const tl = gsap.timeline();
    tl.to($(".preloader__mark", preloader), { opacity: 1, scale: 1, duration: 1, ease: "expo.out" })
      .to($(".preloader__bar i", preloader), { scaleX: 1, duration: 1.4, ease: "power2.inOut" }, 0.1)
      .to(n, { v: 100, duration: 1.4, ease: "power2.inOut", onUpdate: () => (count.textContent = String(Math.round(n.v)).padStart(3, "0")) }, 0.1)
      .to($(".preloader__inner", preloader), { opacity: 0, y: -20, duration: 0.5, ease: "power2.in" }, "+=0.15")
      .set(preloader, { backgroundColor: "transparent" })
      .to($(".preloader__panel--top", preloader), { yPercent: -100, duration: 1.1, ease: "expo.inOut" }, "-=0.05")
      .to($(".preloader__panel--bot", preloader), { yPercent: 100, duration: 1.1, ease: "expo.inOut" }, "<")
      .add(() => { intro(); }, "-=0.75")
      .set(preloader, { display: "none" });
  } else {
    preloader && (preloader.style.display = "none");
    intro().delay(root.classList.contains("is-entering") ? 0.45 : 0.05);
  }

  // Reveal
  $$("[data-reveal]").forEach((el) => {
    gsap.to(el, { opacity: 1, x: 0, y: 0, scale: 1, duration: 1.4, ease: "expo.out", delay: parseFloat(el.getAttribute("data-delay")) || 0,
      scrollTrigger: { trigger: el, start: "top 88%", once: true } });
  });
  $$("[data-stagger]").forEach((el) => {
    gsap.to(el.children, { opacity: 1, y: 0, duration: 1.2, ease: "expo.out", stagger: parseFloat(el.getAttribute("data-stagger")) || 0.08,
      scrollTrigger: { trigger: el, start: "top 85%", once: true } });
  });
  $$("[data-split]").forEach((el) => {
    if (el.closest(".hero, .page-hero")) return;
    gsap.to($$(".line-inner", el), { y: 0, duration: 1.4, ease: "expo.out", stagger: 0.1, scrollTrigger: { trigger: el, start: "top 88%", once: true } });
  });

  // Counters
  $$("[data-count]").forEach((el) => {
    const end = parseFloat(el.getAttribute("data-count"));
    const o = { v: 0 };
    el.textContent = "0";
    gsap.to(o, { v: end, duration: 2.2, ease: "power3.out", scrollTrigger: { trigger: el, start: "top bottom", once: true }, delay: el.closest(".hero, .page-hero") ? 1.2 : 0,
      onUpdate: () => (el.textContent = Math.round(o.v)) });
  });

  // Statement fill
  statements.forEach((el) => {
    const words = $$(".word", el);
    ScrollTrigger.create({ trigger: el, start: "top 80%", end: "bottom 45%", scrub: true,
      onUpdate: (self) => { const lit = Math.round(self.progress * words.length); words.forEach((w, i) => w.classList.toggle("is-lit", i < lit)); } });
  });

  // Parallax
  $$("[data-speed]").forEach((el) => {
    const s = parseFloat(el.getAttribute("data-speed"));
    gsap.to(el, { yPercent: s * -30, ease: "none", scrollTrigger: { trigger: el.parentElement, start: "top bottom", end: "bottom top", scrub: true } });
  });
  $$("[data-parallax-img]").forEach((img) => {
    gsap.fromTo(img, { yPercent: -8 }, { yPercent: 6, ease: "none", scrollTrigger: { trigger: img.parentElement, start: "top bottom", end: "bottom top", scrub: true } });
  });
  const mark = $(".hero__mark");
  if (mark) gsap.to(mark, { yPercent: 25, rotate: 10, ease: "none", scrollTrigger: { trigger: mark.parentElement, start: "top top", end: "bottom top", scrub: true } });

  // Horizontal journey
  $$(".hscroll").forEach((sec) => {
    const track = $(".hscroll__track", sec);
    const line = $(".hscroll__line i", sec);
    const dist = () => Math.max(0, track.scrollWidth - window.innerWidth);
    const tl = gsap.timeline({ scrollTrigger: { trigger: sec, pin: $(".hscroll__pin", sec), start: "top top", end: () => "+=" + (dist() + window.innerHeight * 0.3), scrub: 0.8, invalidateOnRefresh: true, anticipatePin: 1 } });
    tl.to(track, { x: () => -dist(), ease: "none" }, 0);
    if (line) tl.to(line, { scaleX: 1, ease: "none" }, 0);
    $$(".journey-card", track).forEach((c, i) => gsap.from(c, { opacity: 0.25, scale: 0.92, duration: 1, scrollTrigger: { trigger: c, containerAnimation: tl.getChildren()[0], start: "left 90%", end: "left 55%", scrub: true } }));
  });

  // Steps
  $$(".steps").forEach((s) => {
    const line = $(".steps__line i", s);
    if (line) gsap.to(line, { scaleY: 1, ease: "none", scrollTrigger: { trigger: s, start: "top 65%", end: "bottom 65%", scrub: true } });
    $$(".step", s).forEach((st) => ScrollTrigger.create({ trigger: st, start: "top 66%", end: "bottom 66%", onToggle: (self) => self.isActive && st.classList.add("is-active"), onLeaveBack: () => st.classList.remove("is-active") }));
  });

  // Big outlined marquee drifts with scroll
  $$(".marquee--big").forEach((m) => {
    gsap.fromTo($(".marquee__drift", m) || m, { xPercent: m.classList.contains("marquee--reverse") ? -6 : 6 }, { xPercent: m.classList.contains("marquee--reverse") ? 6 : -6, ease: "none",
      scrollTrigger: { trigger: m, start: "top bottom", end: "bottom top", scrub: true } });
  });

  window.addEventListener("load", () => ScrollTrigger.refresh());
})();
