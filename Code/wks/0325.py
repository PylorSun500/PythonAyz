import numpy as np
np.set_printoptions(precision=2, suppress=True)

# [商品ID, 类别, 数量, 单价, 日期, 库存, 总额]
data = np.array([
    [23, 1, 4, 2453.12, 15, 850, 9812.48],
    [8,  2, 6, 128.50,  3, 420, 771.00],
    [41, 3, 2, 89.99,  27, 150, 179.98],
    [15, 4, 1, 156.00,  0, 600, 156.00],
    [33, 1, 8, 5670.25, 12, 95, 45362.00],
    [19, 2, 3, 210.75, 22, 310, 632.25],
    [50, 3, 5, 45.50,   8, 780, 227.50],
    [7,  1, 1, 8999.00, 19, 50, 8999.00],
    [28, 4, 12, 34.20,  5, 890, 410.40],
    [4,  2, 7, 345.60, 29, 200, 2419.20]
])
print("数据形状:", data.shape)

# 提取销售总额列
sales = data[:, 6]

total_sales = np.sum(sales)       # 总销售额
avg_sales = np.mean(sales)        # 平均订单金额
max_sales = np.max(sales)         # 最高单笔金额
min_sales = np.min(sales)         # 最低单笔金额

print(f"总销售额: {total_sales:.2f}")
print(f"平均订单金额: {avg_sales:.2f}")
print(f"最高单笔金额: {max_sales:.2f}")
print(f"最低单笔金额: {min_sales:.2f}")

# 提取 col 2
qty = data[:, 2]

# qty > 10 
high_volume_mask = qty > 10
high_volume_orders = data[high_volume_mask]

# 统计数量
high_volume_count = np.sum(high_volume_mask)

print("高销量订单（销售数量 > 10）：")
print(high_volume_orders)
print(f"高销量订单总数: {int(high_volume_count)}")

# col 3
prices = data[:, 3]

# ceil
prices_ceil = np.ceil(prices)
print("向上取整后的单价:", prices_ceil)

# floor
prices_floor = np.floor(prices)
sorted_prices = np.sort(prices_floor)
cheapest_3 = sorted_prices[:3]
print("向下取整后的单价:", prices_floor)
print("最便宜的3个价格点:", cheapest_3)

# stock
stock = data[:, 5]

# stock < 100
low_stock_mask = stock < 100
low_stock_items = data[low_stock_mask]

print("低库存商品：")
print(low_stock_items)

# low_stock_items sort
low_stock_qty = low_stock_items[:, 2]         # 销售数量
sorted_qty_desc = np.sort(low_stock_qty)[::-1]  # 降序
sorted_items_desc = low_stock_items[np.argsort(-low_stock_items[:, 2])]

print("低库存商品按销量降序排列：")
print(sorted_items_desc)

# for cat in cate
categories = [1, 2, 3, 4]
category_sales = {}

for cat in categories:
    mask = data[:, 1] == cat
    total = np.sum(data[mask, 6])   # 筛选行，对第6列求和
    category_sales[cat] = total
    print(f"类别 {cat} 总销售额: {total:.2f}")

# highest
best_category_id = max(category_sales, key=category_sales.get)
print(f"\n销售额最高的商品类别: {best_category_id} (销售额: {category_sales[best_category_id]:.2f})")