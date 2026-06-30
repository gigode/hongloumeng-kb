(async function () {
  const svg = document.getElementById("graph-svg");
  if (!svg) return;
  const details = document.getElementById("graph-details");
  const search = document.getElementById("graph-search");
  const filter = document.getElementById("graph-filter");
  const graph = await fetch("graph.json").then(r => r.json());
  const width = () => svg.clientWidth || 900;
  const height = () => svg.clientHeight || 700;
  const colors = {
    person: "#8b1e2d",
    place: "#315f8c",
    household: "#256c5b",
    object: "#1f7a8c",
    concept: "#b13b5d",
    role: "#a56b16",
    text: "#6b4c8f",
    event: "#231f1b"
  };
  const types = Array.from(new Set(graph.edges.map(e => e.type))).sort();
  for (const type of types) {
    const option = document.createElement("option");
    option.value = type;
    option.textContent = type;
    filter.appendChild(option);
  }
  const nodes = graph.nodes.map((node, i) => ({
    ...node,
    x: width() / 2 + Math.cos(i * 2.399) * Math.min(width(), height()) * (0.08 + (i % 9) * 0.025),
    y: height() / 2 + Math.sin(i * 2.399) * Math.min(width(), height()) * (0.08 + (i % 9) * 0.025),
    vx: 0,
    vy: 0
  }));
  const byId = new Map(nodes.map(n => [n.id, n]));
  const edges = graph.edges.filter(e => byId.has(e.source) && byId.has(e.target));
  function tick() {
    const cx = width() / 2;
    const cy = height() / 2;
    for (const n of nodes) {
      n.vx += (cx - n.x) * 0.003;
      n.vy += (cy - n.y) * 0.003;
    }
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        let dx = a.x - b.x, dy = a.y - b.y;
        let d2 = dx * dx + dy * dy || 1;
        const force = Math.min(210 / d2, 0.025);
        a.vx += dx * force; a.vy += dy * force;
        b.vx -= dx * force; b.vy -= dy * force;
      }
    }
    for (const e of edges) {
      const a = byId.get(e.source), b = byId.get(e.target);
      const dx = b.x - a.x, dy = b.y - a.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const target = e.type.includes("event") ? 120 : 96;
      const force = (dist - target) * 0.0032;
      a.vx += dx / dist * force; a.vy += dy / dist * force;
      b.vx -= dx / dist * force; b.vy -= dy / dist * force;
    }
    for (const n of nodes) {
      n.vx *= 0.68; n.vy *= 0.68;
      n.x = Math.max(46, Math.min(width() - 96, n.x + n.vx));
      n.y = Math.max(34, Math.min(height() - 48, n.y + n.vy));
    }
  }
  function render() {
    svg.setAttribute("viewBox", `0 0 ${width()} ${height()}`);
    svg.innerHTML = "";
    const term = (search.value || "").trim();
    const rel = filter.value;
    const activeNodeIds = new Set();
    for (const e of edges) {
      if (rel && e.type !== rel) continue;
      activeNodeIds.add(e.source); activeNodeIds.add(e.target);
    }
    for (const e of edges) {
      const a = byId.get(e.source), b = byId.get(e.target);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", a.x); line.setAttribute("y1", a.y);
      line.setAttribute("x2", b.x); line.setAttribute("y2", b.y);
      line.setAttribute("class", `edge ${rel && e.type !== rel ? "dim" : ""}`);
      line.addEventListener("click", () => {
        details.innerHTML = `<strong>${e.type}</strong><p>${e.source} → ${e.target}</p><p>${e.quote || ""}</p>`;
      });
      svg.appendChild(line);
    }
    for (const n of nodes) {
      const match = !term || n.label.includes(term) || n.id.includes(term);
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.setAttribute("class", `gnode ${match && (!rel || activeNodeIds.has(n.id)) ? "" : "dim"}`);
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", n.x); circle.setAttribute("cy", n.y);
      circle.setAttribute("r", n.type === "event" ? 10 : Math.min(18, 7 + Math.sqrt(n.count || 3) * 2));
      circle.setAttribute("fill", colors[n.type] || "#6b6258");
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      const nearRight = n.x > width() - 210;
      text.setAttribute("x", nearRight ? n.x - 12 : n.x + 12);
      text.setAttribute("y", n.y + 4);
      text.setAttribute("text-anchor", nearRight ? "end" : "start");
      text.textContent = n.label;
      g.appendChild(circle); g.appendChild(text);
      g.addEventListener("click", () => {
        const linked = edges.filter(e => e.source === n.id || e.target === n.id).slice(0, 8);
        details.innerHTML = `<strong>${n.label}</strong><p>${n.type} · ${n.id}</p>` +
          linked.map(e => `<p>${e.type}: ${e.source === n.id ? e.target : e.source}</p>`).join("");
      });
      svg.appendChild(g);
    }
  }
  function loop() {
    for (let i = 0; i < 3; i++) tick();
    render();
    requestAnimationFrame(loop);
  }
  search.addEventListener("input", render);
  filter.addEventListener("change", render);
  loop();
})();
