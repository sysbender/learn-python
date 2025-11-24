from pathlib import Path
import pytest
from typing import Any, Generator

#TODO: yield in fixture
@pytest.fixture 
def opened_temp_file(tmp_path ) -> Generator[Path, Any, None]:
    # setup 
    file_path = tmp_path / "demo.txt"
    
    f = file_path.open("w+")
    yield f
    f.close()
  


def test_using_tmp_file(opened_temp_file):
    assert opened_temp_file.write("hello") 
    opened_temp_file.seek(0)
    assert opened_temp_file.read() == "hello"