from rest_framework.throttling import UserRateThrottle

class SimpleRateThrottle(UserRateThrottle):
    scope = "simple"