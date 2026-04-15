import unittest
from unittest.mock import patch

import utils.config as cfg
from utils.integrations.sub2api_client import Sub2APIClient


class DummyResponse:
    def __init__(self, status_code=200, text='data: {"type":"test_complete","success":true}\n'):
        self.status_code = status_code
        self.text = text


class Sub2APIClientTests(unittest.TestCase):
    def setUp(self):
        self.client = Sub2APIClient("https://sub2api.example.com", "test-key")

    @patch("utils.integrations.sub2api_client.cffi_requests.post")
    def test_test_account_uses_default_model_id_when_config_missing(self, mock_post):
        mock_post.return_value = DummyResponse()

        with patch.object(cfg, "SUB2API_TEST_MODEL", "", create=True):
            result, reason = self.client.test_account(123)

        self.assertEqual(("ok", "test completed"), (result, reason))
        self.assertEqual("gpt-5.4", mock_post.call_args.kwargs["json"]["model_id"])

    @patch("utils.integrations.sub2api_client.cffi_requests.post")
    def test_test_account_uses_configured_model_id(self, mock_post):
        mock_post.return_value = DummyResponse()

        with patch.object(cfg, "SUB2API_TEST_MODEL", "gpt-4.1-mini", create=True):
            result, reason = self.client.test_account(456)

        self.assertEqual(("ok", "test completed"), (result, reason))
        self.assertEqual("gpt-4.1-mini", mock_post.call_args.kwargs["json"]["model_id"])


class Sub2APIConfigTests(unittest.TestCase):
    def test_reload_all_configs_reads_sub2api_test_model(self):
        original_init_config = cfg.init_config
        original_model = getattr(cfg, "SUB2API_TEST_MODEL", "")

        def fake_init_config():
            return {
                "sub2api_mode": {
                    "test_model": "gpt-4o-mini",
                },
            }

        try:
            cfg.init_config = fake_init_config
            cfg.reload_all_configs()
            self.assertEqual("gpt-4o-mini", cfg.SUB2API_TEST_MODEL)
        finally:
            cfg.init_config = original_init_config
            cfg.SUB2API_TEST_MODEL = original_model


if __name__ == "__main__":
    unittest.main()
