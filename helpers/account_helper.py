import time
from http.client import responses
from json import loads

from dm_api_account.models.change_email import ChangeEmail
from dm_api_account.models.change_password import ChangePassword
from dm_api_account.models.login_credentials import LoginCredentials
from dm_api_account.models.registration import Registration
from dm_api_account.models.reset_password import ResetPassword
from services.dm_api_account import DMApiAccount
from services.api_mailhog import MailHogApi
from retrying import retry


def retry_if_result_none(
        result
):
    return result is None


class AccountHelper:
    def __init__(
            self,
            dm_account_api: DMApiAccount,
            mailhog: MailHogApi
    ):
        self.dm_account_api = dm_account_api
        self.mailhog = mailhog

    def auth_client(
            self,
            login: str,
            password: str
    ):
        response = self.user_login(login=login, password=password)
        auth_token = {
            "x-dm-auth-token": response.headers["x-dm-auth-token"]
        }
        self.dm_account_api.account_api.set_headers(auth_token)
        self.dm_account_api.login_api.set_headers(auth_token)
        print(auth_token)

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def register_new_user(
            self,
            login: str,
            password: str,
            email: str
    ):
        registration = Registration(
            login=login,
            email=email,
            password=password
        )

        response = self.dm_account_api.account_api.post_v1_account(registration=registration)
        assert response.status_code == 201, f"Пользователь не был создан {response.json()}"
        start_time = time.time()
        token = self.get_activation_token_by_login(login=login)
        end_time = time.time()
        assert end_time - start_time < 3, "Время ожидания активации превышено"
        assert token is not None, f"Токен для пользователя {login}, не был получен "
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)
        return response

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def user_login(
            self,
            login: str,
            password: str,
            remember_me: bool = True,
            validate_response=False
    ):
        login_credentials = LoginCredentials(
            login=login,
            password=password,
            remember_me=remember_me
        )
        response = self.dm_account_api.login_api.post_v1_account_login(
            login_credentials=login_credentials, validate_response=validate_response
        )
        assert response.headers["x-dm-auth-token"], "Токен для пользователя не был получен"
        assert response.status_code == 200, "Пользователь не смог авторизоваться"
        return response

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def change_email(
            self,
            login: str,
            password: str,
            email: str
    ):
        change_email = ChangeEmail(
            login=login,
            password=password,
            email=email,
        )
        response = self.dm_account_api.account_api.put_v1_account_email(change_email=change_email)
        assert response.status_code == 200, "Почта не была изменена"
        token = self.get_activation_token_by_login(login=login)
        assert token is not None, f"Токен для пользователя {login}, не был получен "
        response = self.dm_account_api.account_api.put_v1_account_token(token=token)

    def change_password(
            self,
            login: str,
            email: str,
            old_password: str,
            new_password: str,
    ):
        response = self.dm_account_api.account_api.post_v1_account_password(
            reset_password=ResetPassword(
                login=login,
                email=email
            )
        )
        assert response.status_code == 200, "Пароль не был сброшен"
        token = self.get_password_token_by_login(login=login)
        assert token is not None, f"Токен для пользователя {login}, не был получен "
        response = self.dm_account_api.account_api.put_v1_account_password(
            change_password=ChangePassword(
                login=login,
                token=token,
                old_password=old_password,
                new_password=new_password
            )
        )
        assert response.status_code == 200, "Пароль не был изменен"

    def logout_current_user(
            self
    ):
        response = self.dm_account_api.login_api.delete_v1_account_login()
        assert response.status_code == 204, "Пользователь не был разлогинен"

    def logout_from_every_device(
            self
    ):
        response = self.dm_account_api.login_api.delete_v1_account_login_all()
        assert response.status_code == 204, "Пользователь не был разлогинен"

    @retry(stop_max_attempt_number=5, retry_on_result=retry_if_result_none, wait_fixed=1000)
    def get_activation_token_by_login(
            self,
            login
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:
            user_data = loads(item['Content']['Body'])
            user_login = user_data['Login']
            if user_login == login:
                token = user_data['ConfirmationLinkUrl'].split('/')[-1]
        return token

    def get_password_token_by_login(
            self,
            login,
    ):
        token = None
        response = self.mailhog.mailhog_api.get_api_v2_messages()
        for item in response.json()['items']:
            user_data = loads(item['Content']['Body'])
            user_login = user_data['Login']
            if user_login == login and 'ConfirmationLinkUri' in user_data:
                token = user_data['ConfirmationLinkUri'].split('/')[-1]
        return token
