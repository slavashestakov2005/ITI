from enum import Enum
from flask_login import current_user, UserMixin

from backend import app


class UserRole:
    pass


class UserRoleGlobal(UserRole, Enum):
    FULL = 1
    CHANGE_ITI = 2
    CHANGE_SUBJECT = 4
    CHANGE_MESSAGE = 8
    CHANGE_SCHOOL = 16
    CHANGE_STUDENT = 32
    CHANGE_USER = 64


class UserRoleIti(UserRole, Enum):
    ADMIN = 1
    SCANNER = 2
    CHANGE_BARCODE = 4


class UserRoleItiSubject(UserRole, Enum):
    ADD_RESULT = 1
    EDIT_RESULT = 2
    EDIT_SCORE = 4
    DELETE_RESULT = 8
    SPLIT_CLASS = 16
    SHARE_RESULT = 32


class UserRoleLogin(UserRole, Enum):
    NO_LOGIN = 1
    LOGIN_LOCAL = 2
    LOGIN_ELJUR = 4


class SiteUser(UserMixin):
    def check_role_global(self, status: UserRoleGlobal) -> bool:
        return False
    
    def check_role_iti(self, iti_id: int, status: UserRoleIti) -> bool:
        return False
    
    def check_role_iti_subject(self, iti_subject_id: int, status: UserRoleItiSubject) -> bool:
        return False
    
    def check_role_login(self, status: UserRoleLogin) -> bool:
        return False


def __check_role(user: SiteUser, role: UserRole, iti_id: int | None, iti_subject_id: int | None) -> bool:
    if type(role) == UserRoleLogin:
        if role == UserRoleLogin.NO_LOGIN:
            return not user.is_authenticated
        return user.check_role_login(role)
    if not user.is_authenticated:
        return False
    if type(role) == UserRoleGlobal:
        return user.check_role_global(role)
    if type(role) == UserRoleIti:
        return iti_id is not None and user.check_role_iti(iti_id, role)
    if type(role) == UserRoleItiSubject:
        is_admin = iti_id is not None and user.check_role_iti(iti_id, UserRoleIti.ADMIN)
        is_subject = iti_subject_id is not None and user.check_role_iti_subject(iti_subject_id, role)
        return is_admin or is_subject
    return False


def check_role(*,  user = None, roles: None | list[UserRole], iti_id: int | None = None, iti_subject_id: int | None = None) -> bool:
    if roles is None:
        roles = []
    cur_user = current_user if user is None else user
    if roles is None or roles == []:
        return True
    if cur_user.is_authenticated and cur_user.check_role_global(UserRoleGlobal.FULL):
        return True
    for role in roles:
        if __check_role(cur_user, role, iti_id, iti_subject_id):
            return True
    return False


@app.context_processor
def jinja_context():
    args = {'check_role': check_role, 'UserRoleGlobal': UserRoleGlobal, 'UserRoleIti': UserRoleIti,
            'UserRoleItiSubject': UserRoleItiSubject, 'UserRoleLogin': UserRoleLogin}
    return args
