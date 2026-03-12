import pytest

from checkers.http_checkers import check_status_code_http
from checkers.post_v1_account import PostV1Account


def test_post_v1_account(
        account_helper,
        prepare_user
):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    response = account_helper.user_login(login=login, password=password, validate_response=True)
    PostV1Account.check_response_values(response)


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        (
                {
                    "login": "valid_user",
                    "email": "user@example.com",
                    "password": "123"
                },
                "Validation failed"
        ),
        (
                {
                    "login": "valid_user",
                    "email": "userexample.com",
                    "password": "123456"
                },
                "Validation failed"
        ),
        (
                {
                    "login": "a",
                    "email": "user@example.com",
                    "password": "123456"
                },
                "Validation failed"
        ),
    ]
)
def test_post_v1_account_wrong_credentials(
        account_helper,
        payload,
        expected_error,
):
    with check_status_code_http(400, expected_error):
        account_helper.register_new_user(login=payload['login'], password=payload['password'], email=payload['email'])
