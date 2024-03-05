from vegapi.database import DataSeries, Database
import random

def onEveryPeriod() -> list[DataSeries]:
    return [
        DataSeries(name="device1", y=str(random.randint(0, 2))),
        DataSeries(name="device2",  y=str(random.randint(1, 3))),
        DataSeries(name="device3", y=str(random.randint(2, 4))),
    ]

database = Database(onEveryPeriod=onEveryPeriod, period=2)
database.delete_all_data_series()
database.start_recording()

while True:
    pass
# database.add_data_series("device1", "0", "1")
# database.add_data_series("device2", "0", "1")

# database.add_data_series("device1", "2", "3")
# database.add_data_series("device2", "2", "3")

# database.add_data_series("device1", "4", "0.4")
# database.add_data_series("device2", "4", "0.4")

data = database.get_data_series_last_n(name="device1", n=2)
for record in data:
    print(record.name, record.x, record.y, record.period)
