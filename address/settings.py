from django.conf import settings

# Some counties doesn't have "state" value so google return locality but not no state
# Set this to true and it will create dummy state
ALLOW_UNKNOWN_STATES = getattr(settings, 'ALLOW_UNKNOWN_STATES', False)

# Set this to false so only valid address is saved, allowing dummy addresses means
# accepting Address with only `raw` value is filled
ALLOW_DUMMY_ADDRESSES = getattr(settings, 'ALLOW_UNKNOWN_STATES', True)
