import unittest
import FizzBuzz_server as app

# Test cases for the FizzBuzz API
class TestFizzBuzz(unittest.TestCase):

    def setUp(self):
        self.app = app.app.test_client()

    def test_valid_params(self):
        response = self.app.get('/fizzbuzz?int1=3&int2=5&str1=fizz&str2=buzz&limit=15')
        expected = "1,2,fizz,4,buzz,fizz,7,8,fizz,buzz,11,fizz,13,14,fizzbuzz"
        self.assertEqual(response.data.decode(), expected)

    def test_invalid_params(self):
        response = self.app.get('/fizzbuzz?int1=foo&int2=bar') 
        self.assertEqual(response.status_code, 400)

    def test_default_params(self):
        response = self.app.get('/fizzbuzz')
        expected = "1,2,fizz,4,buzz,fizz,7,8,fizz,buzz,11,fizz,13,14,fizzbuzz,16,17,fizz,19,buzz" 
        self.assertEqual(response.data.decode()[:len(expected)], expected)

    def test_stats(self):
        self.app.get('/fizzbuzz?int1=2&int2=7&str1=foo&str2=bar&limit=30')
        response = self.app.get('/stats')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'int1' in response.data)

if __name__ == '__main__':
    unittest.main()