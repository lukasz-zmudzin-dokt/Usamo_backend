from rest_framework.permissions import BasePermission

from account.account_type import AccountType


class IsEmployer(BasePermission):
    """
    Allows access only to employers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.type == AccountType.EMPLOYER.value)


class IsDefaultUser(BasePermission):
    """
    Allows access only to default users.
    """

    def has_permission(self, request, view):
        out = bool(request.user and request.user.type == AccountType.STANDARD.value)
        return out
