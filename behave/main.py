
def incrementor(stride: int):
    def f(x:int):
        return x + stride
    return f


foo = incrementor(10)
print(foo(5))