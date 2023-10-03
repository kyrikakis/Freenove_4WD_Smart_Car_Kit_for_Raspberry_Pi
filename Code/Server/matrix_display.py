import board
import busio
from adafruit_ht16k33 import matrix

class CustomLEDMatrixController:
    def __init__(self, i2c_address=0x71):
        # Initialize I2C bus and HT16K33 LED matrix with the specified address
        i2c = busio.I2C(board.SCL, board.SDA)
        self.matrix = matrix.Matrix16x8(i2c, address=i2c_address)

    def fill_display(self, data):
        """
        Fill the display with data (16x8 list of True/False values).
        """
        for row in range(8):
            for col in range(16):
                # Invert rows and columns here
                self.matrix[col, row] = data[row][col % 8]

    def clear_display(self):
        """
        Clear the display (turn off all LEDs).
        """
        self.fill_display([[False] * 16 for _ in range(8)])

    def show_display(self):
        """
        Update the physical display with the current data.
        """
        self.matrix.show()
    
