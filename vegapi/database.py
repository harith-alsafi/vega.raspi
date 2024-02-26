from peewee import Model, SqliteDatabase, CharField

database = SqliteDatabase('vega.db')

class BaseModel(Model):
    class Meta:
        database = database

class DataSeries(BaseModel): 
    componentName: CharField
    time: CharField
    value: CharField
    period: CharField

    def __init__(self, componentName):
        self.componentName = componentName

class VegaDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        
