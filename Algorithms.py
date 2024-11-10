def BubbleSort(arr, col_indices):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            for col_index in col_indices:
                if arr[j][col_index] > arr[j + 1][col_index]:  
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    break  
    return arr


def SelectionSort(arr, col_index):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j][col_index] < arr[min_idx][col_index]:  
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def InsertionSort(arr, col_index):
    """Insertion Sort for ascending order"""
    n = len(arr)
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and key[col_index] < arr[j][col_index]:  
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def MergeSort(arr, col_indices):
    if len(arr) > 1:
        
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        MergeSort(left_half, col_indices)
        MergeSort(right_half, col_indices)

        i = j = k = 0

        while i < len(left_half) and j < len(right_half):

            for col_index in col_indices:
                if left_half[i][col_index] < right_half[j][col_index]:
                    arr[k] = left_half[i]
                    i += 1
                    break
                elif left_half[i][col_index] > right_half[j][col_index]:
                    arr[k] = right_half[j]
                    j += 1
                    break
            else:

                arr[k] = left_half[i]
                i += 1

            k += 1

        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1

    return arr

def QuickSort(arr, col_indices):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[len(arr) // 2]

        less_than = []
        equal_to = []
        greater_than = []

        for item in arr:
            for col_index in col_indices:
                if item[col_index] < pivot[col_index]:
                    less_than.append(item)
                    break
                elif item[col_index] > pivot[col_index]:
                    greater_than.append(item)
                    break
            else:
                
                equal_to.append(item)

        return QuickSort(less_than, col_indices) + equal_to + QuickSort(greater_than, col_indices)


def CountingSort(arr, col_indices):
    

    for col_index in col_indices:
     if any(isinstance(row[col_index], str) for row in arr):
        raise ValueError(f"Invalid data type in column {col_index}. Strings are not allowed.")

    for col_index in col_indices:
        max_val = max(row[col_index] for row in arr)  
        count = [0] * (max_val + 1)  

        for row in arr:
            count[row[col_index]] += 1

        for i in range(1, len(count)):
            count[i] += count[i - 1]

        output = [None] * len(arr)
        for row in reversed(arr):
            output[count[row[col_index]] - 1] = row
            count[row[col_index]] -= 1

        arr = output
    
    return arr
def odd_even_sort(arr, col_indices):
   
    n = len(arr)
    sorted = False

    while not sorted:
        sorted = True

        for i in range(1, n, 2):
            if i < n - 1:
                
                if any(arr[i][col] > arr[i + 1][col] for col in col_indices):
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    sorted = False

        for i in range(0, n, 2):
            if i < n - 1:

                if any(arr[i][col] > arr[i + 1][col] for col in col_indices):
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                    sorted = False

    return arr

def counting_sort_for_radix(arr, col_index, exp):
    n = len(arr)
    output = [None] * n  
    count = [0] * 10  

    for row in arr:
        index = (row[col_index] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]


    for i in range(n - 1, -1, -1):
        index = (arr[i][col_index] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1

    for i in range(n):
        arr[i] = output[i]

def RadixSort(arr, col_indices):
    
    for col_index in col_indices:
        if not all(isinstance(row[col_index], (int, float)) for row in arr):
            raise ValueError(f"Invalid data type in column {col_index}. Only numeric types are allowed.")
    

    for col_index in col_indices:
        max_val = max(row[col_index] for row in arr)  
        exp = 1

        while max_val // exp > 0:
            counting_sort_for_radix(arr, col_index, exp)
            exp *= 10
    
    return arr

def gnome_sort(arr, col_indices):
   
    index = 0
    n = len(arr)

    while index < n:
        if index == 0:
            index += 1

        if all(arr[index][col] >= arr[index - 1][col] for col in col_indices):
            index += 1
        else:
            arr[index], arr[index - 1] = arr[index - 1], arr[index]
            index -= 1

    return arr

def bucket_sort(arr, col_indices):
    if not arr:  
        return arr

    num_buckets = 10  
    buckets = [[] for _ in range(num_buckets)]

    min_value = min(row[col_indices[0]] for row in arr)
    max_value = max(row[col_indices[0]] for row in arr)

    if max_value == min_value:
        return sorted(arr, key=lambda x: [x[i] for i in col_indices])

    interval = (max_value - min_value) / num_buckets


    for row in arr:
        bucket_index = min(int((row[col_indices[0]] - min_value) / interval), num_buckets - 1)
        buckets[bucket_index].append(row)


    sorted_buckets = []
    for bucket in buckets:
        sorted_buckets.extend(sorted(bucket, key=lambda x: [x[i] for i in col_indices]))

    return sorted_buckets
