class Calculator:

    def add(self, a: int, b: int) -> int:
        return a + b

    def subtract(self, a: int, b: int) -> int:
        return a - b

    def divide(self, a: int, b: int) -> float:
        if b == 0:
            raise ZeroDivisionError()
        return a / b


    



