from models.statistic_utils import calcMNK, calcMNKMean

a, b = calcMNK([1, 2, 3, 4, 5])
x = calcMNKMean([1, 2, 3, 4, 5])
print(a, b, x)
