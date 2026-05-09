# 快速排序函数
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    # 选取基准
    pivot = arr[len(arr) // 2]
    # 将小于基准的元素放在左边，大于基准的元素放在右边
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    # 递归调用函数进行排序
    return quick_sort(left) + middle + quick_sort(right)

# 测试代码
arr = [5, 4, 23, 3, 11, 2]
print(quick_sort(arr))
# 输出结果为 [1, 2, 3, 5, 8, 9]