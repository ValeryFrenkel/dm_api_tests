from datetime import datetime

from hamcrest import (
    assert_that,
    starts_with,
    has_property,
    all_of,
    has_properties,
    equal_to,
    instance_of,
)


class PostV1Account:

    @classmethod
    def check_response_values(
            cls,
            response
    ):
        login_value = "vfrenkel"
        today = datetime.now().strftime('%Y-%m-%d')
        assert_that(str(response.resource.registration), starts_with(today))
        assert_that(
            response, all_of(
                has_property('resource', has_property('login', starts_with(f"{login_value}"))),
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
