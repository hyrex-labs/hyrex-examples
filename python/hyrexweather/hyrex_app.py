from main import hy as main_registry
from hyrex import HyrexApp

app = HyrexApp("HyrexWeather")

app.add_registry(main_registry)