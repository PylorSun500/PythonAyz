const state = {
  pendingOverspendPayload: null,
};

const settingsForm = document.getElementById("settingsForm");
const billForm = document.getElementById("billForm");
const overspendOverlay = document.getElementById("overspendOverlay");
const overspendSummary = document.getElementById("overspendSummary");
const overspendReason = document.getElementById("overspendReason");
const todayReviewList = document.getElementById("todayReviewList");
const toast = document.getElementById("toast");

document.addEventListener("DOMContentLoaded", () => {
  billForm.elements.date.value = formatDateInput(new Date());
  bindEvents();
  loadDashboard();
});

function bindEvents() {
  settingsForm.addEventListener("submit", handleSettingsSubmit);
  billForm.addEventListener("submit", handleBillSubmit);
  billForm.addEventListener("reset", () => {
    window.setTimeout(() => {
      billForm.elements.date.value = formatDateInput(new Date());
      setStatus("billStatus", state.pendingOverspendPayload ? "等待补充原因" : "等待输入");
    }, 0);
  });

  document.getElementById("confirmOverspendBtn").addEventListener("click", confirmOverspendBill);
  document.getElementById("cancelOverspendBtn").addEventListener("click", resetOverspendFlow);
  document.getElementById("closeOverspendBtn").addEventListener("click", resetOverspendFlow);
  overspendOverlay.addEventListener("click", (event) => {
    if (event.target === overspendOverlay) {
      resetOverspendFlow();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !overspendOverlay.classList.contains("hidden")) {
      resetOverspendFlow();
    }
  });
}

async function loadDashboard() {
  try {
    const response = await fetch("/api/dashboard");
    const payload = await response.json();
    renderDashboard(payload);
    setStatus("settingsStatus", "已同步 Excel");
  } catch (error) {
    showToast("读取仪表盘失败，请检查 Flask 服务。", true);
  }
}

async function handleSettingsSubmit(event) {
  event.preventDefault();

  const payload = {
    daily_budget: settingsForm.elements.daily_budget.value,
    weekly_budget: settingsForm.elements.weekly_budget.value,
  };

  try {
    const response = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || "预算保存失败");
    }

    renderDashboard(result.dashboard);
    setStatus("settingsStatus", "预算已保存");
    showToast(result.message);
  } catch (error) {
    setStatus("settingsStatus", "保存失败");
    showToast(error.message, true);
  }
}

async function handleBillSubmit(event) {
  event.preventDefault();
  const payload = collectBillFormPayload();

  try {
    await submitBillPayload(payload);
  } catch (error) {
    showToast(error.message, true);
  }
}

async function submitBillPayload(payload) {
  const response = await fetch("/api/bills", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();

  if (response.status === 409) {
    state.pendingOverspendPayload = payload;
    showOverspendReview(result.review);
    setStatus("billStatus", "等待补充原因");
    showToast(result.message, true);
    return;
  }

  if (!response.ok) {
    throw new Error(result.message || "账单提交失败");
  }

  renderDashboard(result.dashboard);
  billForm.reset();
  billForm.elements.date.value = formatDateInput(new Date());
  resetOverspendFlow(false);
  setStatus("billStatus", "账单已写入 Excel");
  showToast(result.message);
}

async function confirmOverspendBill() {
  if (!state.pendingOverspendPayload) {
    return;
  }

  const reason = overspendReason.value.trim();
  if (!reason) {
    showToast("请先填写超支原因，再确认保存。", true);
    overspendReason.focus();
    return;
  }

  try {
    await submitBillPayload({
      ...state.pendingOverspendPayload,
      overspend_reason: reason,
    });
  } catch (error) {
    showToast(error.message, true);
  }
}

function showOverspendReview(review) {
  overspendSummary.textContent = `当前提交后今日总支出为 ¥${formatMoney(review.today_total_after)}，超过日预算 ¥${formatMoney(
    review.daily_budget,
  )}。超出部分 ¥${formatMoney(review.overage_amount)} 将自动从本周剩余额度中扣减。`;
  todayReviewList.innerHTML = review.today_records
    .map(
      (item) => `
        <li>
          <strong>${escapeHtml(item.category)}</strong>
          <div>¥${formatMoney(item.amount)} · ${escapeHtml(item.date)}</div>
          <div>${escapeHtml(item.note || "无备注")}</div>
        </li>
      `,
    )
    .join("");

  overspendReason.value = "";
  overspendOverlay.classList.remove("hidden");
  document.body.classList.add("modal-open");
  window.setTimeout(() => overspendReason.focus(), 60);
}

function resetOverspendFlow(resetPending = true) {
  if (resetPending) {
    state.pendingOverspendPayload = null;
  }

  overspendOverlay.classList.add("hidden");
  document.body.classList.remove("modal-open");
  overspendReason.value = "";
  todayReviewList.innerHTML = "";

  if (!state.pendingOverspendPayload) {
    setStatus("billStatus", "等待输入");
  }
}

function collectBillFormPayload() {
  return {
    date: billForm.elements.date.value,
    category: billForm.elements.category.value.trim(),
    amount: billForm.elements.amount.value,
    note: billForm.elements.note.value.trim(),
  };
}

function renderDashboard(dashboard) {
  renderHeader(dashboard.stats);
  renderSettings(dashboard.settings);
  renderStatCards(dashboard.stats);
  renderCategoryBreakdown(dashboard.category_breakdown);
  renderBills(dashboard.bills);
  renderFlagged(dashboard.high_value_bills);
}

function renderHeader(stats) {
  document.getElementById("todayLabel").textContent = `今日 ${stats.today}`;
  document.getElementById("weekLabel").textContent = `${stats.week_start} - ${stats.week_end}`;
}

function renderSettings(settings) {
  settingsForm.elements.daily_budget.value = settings.daily_budget;
  settingsForm.elements.weekly_budget.value = settings.weekly_budget;
}

function renderStatCards(stats) {
  const cards = [
    {
      label: "今日总支出",
      value: stats.today_total,
      note: `剩余 ¥${formatMoney(stats.today_remaining)}`,
      negative: stats.today_remaining < 0,
    },
    {
      label: "本周总支出",
      value: stats.week_total,
      note: `剩余 ¥${formatMoney(stats.week_remaining)}`,
      negative: stats.week_remaining < 0,
    },
    {
      label: "今日超支额",
      value: stats.today_overage,
      note: stats.today_overage > 0 ? "今日已触发超支逻辑" : "今日预算仍安全",
      negative: stats.today_overage > 0,
    },
    {
      label: "周预算惩罚累计",
      value: stats.week_penalty_applied,
      note: "来自超支部分扣减",
      negative: stats.week_penalty_applied > 0,
    },
  ];

  document.getElementById("statCards").innerHTML = cards
    .map(
      (card) => `
        <article class="stat-card">
          <span class="stat-label">${card.label}</span>
          <span class="stat-value ${card.negative ? "money-negative" : "money-positive"}">¥${formatMoney(card.value)}</span>
          <span class="stat-note">${card.note}</span>
        </article>
      `,
    )
    .join("");
}

function renderCategoryBreakdown(items) {
  const container = document.getElementById("categoryBreakdown");
  if (!items.length) {
    container.innerHTML = '<div class="empty-state">本周还没有消费记录。</div>';
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <article class="breakdown-item">
          <div class="breakdown-row">
            <strong>${escapeHtml(item.category)}</strong>
            <span>¥${formatMoney(item.amount)} / ${item.percentage}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-bar" style="width: ${Math.min(item.percentage, 100)}%"></div>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderBills(items) {
  const tbody = document.getElementById("billTableBody");
  if (!items.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-state">还没有账单，先录入一笔试试。</td></tr>';
    return;
  }

  tbody.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.date || "-")}</td>
          <td>${escapeHtml(item.category || "-")}</td>
          <td>¥${formatMoney(item.amount)}</td>
          <td>${escapeHtml(item.note || "-")}</td>
          <td>${escapeHtml(item.overspend_reason || "-")}</td>
          <td>${item.penalty_applied ? `¥${formatMoney(item.penalty_applied)}` : "-"}</td>
        </tr>
      `,
    )
    .join("");
}

function renderFlagged(items) {
  const container = document.getElementById("flaggedList");
  if (!items.length) {
    container.innerHTML = '<div class="empty-state">当前没有超过日预算阈值的单笔账单。</div>';
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
        <article class="flagged-item">
          <strong>${escapeHtml(item.category)}</strong>
          <div>${escapeHtml(item.date)} · ¥${formatMoney(item.amount)}</div>
          <div>${escapeHtml(item.note || "无备注")}</div>
        </article>
      `,
    )
    .join("");
}

function setStatus(elementId, message) {
  document.getElementById(elementId).textContent = message;
}

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.classList.remove("hidden");
  toast.style.background = isError ? "rgba(127, 29, 29, 0.94)" : "rgba(31, 41, 51, 0.92)";
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.classList.add("hidden");
  }, 2600);
}

function formatMoney(value) {
  return Number(value || 0).toFixed(2);
}

function formatDateInput(dateValue) {
  return dateValue.toISOString().split("T")[0];
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
