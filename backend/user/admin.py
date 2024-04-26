from django.contrib import admin
from .models import CustomUser, WhitelistData, UserPreferences, OtpCode

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(WhitelistData)
admin.site.register(UserPreferences)
admin.site.register(OtpCode)

