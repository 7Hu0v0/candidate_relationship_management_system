const state = { payload: null, customers: [], selectedId: null, search: "", priority: "all" };
const priorityClass = { P0: "p0", P1: "p1", P2: "p2", P3: "p3" };

async function loadData() {
  const response = await fetch("./data/crm_customers.json");
  state.payload = await response.json();
  state.customers = state.payload.customers;
  state.selectedId = state.customers[0]?.id;
  render();
}

function initials(name) {
  return Array.from(name || "?").slice(0, 2).join("");
}

function filteredCustomers() {
  const q = state.search.trim().toLowerCase();
  return state.customers.filter((customer) => {
    const matchesPriority = state.priority === "all" || customer.priority === state.priority;
    const haystack = [
      customer.name, customer.alias, customer.remark, customer.company,
      customer.relationship_stage, ...(customer.tags || []), ...(customer.role_signals || []),
    ].join(" ").toLowerCase();
    return matchesPriority && (!q || haystack.includes(q));
  });
}

function renderMetrics(customers) {
  const active = customers.filter((c) => ["active", "warm"].includes(c.relationship_stage)).length;
  const p0p1 = customers.filter((c) => ["P0", "P1"].includes(c.priority)).length;
  const avg = customers.length ? Math.round(customers.reduce((sum, c) => sum + c.llm_relevance_score, 0) / customers.length) : 0;
  document.querySelector("#metrics").innerHTML = [
    ["总人数", customers.length], ["高优先级", p0p1], ["活跃/温联系人", active], ["平均相关度", avg],
  ].map(([label, value]) => `<article class="metric"><span>${label}</span><strong>${value}</strong></article>`).join("");
}

function renderTable(customers) {
  const table = document.querySelector("#customer-table");
  document.querySelector("#result-count").textContent = `${customers.length} 条`;
  table.innerHTML = customers.map((customer) => `
    <button class="row ${customer.id === state.selectedId ? "selected" : ""}" type="button" data-id="${customer.id}">
      <span class="avatar">${initials(customer.name)}</span>
      <span class="primary"><strong>${customer.name}</strong><span>${customer.alias || customer.remark || "未标备注"}</span></span>
      <span class="company">${customer.company}</span>
      <span class="badge ${priorityClass[customer.priority]}">${customer.priority}</span>
      <span class="score">${customer.llm_relevance_score}</span>
    </button>
  `).join("");
  table.querySelectorAll(".row").forEach((row) => row.addEventListener("click", () => {
    state.selectedId = row.dataset.id;
    render();
  }));
}

function renderDetail(customers) {
  const detail = document.querySelector("#detail");
  const customer = customers.find((c) => c.id === state.selectedId) || customers[0];
  if (!customer) {
    detail.innerHTML = "<p>没有匹配结果</p>";
    return;
  }
  state.selectedId = customer.id;
  const evidence = (customer.evidence || []).map((item) => `
    <div class="quote"><strong>${item.source}</strong> · ${item.time}<br>${item.text}</div>
  `).join("");
  detail.innerHTML = `
    <h3>${customer.name}</h3>
    <p class="sub">${customer.company} · ${customer.relationship_stage} · ${customer.last_contact_at}</p>
    <span class="badge ${priorityClass[customer.priority]}">${customer.priority}</span>
    <span class="score">${customer.llm_relevance_score} relevance</span>
    <div class="tags">${(customer.tags || []).map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>
    <div class="section-title">下一步</div>
    <p>${customer.next_action}</p>
    <div class="section-title">证据摘要</div>
    <div class="evidence">${evidence || "<p>暂无证据</p>"}</div>
  `;
}

function render() {
  const customers = filteredCustomers();
  renderMetrics(customers);
  renderTable(customers);
  renderDetail(customers);
}

document.querySelector("#search").addEventListener("input", (event) => {
  state.search = event.target.value;
  render();
});
document.querySelector("#priority").addEventListener("change", (event) => {
  state.priority = event.target.value;
  render();
});
loadData().catch((error) => {
  document.body.innerHTML = `<main class="workspace"><h2>数据加载失败</h2><p>${error.message}</p></main>`;
});
