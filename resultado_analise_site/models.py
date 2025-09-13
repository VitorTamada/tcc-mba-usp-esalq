from django.db import models


class CriterioWCAG(models.Model):
   criterio = models.CharField(max_length=255, blank=False, unique=True)
   prioridade = models.CharField(max_length=3, blank=False)


   def __repr__(self):
      return self.criterio


class SiteCategoria(models.Model):
   index = models.IntegerField(blank=False, default=0, null=False, unique=True)
   categoria = models.CharField(max_length=255, blank=False, primary_key=True, unique=True)


   def __repr__(self):
      return self.categoria


class SiteAnalisado(models.Model):
   url = models.CharField(max_length=255, blank=False, primary_key=True, unique=True)
   categoria = models.ForeignKey(SiteCategoria, on_delete=models.SET_NULL, null=True)


   def __repr__(self):
      return self.url


class TipoDeficiencia(models.Model):
   index = models.IntegerField(blank=False, default=0, null=False, unique=True)
   deficiencia = models.CharField(max_length=255, blank=False, primary_key=True, unique=True)


   def __repr__(self):
      return self.deficiencia


class AxeCoreViolacoes(models.Model):
   index = models.IntegerField(blank=False, default=0, null=False, unique=True)
   violacao = models.CharField(max_length=255, blank=False, primary_key=True, unique=True)
   impact = models.CharField(max_length=255, default='impact')
   description = models.CharField(max_length=255, default='description')


   def __repr__(self):
      return self.violacao


class ResultadoAnaliseSite(models.Model):
   pk = models.CompositePrimaryKey("url", "violacao")
   url = models.ForeignKey(SiteAnalisado, on_delete=models.CASCADE)
   violacao = models.ForeignKey(AxeCoreViolacoes, on_delete=models.CASCADE)
   incomplete = models.BooleanField(default=False, blank=False, null=False)


   def __repr__(self):
      return str(self.pk)


class ViolacaoTipoDeficiencia(models.Model):
   # Vincula uma violação aos tipos de deficiência afetados
   pk = models.CompositePrimaryKey("violacao", "deficiencia")
   violacao = models.ForeignKey(AxeCoreViolacoes, on_delete=models.CASCADE)
   deficiencia = models.ForeignKey(TipoDeficiencia, on_delete=models.CASCADE)
   exist = models.BooleanField(default=False, blank=False, null=False)


   def __repr__(self):
      return str(self.pk)


class ViolacaoCriterioWCAG(models.Model):
   pk = models.CompositePrimaryKey("criterio", "violacao")
   violacao = models.ForeignKey(AxeCoreViolacoes, on_delete=models.CASCADE)
   criterio = models.ForeignKey(CriterioWCAG, on_delete=models.CASCADE)
   exist = models.BooleanField(default=False, blank=False, null=False)


   def __repr__(self):
      return str(self.pk)