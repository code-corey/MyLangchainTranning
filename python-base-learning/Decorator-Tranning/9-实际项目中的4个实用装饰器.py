# demo9_practical_decorators.py
"""
真实项目中常用的装饰器
"""

from functools import wraps
import time
import logging


# 1. 缓存装饰器（增强版）
def cached(ttl_seconds=60):
    """带过期时间的缓存"""

    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()

            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    print(f"✅ 缓存命中 (剩余 {ttl_seconds - (now - timestamp):.0f}秒)")
                    return result
                else:
                    print("⏰ 缓存已过期")

            result = func(*args, **kwargs)
            cache[key] = (result, now)
            print(f"💾 已缓存新结果")
            return result

        return wrapper

    return decorator


# 2. 输入验证装饰器
def validate_types(**type_map):
    """验证函数参数类型"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 将位置参数也转为关键字参数的形式
            func_args = func.__code__.co_varnames
            all_args = {**dict(zip(func_args, args)), **kwargs}

            for param_name, expected_type in type_map.items():
                if param_name in all_args:
                    value = all_args[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"参数 '{param_name}' 应该是 {expected_type.__name__}, "
                            f"实际是 {type(value).__name__}"
                        )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# 3. 日志装饰器
def log(level=logging.INFO):
    """自动记录函数调用日志"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            logger.log(level, f"调用 {func.__name__}(args={args}, kwargs={kwargs})")
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"{func.__name__} 返回: {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} 异常: {e}")
                raise

        return wrapper

    return decorator


# 4. 限流装饰器
def rate_limit(max_calls, time_window):
    """限制函数在时间窗口内的调用次数"""

    def decorator(func):
        calls = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # 清除过期的调用记录
            calls[:] = [call_time for call_time in calls if now - call_time < time_window]

            if len(calls) >= max_calls:
                wait_time = time_window - (now - calls[0])
                raise Exception(f"调用太频繁，请等待 {wait_time:.1f} 秒")

            calls.append(now)
            return func(*args, **kwargs)

        return wrapper

    return decorator


# 测试用例
print("=" * 50)
print("1. 测试缓存装饰器")
print("=" * 50)


@cached(ttl_seconds=3)
def get_user_data(user_id):
    print("🔄 从数据库查询...")
    return {"id": user_id, "name": f"User{user_id}"}


print(get_user_data(1))
print(get_user_data(1))  # 缓存命中
time.sleep(4)
print(get_user_data(1))  # 缓存过期，重新查询

print("\n" + "=" * 50)
print("2. 测试类型验证")
print("=" * 50)


@validate_types(name=str, age=int)
def register_user(name, age):
    return f"用户 {name} 注册成功，年龄 {age}"


print(register_user("Alice", 25))
try:
    print(register_user("Bob", "thirty"))  # 类型错误
except TypeError as e:
    print(f"错误: {e}")

print("\n" + "=" * 50)
print("3. 测试限流")
print("=" * 50)


@rate_limit(max_calls=2, time_window=3)
def api_call():
    return "API 响应成功"


for i in range(4):
    try:
        print(f"第{i + 1}次调用: {api_call()}")
    except Exception as e:
        print(f"第{i + 1}次调用: {e}")
    time.sleep(1)