from typing import Callable, List
from peewee import Model, SqliteDatabase, CharField, IntegerField
from threading import Thread
import time
import signal

database = SqliteDatabase('vega.db')

class BaseModel(Model):
    class Meta:
        database = database

class DataSeriesModel(BaseModel): 
    name = CharField()
    x = IntegerField()
    y = CharField()
    period = CharField()

    def to_json(self):
        return {
            "name": self.name.__str__(),
            "x": self.x.__str__(),
            "y": self.y.__str__(),
            "period": self.period.__str__()
        }

class PeriodicData:
    name: str
    y: str

    def __init__(self, name: str, y: str):
        self.name = name
        self.y = y

class SinglePlot(PeriodicData):
    x: int
    period: str

    def __init__(self, name: str, x: int, y: str, period: str):
        super().__init__(name, y)
        self.x = x
        self.period = period

    def to_json(self):
        return {
            "name": self.name,
            "x": self.x.__str__(),
            "y": self.y,
            "period": self.period
        }

class DataSeries: 
    name: str
    data: List[SinglePlot]

    def __init__(self, name: str, data: List[SinglePlot]):
        self.name = name
        self.data = data
    
    def to_json(self):
        return {
            "name": self.name,
            "data": [d.to_json() for d in self.data]
        }

class DataPlot:
    title: str
    x_label: str
    y_label: str
    data: List[DataSeries]

    def __init__(self, title: str, x_label: str, y_label: str, data: List[DataSeries]):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.data = data

    def to_json(self):
        return {
            "title": self.title,
            "xLabel": self.x_label,
            "yLabel": self.y_label,
            "data": [d.to_json() for d in self.data]
        }

def init_db():
    database.connect()
    database.create_tables([DataSeriesModel])

class Database:
    time: int # in seconds
    period: int # in seconds
    onEveryPeriod: Callable[[], List[PeriodicData]]
    thread: Thread
    is_running: bool = False

    def __init__(self, onEveryPeriod: Callable[[], List[PeriodicData]], period: int = 2):
        init_db()
        self.database = database
        self.period = period
        self.onEveryPeriod = onEveryPeriod
        self.is_running = False
        self.thread = Thread(target=self.periodic_polling)
        self.thread.setDaemon(True)
        self.time = 0

    def periodic_polling(self):
        while self.is_running:
            data = self.onEveryPeriod()
            self.add_data_batch(data)
            time.sleep(self.period)

    def start_recording(self):
        self.is_running = True
        def signal_handler(sig, frame):
            print("Ctrl+C pressed. Stopping the database...")
            print("Database stopped.")
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        self.thread.start()

    def stop_recording(self):
        self.is_running = False
        self.thread.join()

    def add_data_batch(self, data: List[PeriodicData]):
        x = str(self.time)
        self.time += self.period
        for record in data:
            DataSeriesModel.create(name=record.name, x=x, y=record.y, period=self.period.__str__())

    def add_data_series(self, name: str, y: str):
        x = str(self.time)
        self.time += self.period
        DataSeriesModel.create(name=name, x=x, y=y, period=self.period.__str__())

    def get_data_series(self, name: str) -> List[SinglePlot]:
        return list(DataSeriesModel.select().where(DataSeriesModel.name == name).execute())

    def get_data_series_by_period(self, name: str, period: str) -> List[SinglePlot]:
        return list(DataSeriesModel.select().where(DataSeriesModel.name == name and DataSeriesModel.period == period).execute())
    
    def get_data_series_last_n(self, name: str, n: int) -> List[SinglePlot]:
        data = DataSeriesModel.select().where(DataSeriesModel.name == name).order_by(DataSeriesModel.x.desc()).limit(n).execute()
        results: List[DataSeriesModel] = list(data)
        sorted_results = sorted(results, key=lambda x: x.x)
        return sorted_results
    
    def get_all_data_series_by_seconds(self, name:str, seconds: int) -> List[SinglePlot]:
        return self.get_data_series_last_n(name, seconds // self.period)

    def get_all_data_series(self) -> List[SinglePlot]:
        return list(DataSeriesModel.select().execute())

    def delete_all_data_series(self):
        self.time = 0
        DataSeriesModel.delete().execute()

    def delete_last_n_data_series(self, n: int):
        DataSeriesModel.delete().limit(n)

    def close(self):
        self.database.close()
