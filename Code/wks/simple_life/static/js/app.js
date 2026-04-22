const budgetForm = document.getElementById("budgetForm");
const salaryInput = document.getElementById("salaryInput");
const savingsRange = document.getElementById("savingsRange");
const savingsInput = document.getElementById("savingsInput");
const exportButton = document.getElementById("exportButton");
const toast = document.getElementById("toast");

document.addEventListener("DOMContentLoaded", () => {
  bindEvents();
  requestBudget();
});

function bindEvents() {
  budgetForm.addEventListener("submit", (event) => {
    event.preventDefault();
    requestBudget();
  });

  salaryInput.addEventListener("input", debounce(requestBudget, 280));

  savingsRange.addEventListener("input", () => {
    savingsInput.value = savingsRange.value;
    requestBudget();
  });

  savingsInput.addEventListener("input", () => {
    const safeValue = clampValue(savingsInput.value, 0, 50);
    savingsRange.value = safeValue;
    savingsInput.value = safeValue;
    requestBudget();
  });

  exportButton.addEventListener("click", exportWorkbook);
}

async function requestBudget() {
  const payload = collectPayload();

  if (!payload.salary || Number(payload.salary) <= 0) {
    setStatus("请输入有效工资");
    return;
  }

  try {
    const response = await fetch("/api/budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || "预算计算失败");
    }

    renderPlan(result.plan);
    setStatus("预算已更新");
  } catch (error) {
    setStatus("计算失败");
    showToast(error.message, true);
  }
}

async function exportWorkbook() {
  const payload = collectPayload();

  try {
    const response = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorPayload = await response.json();
      throw new Error(errorPayload.message || "导出失败");
    }

    const blob = await response.blob();
    const disposition = response.headers.get("Content-Disposition") || "";
    const fileNameMatch = disposition.match(/filename="?([^"]+)"?/);
    const fileName = fileNameMatch ? fileNameMatch[1] : "graduation_budget.xlsx";
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = fileName;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);

    showToast("Excel 报表已生成并开始下载。");
  } catch (error) {
    showToast(error.message, true);
  }
}

function renderPlan(plan) {
  document.getElementById("salaryDisplay").textContent = money(plan.monthly_salary);
  document.getElementById("savingsDisplay").textContent = money(plan.savings_amount);
  document.getElementById("spendingDisplay").textContent = money(
    plan.items.reduce((sum, item) => sum + Number(item.amount || 0), 0),
  );
  document.getElementById("remainingDisplay").textContent = money(plan.savings_amount + plan.remaining_amount);

  document.getElementById("budgetCards").innerHTML = plan.items
    .map(
      (item) => `
        <article class="budget-card">
          <h3>${escapeHtml(item.category)}</h3>
          <p>建议占比 ${item.percent}%</p>
          <p>基于可支配支出部分自动缩放</p>
          <strong>${money(item.amount)}</strong>
        </article>
      `,
    )
    .join("");

  document.getElementById("annualTableBody").innerHTML = Array.from({ length: 12 }, (_, index) => {
    return `
      <tr>
        <td>${index + 1}月</td>
        <td>${money(plan.annual_budget_matrix[index][0])}</td>
        <td>${money(plan.annual_budget_matrix[index][1])}</td>
        <td>${money(plan.annual_budget_matrix[index][2])}</td>
        <td>${money(plan.annual_budget_matrix[index][3])}</td>
        <td>${money(plan.annual_budget_matrix[index][4])}</td>
        <td>${money(plan.savings_amount)}</td>
      </tr>
    `;
  }).join("");
}

function collectPayload() {
  return {
    salary: Number(salaryInput.value || 0),
    savings_ratio: Number(savingsInput.value || 0),
  };
}

function setStatus(message) {
  document.getElementById("statusText").textContent = message;
}

function money(value) {
  return `¥${Number(value || 0).toFixed(2)}`;
}

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.style.background = isError ? "rgba(127, 29, 29, 0.94)" : "rgba(17, 24, 39, 0.94)";
  toast.classList.remove("hidden");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    toast.classList.add("hidden");
  }, 2500);
}

function clampValue(value, min, max) {
  const numeric = Number(value || 0);
  return String(Math.min(max, Math.max(min, numeric)));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function debounce(fn, wait) {
  let timerId;
  return (...args) => {
    window.clearTimeout(timerId);
    timerId = window.setTimeout(() => fn(...args), wait);
  };
}
