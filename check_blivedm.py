import blivedm
import inspect

print("blivedm location:", blivedm.__file__)
print("Attributes in blivedm:", dir(blivedm))

try:
    import blivedm.models.web as web_models
    print("Attributes in blivedm.models.web:", dir(web_models))
except ImportError:
    print("Could not import blivedm.models.web")
