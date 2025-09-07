from datetime import datetime

import pytest
from hamcrest import (
    assert_that,
    has_property,
    starts_with,
    all_of,
    instance_of,
    has_properties,
    equal_to,
)

from checkers.http_checkers import check_status_code_http


def test_post_v1_account(
        account_helper,
        prepare_user
):
    login = prepare_user.login
    password = prepare_user.password
    email = prepare_user.email
    account_helper.register_new_user(login=login, password=password, email=email)
    response = account_helper.user_login(login=login, password=password, validate_response=True)
    assert_that(
        response, all_of(
            has_property('resource', has_property('login', starts_with("vfrenkel"))),
            has_property('resource', has_property('registration', instance_of(datetime))),
            has_property(
                'resource', has_properties(
                    {
                        'rating': has_properties(
                            {
                                "enabled": equal_to(True),
                                "quality": equal_to(0),
                                "quantity": equal_to(0)
                            }
                        )
                    }
                )
            )
        )
    )
    print(response)


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
        account_helper.register_new_user(login=payload['login'],password=payload['password'], email=payload['email'])
