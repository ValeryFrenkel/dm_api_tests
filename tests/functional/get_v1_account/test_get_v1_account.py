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


def test_get_v1_account_auth(

        auth_account_helper
):
    response = auth_account_helper.dm_account_api.account_api.get_v1_account()
    print(response)
    assert_that(
        response,
        all_of(
            has_property('resource', has_property('login', starts_with("vfrenkel"))),
            has_property('resource', has_property("login", all_of(not_none(), ends_with("10")))),
            has_property('resource', has_property("roles", contains_inanyorder("Guest", "Player"))),
            has_property('resource', has_property("online", all_of(contains_string("T"), ends_with("+00:00"))))
        )
    )

    def test_get_v1_account_no_auth(
            account_helper
    ):
        account_helper.dm_account_api.account_api.get_v1_account()
