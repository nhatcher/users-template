import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase


class UsersTests(TestCase):
    """Tests users API"""

    def setUp(self) -> None:
        """Sets up tests client."""
        # We create a user
        self.user = User.objects.create_user(
            "my_username", "test@example.com", "A_Pas$word123"
        )

    def test_successful_login(self):
        """Test normal login"""
        response = self.client.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_username",
                    "password": "A_Pas$word123",
                }
            ),
        )

        self.assertEqual(response.status_code, 200)

    def test_login_csrftoken(self):
        """Test user can login if csrftoken is right"""
        # Note that django ignores the csrf checks by default
        # Here we get a csrf token from a session call
        c = Client(enforce_csrf_checks=True)
        response = c.get("/api/session/")
        self.assertEqual(response.status_code, 200)
        csrftoken = response.cookies["csrftoken"].value

        headers = {"X-CSRFToken": csrftoken}
        response = c.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_username",
                    "password": "A_Pas$word123",
                }
            ),
            headers=headers,  # type: ignore
        )
        self.assertEqual(response.status_code, 200)

        # Hopefully wrong token
        headers = {"X-CSRFToken": "d6MrkXhL4BAIllYATNS8egOzvMzwrong"}
        response = c.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_username",
                    "password": "A_Pas$word123",
                }
            ),
            headers=headers,  # type: ignore
        )
        self.assertEqual(response.status_code, 403)

    def test_unsuccessful_login_password(self):
        """Test user cannot login if password is wrong"""
        response = self.client.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_username",
                    "password": "wrong-password",
                }
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_unsuccessful_login_with_wrong_username(self):
        """Test we cannot login with a wrong username"""
        response = self.client.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_other_username",
                    "password": "A_Pas$word123",
                }
            ),
        )

        self.assertEqual(response.status_code, 400)

    def test_missing_password(self):
        """Test we cannot login without a password"""
        # Note: We could "fix" this and return a 400
        with self.assertRaises(KeyError):
            self.client.post(
                "/api/login/",
                content_type="application/json",
                data=json.dumps(
                    {
                        "username": "my_username",
                    }
                ),
            )

    def test_missing_username(self):
        """Test we cannot login without a password"""
        # Note: We could "fix" this and return a 400
        with self.assertRaises(KeyError):
            self.client.post(
                "/api/login/",
                content_type="application/json",
                data=json.dumps(
                    {
                        "password": "my_password",
                    }
                ),
            )

    @patch("users.email.send_confirmation_email")
    def test_create_account(self, send_confirmation_email_mock: MagicMock):
        """
        Test we can create an account.

        We test the full cycle. Note that we need to patch `send_confirmation_email`,
        otherwise we would end up sending emails during the tests!

        We create the account, check that we cannot login, activate the account and finally check
        that we can login.

        We need to check the arguments `send_confirmation_email_mock` was called with to get the
        `email_token`
        """
        response = self.client.post(
            "/api/create-account/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "nick_username",
                    "password": "A_Pas$word123",
                    "nickname": "Nick",
                    "first-name": "Leonard",
                    "last-name": "Cohen",
                    "email": "fake@example.com",
                }
            ),
        )

        self.assertEqual(response.status_code, 200)

        # check I cannot login (Account not activated)
        response = self.client.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "nick_username",
                    "password": "A_Pas$word123",
                }
            ),
        )

        self.assertEqual(response.status_code, 400)

        # Check the email function was called with the right arguments
        args = send_confirmation_email_mock.call_args.args

        self.assertEqual(args[0], "fake@example.com")
        self.assertEqual(args[1], "nick_username")

        email_token = args[2]
        # activate the account:
        response = self.client.get(f"/api/activate-account/{email_token}")

        # check I can login now!
        response = self.client.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "nick_username",
                    "password": "A_Pas$word123",
                }
            ),
        )

        self.assertEqual(response.status_code, 200)

    def test_create_account_fails_if_username_is_taken(self):
        """Test we cannot create an account if there is already an account with the same username"""
        response = self.client.post(
            "/api/create-account/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_username",
                    "password": "A_Pas$word123",
                    "nickname": "Nick",
                    "first-name": "Leonard",
                    "last-name": "Cohen",
                    "email": "fake@example.com",
                }
            ),
        )

        self.assertEqual(response.status_code, 400)

    def test_create_account_fails_if_email_is_taken(self):
        """Test we cannot create an account if there is already an account with the same username"""
        response = self.client.post(
            "/api/create-account/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_new_username",
                    "password": "A_Pas$word123",
                    "nickname": "Nick",
                    "first-name": "Leonard",
                    "last-name": "Cohen",
                    "email": "test@example.com",
                }
            ),
        )

        self.assertEqual(response.status_code, 400)

    def test_whoami(self):
        """Test we can call whoami if we are logged in"""

        # Cannot access before logging in
        response = self.client.post("/api/whoami/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertAlmostEqual(data["authenticated"], False)

        response = self.client.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_username",
                    "password": "A_Pas$word123",
                }
            ),
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.post("/api/whoami/")

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertAlmostEqual(data["authenticated"], True)
        self.assertAlmostEqual(data["username"], "my_username")

        response = self.client.post("/api/logout/")
        self.assertEqual(response.status_code, 200)

        # Again cannot access info
        response = self.client.post("/api/whoami/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertAlmostEqual(data["authenticated"], False)

    @patch("users.email.send_update_password_email")
    def test_recover_password(self, send_update_password_email_mock: MagicMock):
        """
        Tests recover password functionality is working properly.

        We follow here the whole cycle. Note that we need to patch the send email method.
        """

        # 1. Send the request to update my password
        response = self.client.post(
            "/api/recover-password/",
            content_type="application/json",
            data=json.dumps(
                {
                    "email": "test@example.com",
                }
            ),
        )

        self.assertEqual(response.status_code, 200)

        # 2. Check the email has been send and capture the email token
        args = send_update_password_email_mock.call_args.args
        self.assertEqual(args[0], "test@example.com")
        self.assertEqual(args[1], "my_username")
        email_token = args[2]

        # 3A. Send the request to update the password
        response = self.client.post(
            "/api/update-password/",
            content_type="application/json",
            data=json.dumps({"email-token": email_token, "password": "123"}),
        )

        self.assertEqual(response.status_code, 400)

        # 3B. Send the request to update the password
        response = self.client.post(
            "/api/update-password/",
            content_type="application/json",
            data=json.dumps({"email-token": email_token, "password": "@_new_Pa$w0rd"}),
        )

        self.assertEqual(response.status_code, 200)

        # Now we should not be able to login with the old password
        response = self.client.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_username",
                    "password": "A_Pas$word123",
                }
            ),
        )

        self.assertEqual(response.status_code, 400)

        # But the new password should work
        response = self.client.post(
            "/api/login/",
            content_type="application/json",
            data=json.dumps(
                {
                    "username": "my_username",
                    "password": "@_new_Pa$w0rd",
                }
            ),
        )

        self.assertEqual(response.status_code, 200)
