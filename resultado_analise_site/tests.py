import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from .models import ResultadoAnaliseSite
from .serializers import ResultadoAnaliseSiteSerializer


# inicializa o aplicativo APIClient
client = Client()


class GetAllResultadoAnaliseSiteTest(TestCase):
    def setUp(self):
        ResultadoAnaliseSite.objects.create(
            url='google', violacao='violacao', nodes='nodes')
        ResultadoAnaliseSite.objects.create(
            url='instagram', violacao='campo3', nodes='campo4')
        ResultadoAnaliseSite.objects.create(
            url='twitch', violacao='campo5', nodes='campo6')
        ResultadoAnaliseSite.objects.create(
            url='banco do brasil', violacao='campo7', nodes='campo8')

    def test_recebe_todos_ras(self):
        response = client.get(reverse('get_post_resultado_analise_site'))

        ras = ResultadoAnaliseSite.objects.all()
        serializer = ResultadoAnaliseSiteSerializer(ras, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleResultadoAnaliseSiteTest(TestCase):
    def setUp(self):
        self.google = ResultadoAnaliseSite.objects.create(
            url='google', violacao='violacao', nodes='nodes')
        self.insta = ResultadoAnaliseSite.objects.create(
            url='instagram', violacao='campo3', nodes='campo4')
        self.twitch = ResultadoAnaliseSite.objects.create(
            url='twitch', violacao='campo5', nodes='campo6')
        self.bb = ResultadoAnaliseSite.objects.create(
            url='banco do brasil', violacao='campo7', nodes='campo8')
        
    def test_recebe_um_ras_valido(self):
        response = client.get(
            reverse('get_delete_update_resultado_analise_site',
                    kwargs={'url': self.twitch.url, 'violacao': self.twitch.violacao}))
        
        ras = ResultadoAnaliseSite.objects.get(pk=self.twitch.pk)
        serializer = ResultadoAnaliseSiteSerializer(ras)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_recebe_um_ras_invalido(self):
        response = client.get(
            reverse('get_delete_update_resultado_analise_site',
                    kwargs={'url': 30, 'violacao': 40}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostResultadoAnaliseSiteTest(TestCase):
    def setUp(self):
        self.dados_validos = {
            'url': 'banco do brasil',
            'violacao': 'violacao',
            'nodes': 'nodes'
        }

        self.dados_invalidos = {
            'url': '',
            'violacao': 'campo3',
            'nodes': 'campo4'
        }

    def test_insere_ras_valido(self):
        response = client.post(
            reverse('get_post_resultado_analise_site'),
            data=json.dumps(self.dados_validos),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_insere_ras_invalido(self):
        response = client.post(
            reverse('get_post_resultado_analise_site'),
            data=json.dumps(self.dados_invalidos),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateResultadoAnaliseSiteTest(TestCase):
    def setUp(self):
        self.google = ResultadoAnaliseSite.objects.create(
            url='google', violacao='violacao', nodes='nodes')
        self.bb = ResultadoAnaliseSite.objects.create(
            url='banco do brasil', violacao='campo3', nodes='campo4')
        
        self.dados_validos = {
            'url': 'google',
            'violacao': 'campo5',
            'nodes': 'campo6'
        }
        self.dados_invalidos = {
            'url': '',
            'violacao': 'campo7',
            'nodes': 'campo8'
        }
        
    
    def test_atualizacao_valida(self):
        response = client.put(
            reverse('get_delete_update_resultado_analise_site',
                    kwargs={'url': self.google.url, 'violacao': self.google.violacao}),
                    data=json.dumps(self.dados_validos),
                    content_type='application/json'
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_atualizacao_invalida(self):
        response = client.put(
            reverse('get_delete_update_resultado_analise_site',
                    kwargs={'url': self.google.url, 'violacao': self.google.violacao}),
                    data=json.dumps(self.dados_invalidos),
                    content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteResultadoAnaliseSiteTest(TestCase):
    def setUp(self):
        self.google = ResultadoAnaliseSite.objects.create(
            url='google', violacao='violacao', nodes='nodes')
        self.bb = ResultadoAnaliseSite.objects.create(
            url='banco do brasil', violacao='campo3', nodes='campo4')
    
    def test_apaga_valido(self):
        response = client.delete(
            reverse('get_delete_update_resultado_analise_site',
                    kwargs={'url': self.google.url, 'violacao': self.google.violacao}))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_apaga_invalido(self):
        response = client.delete(
            reverse('get_delete_update_resultado_analise_site',
                    kwargs={'url': 30, 'violacao': 40}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        