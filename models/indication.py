class Indication():
    """Класс описывающий показание датчика
    dt - дата и время показания
    value -значение
    status -статус показание(признак достоверности)
    """
#     конструктор: время, показание, признак достоверности
  
    def __init__(self, dt, value, status):
        self.dt = dt
        self.value = value
        self.status = status
    def __repr__(self):
        return '{}; {}; {}'.format(self.dt, self.value, self.status)
    def __lt__(self, other):
        """сравнение 2 значений"""
        return self.dt<other.dt