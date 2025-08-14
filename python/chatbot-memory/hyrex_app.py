from hyrex import HyrexApp

from tasks import hy as registry

app = HyrexApp("hyrex-chatbot")

app.add_registry(registry)
