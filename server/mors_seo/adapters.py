from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_username, user_field


class UserAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        """Saves a new `User` instance using information provided in the signup form."""
        data = form.cleaned_data
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        user_email(user, data.get('email'))
        user_username(user, data.get('username'))
        user_field(user, 'seo_result', [])

        if first_name:
            user_field(user, 'first_name', first_name)
        if last_name:
            user_field(user, 'last_name', last_name)
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)

        if commit:
            user.save()
        return user
