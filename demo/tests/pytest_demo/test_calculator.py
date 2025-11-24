from pytest_demo.calculator import Calculator
import pytest

from typing import Generator
#TODO: fixture is facotry method
@pytest.fixture(scope="session")
# default=function, class , module, package, session, 

def calc()->Calculator:
    return Calculator()

 
@pytest.mark.parametrize("n1,n2,expected", [
    [1,2,3], 
    [-2,2,0]

])
def test_add(calc: Calculator , n1:int, n2:int, expected:int):      
    assert calc.add(n1, n2)  == expected


def test_subtract(calc: Calculator):
   
    result =  calc.subtract(5, 1) 
    assert result == 4

def test_zero_division(calc: Calculator):
   
    #TODO: pytest.raise
    with pytest.raises(ZeroDivisionError):
        calc.divide(2,0)