# demo5_timer.py
"""
实际应用：计算函数执行时间
"""

import time
from functools import wraps

def timer(func):
    """计算函数执行时间的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # 高精度计时器
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = (end_time - start_time) * 1000  # 转换为毫秒
        print(f"⏱️  {func.__name__} 执行时间: {elapsed:.4f} 毫秒")
        return result
    return wrapper

@timer
def slow_sum(n):
    """慢速求和（故意用循环）"""
    total = 0
    for i in range(n):
        total += i
        time.sleep(0.0001)  # 故意延时
    return total

@timer
def fast_sum(n):
    """快速求和（用公式）"""
    return n * (n - 1) // 2

# 测试
print("计算 1 到 1000 的和")
slow_sum(1000)
fast_sum(1000)

# 可以装饰已有的函数
@timer
def sleep_function(seconds):
    time.sleep(seconds)
    return "醒了"

result = sleep_function(1)
print(f"返回值: {result}")