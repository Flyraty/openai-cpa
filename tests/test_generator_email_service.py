import unittest
from unittest.mock import patch

import utils.config as cfg
from utils.email_providers.generator_email_service import GeneratorEmailService
from utils.email_providers.mail_service import get_oai_code


class DummyResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text


class GeneratorEmailServiceTests(unittest.TestCase):
    @patch("utils.email_providers.generator_email_service.requests.get")
    def test_get_verification_code_prefers_email_body_code_over_tracking_link_digits(self, mock_get):
        mock_get.return_value = DummyResponse(
            200,
            """
            <html>
              <body>
                <p>We noticed a suspicious log-in on your account. If that was you, enter this code:</p>
                <h1>170876</h1>
                <p>
                  If you were not trying to log in to ChatGPT, please
                  <a href="https://u20216706.ct.sendgrid.net/ls/click?upn=example">secure account</a>
                </p>
              </body>
            </html>
            """,
        )

        service = GeneratorEmailService()

        self.assertEqual("170876", service.get_verification_code("alightmotion.top/lenkuhn"))

    @patch("utils.email_providers.mail_service.time.sleep", return_value=None)
    @patch("utils.email_providers.generator_email_service.requests.get")
    def test_get_oai_code_skips_reused_generator_email_code_until_new_code_arrives(self, mock_get, _mock_sleep):
        mock_get.return_value = DummyResponse(
            200,
            """
            <html>
              <body>
                <p>Your ChatGPT code is 463686</p>
              </body>
            </html>
            """,
        )

        service = GeneratorEmailService()
        first_code = service.get_verification_code("alightmotion.top/lenkuhn")
        self.assertEqual("463686", first_code)

        original_mode = cfg.EMAIL_API_MODE
        original_proxy = cfg.USE_PROXY_FOR_EMAIL
        try:
            cfg.EMAIL_API_MODE = "generator_email"
            cfg.USE_PROXY_FOR_EMAIL = False
            processed = {"generator_email:alightmotion.top/lenkuhn:463686"}

            with patch(
                "utils.email_providers.generator_email_service.GeneratorEmailService.get_verification_code",
                side_effect=["463686", "463686", "699595"],
            ):
                fresh_code = get_oai_code(
                    "lenkuhn@alightmotion.top",
                    jwt="alightmotion.top/lenkuhn",
                    processed_mail_ids=processed,
                    max_attempts=3,
                )
        finally:
            cfg.EMAIL_API_MODE = original_mode
            cfg.USE_PROXY_FOR_EMAIL = original_proxy

        self.assertEqual("699595", fresh_code)


if __name__ == "__main__":
    unittest.main()
