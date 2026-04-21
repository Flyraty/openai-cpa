import unittest
from unittest.mock import patch

from utils.email_providers.generator_email_service import GeneratorEmailService


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


if __name__ == "__main__":
    unittest.main()
