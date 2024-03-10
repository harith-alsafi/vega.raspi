import Adafruit_CharLCD as LCD
from time import sleep

# Define LCD pin numbers
LCD_RS = 25
LCD_EN = 24
LCD_D4 = 23
LCD_D5 = 17
LCD_D6 = 18
LCD_D7 = 22
LCD_COLUMNS = 16
LCD_ROWS = 2

# Create LCD object
lcd = LCD.Adafruit_CharLCD(
    LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7,
    LCD_COLUMNS, LCD_ROWS
)

try:
    while True:
        lcd.clear()
        lcd.message("Hello, World!\nI2C LCD on RPi")
        sleep(2)
except KeyboardInterrupt:
    pass
finally:
    lcd.clear()
