from assertpy import (
    soft_assertions,
    assert_that,
)

from dm_api_account.models.user_details_envelope import UserRole


class GetV1Account:

    @classmethod
    def check_response_values(
            cls,
            response
    ):
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