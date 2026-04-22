# 毕业生极简生活预算管理模块

一个基于 Flask 的轻量级预算工具，使用 NumPy 进行预算分配计算，使用 Pandas 和 OpenPyXL 生成 Excel 报表，适合毕业生或实习期学生快速建立月度预算意识。

## 功能概览

- 输入每月税后工资和强制储蓄比例，实时生成预算建议。
- 使用 NumPy 向量化计算 5 大消费类别预算金额。
- 自动校验预算总和与储蓄金额不超过工资总额。
- 一键导出 `.xlsx` 报表，包含年度预算总表和实际支出记录模板。
- Excel 内置差异和状态计算，便于月底复盘。

## 目录结构

```text
simple_life/
  app.py
  requirements.txt
  README.md
  templates/
    index.html
  static/
    css/style.css
    js/app.js
```

## 运行方式

```bash
cd /Users/pylorsun/Documents/Study/2025-2026第二学期/PythonAyz/Code/wks/simple_life
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

浏览器访问 `http://127.0.0.1:5000`。

## Excel 说明

- `年度预算总表`：展示 1 月到 12 月的预算分配详情。
- `实际支出记录`：按月份和类别生成支出填写模板。
- `差异`：自动计算 `预算金额 - 实际支出`。
- `状态`：自动标记 `超支` 或 `结余`。

## 算法说明

- 基础类别：`房租`、`餐饮`、`交通`、`通讯`、`生活杂项`
- 基础权重：`[0.30, 0.20, 0.10, 0.05, 0.25]`
- 当用户调整储蓄比例时，系统会对支出部分按相同比例缩放，保证：

```text
各项预算总和 + 储蓄金额 = 月收入
```
