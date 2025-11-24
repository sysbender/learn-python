from unittest.mock import patch

from learn_patch.patch_demo import parse


@patch("learn_patch.patch_demo.fetch_net")
def test_parse(mock_get):
    mock_get.return_value = "demo"
    assert parse() == "demo123"
