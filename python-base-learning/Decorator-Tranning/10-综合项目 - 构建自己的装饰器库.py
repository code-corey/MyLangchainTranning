# demo10_decorator_library.py
"""
构建自己的装饰器工具箱
可以保存为 decorators.py 在不同项目中复用
"""

from functools import wraps
import time
import functools


# ========== 性能类装饰器 ==========

class Timer:
    """上下文管理器版本的计时器（配合with使用）"""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.elapsed = (self.end - self.start) * 1000
        print(f"⏱️  代码块执行时间: {self.elapsed:.4f}ms")


def measure_time(func):
    """装饰器版本的计时器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"📈 {func.__name__} 耗时: {(end - start) * 1000:.2f}ms")
        return result

    return wrapper


def memoize(func):
    """记忆化装饰器（自动缓存所有调用）"""
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    return wrapper


# ========== 调试类装饰器 ==========

def debug(func):
    """打印函数调用详情的调试装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"🔍 调用: {func.__name__}({signature})")

        result = func(*args, **kwargs)
        print(f"✅ 返回: {result!r}")
        return result

    return wrapper


def deprecated(func):
    """标记函数为已弃用"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        import warnings
        warnings.warn(
            f"{func.__name__} 已被弃用，将在未来版本移除",
            DeprecationWarning,
            stacklevel=2
        )
        return func(*args, **kwargs)

    return wrapper


# ========== 控制流装饰器 ==========

def singleton(cls):
    """单例模式装饰器"""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def timeout(seconds):
    """函数超时装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def handle_timeout(signum, frame):
                raise TimeoutError(f"函数执行超过 {seconds} 秒")

            signal.signal(signal.SIGALRM, handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator


# ========== 测试所有装饰器 ==========

if __name__ == "__main__":
    print("🎯 测试装饰器工具箱\n" + "=" * 50)

    # 测试计时器
    print("\n1. 计时器测试:")


    @measure_time
    def test_sleep():
        time.sleep(0.5)
        return "完成"


    test_sleep()

    # 测试记忆化
    print("\n2. 记忆化测试:")


    @memoize
    def fibonacci(n):
        if n < 2:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)


    print(f"fib(30) = {fibonacci(30)} (第1次计算)")
    print(f"fib(30) = {fibonacci(30)} (从缓存获取)")

    # 测试调试
    print("\n3. 调试测试:")


    @debug
    def complex_calc(a, b, c=10):
        return a + b * c


    complex_calc(2, 3, c=4)

    # 测试单例
    print("\n4. 单例测试:")


    @singleton
    class DatabaseConnection:
        def __init__(self):
            print("🔌 建立数据库连接...")
            self.id = id(self)

        def query(self):
            return f"查询结果 from connection {self.id}"


    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    print(f"db1 is db2: {db1 is db2}")
    print(db1.query())
    print(db2.query())

    # 测试超时（注意：只在Unix系统上工作）
    print("\n5. 超时测试 (跳过，需要Unix系统):")
    try:
        @timeout(1)
        def slow_task():
            time.sleep(3)
            return "永远不会返回"


        result = slow_task()
    except Exception as e:
        print(f"超时工作正常: {e}")

    # 测试已弃用警告
    print("\n6. 弃用警告测试:")


    @deprecated
    def old_function():
        return "旧函数"


    import warnings

    warnings.filterwarnings("always")
    result = old_function()
    print(result)

    # 使用上下文管理器计时
    print("\n7. 上下文管理器计时:")
    with Timer() as t:
        time.sleep(0.3)
        print("执行了一些操作...")