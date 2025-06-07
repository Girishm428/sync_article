import pytest
import requests
from unittest.mock import patch
from core.zendesk import update_zendesk_translation

@patch("core.zendesk.requests.put")
def test_update_zendesk_translation_success(mock_put):
    mock_put.return_value.status_code = 200
    mock_put.return_value.text = "Success"

    try:
        update_zendesk_translation(123, "en-us", "Title", "<p>Body</p>")
    except Exception:
        pytest.fail("update_zendesk_translation raised Exception unexpectedly!")

    mock_put.assert_called_once()

@patch("core.zendesk.requests.put")
def test_update_zendesk_translation_failure(mock_put):
    mock_put.return_value.status_code = 400
    mock_put.return_value.text = "Bad request"
    mock_put.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError()

    with pytest.raises(requests.exceptions.HTTPError):
        update_zendesk_translation(123, "en-us", "Title", "<p>Body</p>")
