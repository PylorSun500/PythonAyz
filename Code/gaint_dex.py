import numpy as np 
bill = np.array([[50, 20, 30, 100, 40],  # 周一 
                 [45, 15, 25, 80, 30],   # 周二    
                 [60, 25, 40, 120, 50],  # 周三    
                 [55, 20, 35, 90, 35],   # 周四    
                 [70, 30, 50, 150, 60],  # 周五    
                 [80, 35, 45, 200, 70],  # 周六    
                 [65, 25, 30, 180, 55]   # 周日 
                 ])

print("原始数据:")
print(bill)
print()

# 1. 切片索引：提取工作日（周一至周五）的餐饮和交通列（第0,1列）
workdays = bill[0:5, 0:2]  # 行: 0-4（周一至周五），列: 0-1（餐饮、交通）
print("1. 工作日的餐饮和交通消费:")
print(workdays)
print()

# 2. 条件布尔索引：筛选娱乐费用超过100元的所有日期
high_entertainment_days = bill[bill[:, 2] > 100]
print("2. 娱乐费用超过100元的日期:")
print(high_entertainment_days)
print()

# 3. 整数数组索引：提取特定数据
selected_data = np.array([
    [bill[0, 0], bill[1, 2]],  # 周一餐饮, 周二娱乐
    [bill[2, 0], bill[3, 2]],  # 周三餐饮, 周四娱乐
    [bill[4, 0], bill[5, 2]]   # 周五餐饮, 周六娱乐
])
print("3. 提取的特定数据 (3x2 数组):")
print(selected_data)
print()

# 4. 索引赋值：将周末（周六、周日）的其他费用修改为0
bill[5:7, 4] = 0  # 或者 bill[5:, 4] = 0
print("4. 修改后的 bill 数组（周末其他费用为0）:")
print(bill)