from typing import Iterator


def quick_sort(arr) -> Iterator[list[int]]:
    quick_sort_helper(arr, 0, len(arr) - 1)
    return arr


def quick_sort_helper(arr, low: int = 0, high: int = 0):
    if low < high:
        pivot_index = partition(low, high, arr)
        quick_sort_helper(arr, low, pivot_index - 1)
        quick_sort_helper(arr, pivot_index + 1, high)


def partition(low, high, arr):
    pivot = arr[high]
    i = low
    for j in range(i, high):
        if arr[j] <= pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[high] = arr[high], arr[i]
    return i
