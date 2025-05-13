from modules.leds import strip, Color

for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(255, 255, 255))  # Branco
strip.show()
