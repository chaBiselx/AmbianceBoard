from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        email = sociallogin.account.extra_data.get("email")
        print("=== Google OAuth extra_data ===")
        print(sociallogin.account.extra_data)
        if email:
            user.email = email
        user.isConfirmed = True
        user.save(update_fields=["isConfirmed", "email"])
        return user

    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)
        if sociallogin.is_existing:
            user = sociallogin.user
            email = sociallogin.account.extra_data.get("email")
            updated_fields = []
            if not user.isConfirmed:
                user.isConfirmed = True
                updated_fields.append("isConfirmed")
            if email and user.email != email:
                user.email = email
                updated_fields.append("email")
            if updated_fields:
                user.save(update_fields=updated_fields)
