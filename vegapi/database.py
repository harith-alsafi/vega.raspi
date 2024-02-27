from peewee import Model, SqliteDatabase, CharField

database = SqliteDatabase('vega.db')

class DataSeries: 
    name: str
    x: str
    y: str
    period: str

    def __init__(self, name, x, y, period):
        self.name = name
        self.x = x
        self.y = y
        self.period = period
    
    def to_json(self):
        return {
            "name": self.deviceName,
            "x": self.time,
            "y": self.value,
        }


class BaseModel(Model):
    class Meta:
        database = database

class DataSeriesModel(BaseModel, DataSeries): 
    def __init__(self):
        super().__init__()

def init_db():
    database.connect()
    database.create_tables([DataSeriesModel])
