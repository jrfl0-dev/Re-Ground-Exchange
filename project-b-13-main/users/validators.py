from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class NoReusePasswordValidator:
    def validate(self, password, user=None):
        if user and user.has_usable_password() and user.check_password(password):
            raise ValidationError(
                _("Your new password cannot be the same as your current password."),
                code="password_no_reuse",
            )

    def get_help_text(self):
        return _("Your new password cannot be the same as your current password.")
