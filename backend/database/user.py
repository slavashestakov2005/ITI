from werkzeug.security import check_password_hash, generate_password_hash

from .__db_session import orm, sa, SqlAlchemyBase, Table
from .team import Team
from ..help import check_role, SiteUser, UserRoleGlobal, UserRoleIti, UserRoleItiSubject, UserRoleLogin

class User(SqlAlchemyBase, SiteUser, Table):
    __tablename__ = 'user'
    fields = ['id', 'login', 'password']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    login = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)
    __role_global = orm.relationship("RoleGlobal", uselist=False, lazy='joined')
    __role_iti = orm.relationship("RoleIti", lazy='joined')
    __role_iti_subject = orm.relationship("RoleItiSubject", lazy='joined')

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def __prepare_roles(self) -> None:
        if hasattr(self, 'role_global'):
            return
        if self.__role_global is None:
            self.role_global = 0
        else:
            self.role_global = self.__role_global.role
        if self.__role_iti is None:
            self.role_iti = {}
        else:
            self.role_iti = {role.iti_id: role.role for role in self.__role_iti}
        if self.__role_iti_subject is None:
            self.role_iti_subject = {}
        else:
            self.role_iti_subject = {role.iti_subject_id: role.role for role in self.__role_iti_subject}

    def check_role_global(self, status: UserRoleGlobal) -> bool:
        self.__prepare_roles()
        return self.role_global & status.value == status.value

    def check_role_iti(self, iti_id: int, status: UserRoleIti) -> bool:
        self.__prepare_roles()
        return iti_id in self.role_iti and self.role_iti[iti_id] & status.value == status.value

    def check_role_iti_subject(self, iti_subject_id: int, status: UserRoleItiSubject) -> bool:
        self.__prepare_roles()
        return iti_subject_id in self.role_iti_subject and self.role_iti_subject[iti_subject_id] & status.value == status.value
    
    def check_role_login(self, status: UserRoleLogin) -> bool:
        return status == UserRoleLogin.LOGIN_LOCAL

    def roles_global_str(self) -> str:
        roles = []
        for role in UserRoleGlobal:
            if self.check_role_global(role):
                roles.append(role.name)
        return ', '.join(roles)

    def roles_iti_str(self, iti_id: int) -> str:
        roles = []
        for role in UserRoleIti:
            if self.check_role_iti(iti_id, role):
                roles.append(role.name)
        return ', '.join(roles)

    def roles_iti_subject_str(self, iti_subjects: dict[int, str]) -> str:
        subjects = []
        for ys_id, subject in iti_subjects.items():
            if ys_id in self.role_iti_subject:
                roles = []
                for role in UserRoleItiSubject:
                    if self.check_role_iti_subject(ys_id, role):
                        roles.append(role.name)
                subjects.append('{0} [{1}]'.format(subject.name, ', '.join(roles)))
        return '; '.join(subjects)

    def teams_list(self, year: int):
        is_adm = check_role(user=self, roles=[UserRoleIti.ADMIN], iti_id=year)
        return [_.id for _ in Team.select_by_iti(year)] if is_adm else []

    # Table

    @classmethod
    def select_by_login(cls, login: str):
        return cls.__select_by_expr__(cls.login == login, one=True)

    @classmethod
    def update_by_login(cls, user) -> None:
        return cls.__update_by_expr__(user, cls.login == user.login)
