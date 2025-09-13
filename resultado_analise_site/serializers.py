from rest_framework import serializers
from .models import ResultadoAnaliseSite

class ResultadoAnaliseSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoAnaliseSite
        fields = ('url', 'violacao', 'nodes')