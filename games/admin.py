from django.contrib import admin

from .models import Game, Tournament

admin.site.register([Game, Tournament])
