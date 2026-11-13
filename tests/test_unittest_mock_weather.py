import json
import unittest
from unittest.mock import MagicMock, patch

from myapp import weather


def fake_response(payload):
    resp = MagicMock()
    resp.read.return_value = json.dumps(payload).encode("utf-8")
    resp.__enter__.return_value = resp
    return resp


class TestWeatherWithPatch(unittest.TestCase):
    @patch("myapp.weather.urllib.request.urlopen")
    def test_fetch_weather(self, mock_urlopen):
        mock_urlopen.return_value = fake_response({"city": "Hanoi", "temp": 31})

        data = weather.fetch_weather("Hanoi")

        self.assertEqual(data["temp"], 31)
        mock_urlopen.assert_called_once()
        self.assertIn("city=Hanoi", mock_urlopen.call_args.args[0])

    @patch("myapp.weather.fetch_weather")
    def test_describe_weather_levels(self, mock_fetch):
        mock_fetch.side_effect = [{"temp": 35}, {"temp": 25}, {"temp": 10}]
        self.assertEqual(weather.describe_weather("A"), "Nóng")
        self.assertEqual(weather.describe_weather("B"), "Mát mẻ")
        self.assertEqual(weather.describe_weather("C"), "Lạnh")
        self.assertEqual(mock_fetch.call_count, 3)

    def test_network_error_propagates(self):
        with patch("myapp.weather.urllib.request.urlopen", side_effect=TimeoutError):
            with self.assertRaises(TimeoutError):
                weather.fetch_weather("Hanoi")


if __name__ == "__main__":
    unittest.main()
