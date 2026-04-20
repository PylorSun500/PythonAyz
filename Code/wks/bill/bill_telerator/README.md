# Bill Telerator

一个轻量级个人财务管理系统，使用 Flask 提供 Web 界面，使用 pandas + Excel 做本地持久化，并用 NumPy 完成预算统计和超支预警。

## 功能概览

- 自动创建 `bills_data.xlsx`，包含 `bills` 和 `settings` 两个 Sheet。
- 支持修改日预算、周预算，并实时写回 Excel。
- 账单录入后立即持久化，重启应用后数据不丢失。
- 使用 NumPy 的 `np.sum()` 和布尔索引进行今日/本周支出统计与高金额账单筛选。
- 当新增账单导致当日超支时，前端会弹出红色警示区，要求填写超支原因，并展示当天消费明细供审查。
- 超支部分会记录为周预算惩罚金额，自动从周预算剩余额度中扣减。

## 运行方式

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

浏览器访问 `http://127.0.0.1:5000`。

## 数据文件

- Excel 文件路径：`./bills_data.xlsx`
- 账单 Sheet：`bills`
- 设置 Sheet：`settings`

## 说明

- 每周开始时会自动重置本周的超支惩罚累计值。
- 历史账单会一直保留在 Excel 中，统计面板默认聚焦于当前周。
