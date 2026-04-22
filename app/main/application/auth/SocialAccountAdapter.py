from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.isConfirmed = True
        user.save(update_fields=["isConfirmed"])
        return user

    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)
        if sociallogin.is_existing:
            user = sociallogin.user
            if not user.isConfirmed:
                user.isConfirmed = True
                user.save(update_fields=["isConfirmed"])
