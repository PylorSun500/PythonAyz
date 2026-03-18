import numpy as np
arr1 = np.array([1, 2, 3, 4, 5])
print(arr1)

arr2 = np.array([[1,2],[3,4],[5,6]])
print(arr2)

# shape and dtype
arrdec_one = np.array([5, 10, 15, 20, 25])
print(arrdec_one)
print(arrdec_one.shape)
print(arrdec_one.dtype)

arrdec_two = np.array([[1,2,3],[4,5,6]])
print(arrdec_two)
print(arrdec_two.shape)
print(arrdec_two.dtype)

arrdec_ones = np.ones((3,4), int)
print(arrdec_ones)
print(arrdec_ones.shape)
print(arrdec_ones.dtype)

arrdec_zeros = np.zeros((100, 100), np.uint8)
print(arrdec_zeros)
print(arrdec_zeros.shape)
print(arrdec_zeros.dtype)

arrdec_full = np.full((2,3,4), -100, np.int32)
print(arrdec_full)
print(arrdec_full.shape)
print(arrdec_full.dtype)