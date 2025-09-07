from datetime import datetime

from hamcrest import (
    assert_that,
    has_property,
    starts_with,
    all_of,
    contains_inanyorder,
    not_none,
    contains_string,
    ends_with,
)

from checkers.http_checkers import check_status_code_http
from assertpy import (
    assert_that,
    soft_assertions,
)

from dm_api_account.models.user_details_envelope import UserRole


def test_get_v1_account_auth(
        auth_account_helper
):
    response = auth_account_helper.dm_account_api.account_api.get_v1_account()
    print(response)
    with soft_assertions():
        assert_that(response.resource.login).is_equal_to('vfrenkel_test10')
        assert_that(response.resource.roles).contains(UserRole.GUEST, UserRole.PLAYER)
    # assert_that(
    #     response,
    #     all_of(
    #         has_property('resource', has_property('login', starts_with("vfrenkel"))),
    #         has_property('resource', has_property("login", all_of(not_none(), ends_with("10")))),
    #         has_property('resource', has_property("roles", contains_inanyorder("Guest", "Player"))),
    #         has_property('resource', has_property("online", all_of(contains_string("T"), ends_with("+00:00"))))
    #     )
    # )


def test_get_v1_account_no_auth(
        account_helper
):
    with check_status_code_http(401, 'User must be authenticated'):
        account_helper.dm_account_api.account_api.get_v1_account()
