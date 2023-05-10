from .__db_session import sa, SqlAlchemyBase, Table


class Subject(SqlAlchemyBase, Table):
    __tablename__ = 'subject'
    fields = ['id', 'name', 'short_name', 'type', 'diploma', 'msg']

    id = sa.Column(sa.Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
    short_name = sa.Column(sa.String, nullable=False)
    type = sa.Column(sa.String, nullable=False)
    diploma = sa.Column(sa.String, nullable=False)
    msg = sa.Column(sa.String, nullable=False)

    def type_str(self):
        if self.type == 'i':
            return 'individual'
        elif self.type == 'g':
            return 'group'
        return 'team'

    def diplomas_br(self):
        return self.diploma.replace('\n', '<br>')

    def msg_br(self):
        return self.msg.replace('\n', '<br>')

    # Table
    @classmethod
    def default_init(cls):
        cls.insert(cls.build(None, 'Командный тур', 'Команд.', 'a', 'в командном туре', 'командного тура'))
        cls.insert(cls.build(None, 'История', 'Ист.', 'i', 'в индивидуальном туре\nпо истории', 'по истории'))
        cls.insert(cls.build(None, 'Английский язык', 'Анг.', 'i', 'в индивидуальном туре\nпо английскому языку', 'по английскому языку'))
        cls.insert(cls.build(None, 'Русский язык', 'Рус.', 'i', 'в индивидуальном туре\nпо русскому языку', 'по русскому языку'))
        cls.insert(cls.build(None, 'Информатика', 'Инф.', 'i', 'в индивидуальном туре\nпо информатике', 'по информатике'))
        cls.insert(cls.build(None, 'ИЦН', 'ИЦН', 'i', 'в индивидуальном туре\nпо ИЦН', 'по ИЦН'))
        cls.insert(cls.build(None, 'Математика', 'Мат.', 'i', 'в индивидуальном туре\nпо математике', 'по математике'))
        cls.insert(cls.build(None, 'Обществознание', 'Общ.', 'i', 'в индивидуальном туре\nпо обществознанию', 'по обществознанию'))
        cls.insert(cls.build(None, 'Естествознание', 'Ест.', 'i', 'в индивидуальном туре\nпо естествознанию', 'по естествознанию'))
        cls.insert(cls.build(None, 'Литература', 'Лит.', 'i', 'в индивидуальном туре\nпо литературе', 'по литературе'))
        cls.insert(cls.build(None, 'Искусство', 'Иск.', 'i', 'в индивидуальном туре\nпо искусству', 'по искусству'))
        cls.insert(cls.build(None, 'Карусель', 'Карус.', 'g', 'в карусели', 'карусели'))
        cls.insert(cls.build(None, 'Естественно-научные бои', 'Е-н. бои', 'g', 'в естественно-научных боях', 'ествественно-научных боёв'))
        cls.insert(cls.build(None, 'Коммуникативные бои', 'Ком. бои', 'g', 'в коммуникативных боях', 'коммуникативных боёв'))
        cls.insert(cls.build(None, ' Литература', 'Пар. лит.', 'g', 'в групповом туре\nпо литературе', 'по литературе (групповой тур)'))
        cls.insert(cls.build(None, ' Английский язык', 'Пар. анг.', 'g', 'в групповом туре\nпо английскому языку', 'по английскому языку (групповой тур)'))
        cls.insert(cls.build(None, 'Театр', 'Театр', 'g', 'в театре', 'театра'))
        cls.insert(cls.build(None, 'Конструкторская задача', 'Констр.', 'g', 'в конструкторской задаче', 'конструкторской задачи'))
        cls.insert(cls.build(None, ' Информатика', 'Пар. инф.', 'g', 'в групповом туре\nпо информатике', 'по информатике (групповой тур)'))
        cls.insert(cls.build(None, 'Окружающий мир', 'Окр. мир', 'i', 'в индивидуальном туре\nпо окружающему миру', 'по окружающему миру'))
        cls.insert(cls.build(None, 'Искусство 5-6', 'Иск.', 'i', 'в индивидуальном туре\nпо искусству', 'по искусству среди 5-6 классов'))
        cls.insert(cls.build(None, 'Искусство 7-9', 'Иск.', 'i', 'в индивидуальном туре\nпо искусству', 'по искусству среди 7-9 классов'))
        cls.insert(cls.build(None, 'Настольные игры', 'Наст.', 'g', 'в настольных играх', 'настольных игр'))
        cls.insert(cls.build(None, 'Бонус', 'Бонус', 'g', 'бонусном туре', 'выставления бонусных баллов за публичную защиту'))
        cls.insert(cls.build(None, '«Зри в корень»', '«Зри...»', 'g', 'в групповом туре\n«Зри в корень»', 'игры «Зри в корень»'))

    @classmethod
    def select_by_name(cls, name: str):
        return cls.__select_by_expr__(cls.name == name, one=True)
