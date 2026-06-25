const STORAGE_KEY = "lm-talent-crm-edits";
const ADMIN_KEY = "lm-talent-crm-admin";
const LOG_KEY = "lm-talent-crm-task-log";
const ADMIN_PASSWORD = "jeffersonhu";

const companyFilters = {
  all: { label: "全部公司", match: () => true },
  OpenAI: { label: "OpenAI", match: (c) => hasCompany(c, ["OpenAI"]) },
  Google: { label: "Google", match: (c) => hasCompany(c, ["Google", "DeepMind"]) },
  Anthropic: { label: "Anthropic", match: (c) => hasCompany(c, ["Anthropic"]) },
  xAI: { label: "xAI", match: (c) => hasCompany(c, ["xAI"]) },
  Meta: { label: "Meta", match: (c) => hasCompany(c, ["Meta"]) },
  ByteDance: { label: "字节", match: (c) => hasCompany(c, ["ByteDance", "字节", "Seed", "豆包"]) },
  Alibaba: { label: "阿里", match: (c) => hasCompany(c, ["Alibaba", "阿里", "Qwen", "通义"]) },
  Tencent: { label: "腾讯", match: (c) => hasCompany(c, ["Tencent", "腾讯", "Hunyuan", "混元"]) },
  ChinaSix: {
    label: "大模型六小龙",
    match: (c) => hasCompany(c, ["DeepSeek", "Moonshot", "Kimi", "Zhipu", "智谱", "MiniMax", "Baichuan", "StepFun", "01.AI"]),
  },
};

const state = {
  payload: null,
  customers: [],
  selectedId: null,
  search: "",
  priority: "all",
  companyFilter: "all",
  view: "workbench",
  edits: loadJson(STORAGE_KEY, {}),
  taskLog: loadJson(LOG_KEY, [
    {
      time: "2026-06-25 16:40:00",
      title: "微信/企微权限检查",
      status: "Blocked",
      detail: "企业机器人权限不足，前台继续使用本地已确认线索。",
    },
  ]),
};

const priorityClass = { P0: "p0", P1: "p1", P2: "p2", P3: "p3" };

async function loadData() {
  const response = await fetch("./data/crm_customers.json");
  state.payload = await response.json();
  state.customers = state.payload.customers.map(applyLocalEdit);
  state.selectedId = state.customers[0]?.id;
  render();
}

function loadJson(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) || fallback;
  } catch {
    return fallback;
  }
}

function saveJson(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function applyLocalEdit(customer) {
  const edit = state.edits[customer.id] || {};
  return {
    ...customer,
    relationship_stage: edit.relationship_stage || customer.relationship_stage,
    priority: edit.priority || customer.priority,
    follow_status: edit.follow_status || customer.follow_status || "未跟进",
    owner: edit.owner || customer.owner || "",
  };
}

function updateCustomerEdit(id, field, value) {
  state.edits[id] = { ...(state.edits[id] || {}), [field]: value };
  saveJson(STORAGE_KEY, state.edits);
  state.customers = state.customers.map((customer) => (customer.id === id ? applyLocalEdit(customer) : customer));
  render();
}

function hasCompany(customer, needles) {
  const haystack = [
    customer.company,
    customer.alias,
    customer.remark,
    ...(customer.tags || []),
  ].join(" ").toLowerCase();
  return needles.some((needle) => haystack.includes(needle.toLowerCase()));
}

function initials(name) {
  return Array.from(name || "?").slice(0, 2).join("");
}

function filteredCustomers() {
  const q = state.search.trim().toLowerCase();
  const filter = companyFilters[state.companyFilter] || companyFilters.all;
  return state.customers.filter((customer) => {
    const matchesPriority = state.priority === "all" || customer.priority === state.priority;
    const matchesCompany = filter.match(customer);
    const haystack = [
      customer.name, customer.alias, customer.remark, customer.company, customer.owner, customer.follow_status,
      customer.relationship_stage, ...(customer.tags || []), ...(customer.role_signals || []),
    ].join(" ").toLowerCase();
    return matchesCompany && matchesPriority && (!q || haystack.includes(q));
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
      <span class="follow">${customer.follow_status}</span>
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
    <div class="field-grid">
      ${selectField("relationship_stage", "关系阶段", customer.relationship_stage, [
        ["new", "新线索"], ["warm", "温联系人"], ["active", "活跃"], ["nurture", "长期维护"],
      ])}
      ${selectField("priority", "优先级", customer.priority, [["P0", "P0"], ["P1", "P1"], ["P2", "P2"], ["P3", "P3"]])}
      ${selectField("follow_status", "跟进状态", customer.follow_status, [
        ["未跟进", "未跟进"], ["待触达", "待触达"], ["已触达", "已触达"], ["已约聊", "已约聊"], ["暂停", "暂停"],
      ])}
      <label class="field"><span>Owner</span><input data-edit-field="owner" data-id="${customer.id}" value="${escapeHtml(customer.owner)}" placeholder="负责人"></label>
    </div>
    <div class="tags">${(customer.tags || []).map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>
    <div class="section-title">下一步</div>
    <p>${customer.next_action}</p>
    <div class="section-title">证据摘要</div>
    <div class="evidence">${evidence || "<p>暂无证据</p>"}</div>
  `;
  detail.querySelectorAll("[data-edit-field]").forEach((control) => {
    const eventName = control.tagName === "INPUT" ? "change" : "change";
    control.addEventListener(eventName, () => updateCustomerEdit(control.dataset.id, control.dataset.editField, control.value.trim()));
  });
}

function selectField(field, label, value, options) {
  return `
    <label class="field">
      <span>${label}</span>
      <select data-edit-field="${field}" data-id="${state.selectedId}">
        ${options.map(([optionValue, text]) => `<option value="${optionValue}" ${optionValue === value ? "selected" : ""}>${text}</option>`).join("")}
      </select>
    </label>
  `;
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
}

function renderAdmin() {
  const unlocked = localStorage.getItem(ADMIN_KEY) === "unlocked";
  document.querySelector("#admin-login").hidden = unlocked;
  document.querySelector("#admin-console").hidden = !unlocked;
  if (!unlocked) return;
  document.querySelector("#log-count").textContent = String(state.taskLog.length);
  document.querySelector("#task-log").innerHTML = state.taskLog.map((item) => `
    <div class="log-row">
      <span>${item.time}</span>
      <strong>${item.title}</strong>
      <b>${item.status}</b>
      <p>${item.detail}</p>
    </div>
  `).join("");
}

function renderView() {
  document.querySelectorAll(".view").forEach((view) => view.classList.toggle("active", view.id === `${state.view}-view`));
  document.querySelectorAll("[data-view]").forEach((button) => button.classList.toggle("active", button.dataset.view === state.view));
}

function renderCompanyFilter() {
  document.querySelector("#scope-label").textContent = companyFilters[state.companyFilter]?.label || "全部公司";
  document.querySelectorAll("[data-company-filter]").forEach((button) => {
    button.classList.toggle("active", button.dataset.companyFilter === state.companyFilter);
  });
}

function render() {
  const customers = filteredCustomers();
  renderView();
  renderCompanyFilter();
  renderMetrics(customers);
  renderTable(customers);
  renderDetail(customers);
  renderAdmin();
}

document.querySelector("#search").addEventListener("input", (event) => {
  state.search = event.target.value;
  render();
});

document.querySelector("#priority").addEventListener("change", (event) => {
  state.priority = event.target.value;
  render();
});

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => {
    state.view = button.dataset.view;
    render();
  });
});

document.querySelectorAll("[data-company-filter]").forEach((button) => {
  button.addEventListener("click", () => {
    state.companyFilter = button.dataset.companyFilter;
    state.view = "workbench";
    render();
  });
});

document.querySelector("#admin-login-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const password = document.querySelector("#admin-password").value;
  if (password !== ADMIN_PASSWORD) {
    document.querySelector("#login-error").textContent = "密码不正确";
    return;
  }
  document.querySelector("#login-error").textContent = "";
  localStorage.setItem(ADMIN_KEY, "unlocked");
  render();
});

document.querySelector("#admin-lock").addEventListener("click", () => {
  localStorage.removeItem(ADMIN_KEY);
  document.querySelector("#admin-password").value = "";
  render();
});

document.querySelector("#simulate-run").addEventListener("click", () => {
  const time = new Date().toLocaleString("zh-CN", { hour12: false });
  state.taskLog.unshift({
    time,
    title: "模拟抓取任务",
    status: "Blocked",
    detail: "已完成规则匹配预演；真实 WeCom/微信扫描等待企业机器人权限和数据库解密条件。",
  });
  state.taskLog = state.taskLog.slice(0, 12);
  saveJson(LOG_KEY, state.taskLog);
  renderAdmin();
});

loadData().catch((error) => {
  document.body.innerHTML = `<main class="workspace"><h2>数据加载失败</h2><p>${error.message}</p></main>`;
});
