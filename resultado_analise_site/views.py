import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from colour import Color
import matplotlib.pyplot as plt
import seaborn as sns

from django.db.models import Max
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import ResultadoAnaliseSiteSerializer

from .forms import *

from .analise_axe_core import analisa_site

@api_view(['GET', 'DELETE', 'PUT'])
def get_delete_update_resultado_analise_site(request, url, violacao):
    try:
        resultado_analise_site = ResultadoAnaliseSite.objects.get(pk=(url, violacao))
    except ResultadoAnaliseSite.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Pega detalhes do resultado da análise de um site
    if request.method == 'GET':
        serializer = ResultadoAnaliseSiteSerializer(resultado_analise_site)
        return Response(serializer.data)
    # Apaga os resultados da análise de um site
    elif request.method == 'DELETE':
        resultado_analise_site.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # Atualiza os resultados da análise de um site
    elif request.method == 'PUT':
        serializer = ResultadoAnaliseSiteSerializer(resultado_analise_site, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def get_post_resultado_analise_site(request):
    # Pega o resultado da análise de todos os sites
    if request.method == 'GET':
        ras = ResultadoAnaliseSite.objects.all()
        serializer = ResultadoAnaliseSiteSerializer(ras, many=True)
        return Response(serializer.data)
    # Insere os resultados da análise de um novo site
    elif request.method == 'POST':
        data = {
            'url': request.data.get('url'),
            'violacao': request.data.get('violacao')
        }
        serializer = ResultadoAnaliseSiteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------


def get_pagina_inicial(request):
    return HttpResponseRedirect("/todos_resultados_analise_site/")

# Função auxiliar
def get_todos_dados(revisao_manual=False):
    todos_sa = SiteAnalisado.objects.all().values()
    #todos_acv = AxeCoreViolacoes.objects.all().values()
    todos_ras = {}

    todos_acv = set()
    for sa in todos_sa:
        ras = [ras['violacao_id'] for ras in ResultadoAnaliseSite.objects.filter(url=sa['url'], incomplete=revisao_manual).values()]
        todos_ras[sa['url']] = ras
        for ras in ResultadoAnaliseSite.objects.filter(url=sa['url'], incomplete=revisao_manual):
            todos_acv.add(ras.violacao)

    site_mais_violacao = []
    maior_numero_violacoes = -1
    for k, v in todos_ras.items():
        if len(v) >= maior_numero_violacoes:
            if len(v) >= maior_numero_violacoes:
                site_mais_violacao = []
            site_mais_violacao.append(k)
            maior_numero_violacoes = len(v)

    numero_ocorrencias_violacao = {}
    for k, v in todos_ras.items():
        for violacao in v:
            if not violacao in numero_ocorrencias_violacao.keys():
                numero_ocorrencias_violacao[violacao] = 1
            else:
                numero_ocorrencias_violacao[violacao] += 1

    # Ordena por ordem decrescente de ocorrências da violação
    numero_ocorrencias_violacao = dict(sorted(numero_ocorrencias_violacao.items(), key=lambda item: item[1], reverse=True))

    return todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao


def get_todos_resultados_analise_site(request):
    if request.method == 'POST':
        if 'analisar' in request.POST and request.POST['analisar'] == 'Analisar':
            form = ResultadoAnaliseSiteForm(request.POST)
            if form.is_valid():
                analisa_site(form.cleaned_data)
        elif 'delete' in request.POST and request.POST['delete'] == 'Delete':
            try:
                site_a_ser_apagado = SiteAnalisado.objects.get(url=request.POST['k'])
                site_a_ser_apagado.delete()

                for acv in AxeCoreViolacoes.objects.all():
                    ras_restantes = ResultadoAnaliseSite.objects.filter(violacao=acv.violacao)
                    if not ras_restantes:
                        acv.delete()
            except:
                print("Não foi possível apagar o site")

    form = ResultadoAnaliseSiteForm()

    todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao = get_todos_dados()

    todos_ras = {}
    for sa in todos_sa:
        ras_aux = []
        vcw_aux = set()
        for ras in ResultadoAnaliseSite.objects.filter(url=sa['url'], incomplete=False):
            ras_aux.append(ras.violacao.violacao)
            for vcw in ViolacaoCriterioWCAG.objects.filter(violacao=ras.violacao, exist=True):
                vcw_aux.add(vcw.criterio.criterio)
        vcw_aux = list(vcw_aux)
        vcw_aux.sort()

        todos_ras[sa['url']] = [ras_aux, vcw_aux]

    template = loader.get_template('todos_resultados_analise_site.html')
    context = {
        'form': form,
        'todos_ras': todos_ras,
        'todos_acv': todos_acv,
        'site_mais_violacao': site_mais_violacao,
        'maior_numero_violacoes': maior_numero_violacoes,
        'numero_ocorrencias_violacao': numero_ocorrencias_violacao
    }
    return render(request, "todos_resultados_analise_site.html", context)


def get_revisao_manual(request):
    if request.method == 'POST':
        if 'analisar' in request.POST and request.POST['analisar'] == 'Analisar':
            form = ResultadoAnaliseSiteForm(request.POST)
            if form.is_valid():
                analisa_site(form.cleaned_data)
        elif 'delete' in request.POST and request.POST['delete'] == 'Delete':
            try:
                site_a_ser_apagado = SiteAnalisado.objects.get(url=request.POST['k'])
                site_a_ser_apagado.delete()

                for acv in AxeCoreViolacoes.objects.all():
                    ras_restantes = ResultadoAnaliseSite.objects.filter(violacao=acv.violacao)
                    if not ras_restantes:
                        acv.delete()
            except:
                print("Não foi possível apagar o site")

    form = ResultadoAnaliseSiteForm()

    todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao = get_todos_dados(True)

    template = loader.get_template('revisao_manual.html')
    context = {
        'form': form,
        'todos_ras': todos_ras,
        'todos_acv': todos_acv,
        'site_mais_violacao': site_mais_violacao,
        'maior_numero_violacoes': maior_numero_violacoes,
        'numero_ocorrencias_violacao': numero_ocorrencias_violacao
    }
    return render(request, "revisao_manual.html", context)


def get_url_analise_site(request):
    if request.method == 'POST':
        form = ResultadoAnaliseSiteForm(request.POST)
        if form.is_valid():
            analisa_site(form.cleaned_data)
            return HttpResponseRedirect("/todos_resultados_analise_site/")
    else:
        form = ResultadoAnaliseSiteForm()
        context = {
            "form": form,
            "todos_sa": SiteAnalisado.objects.all()
        }

    return render(request, "analisa_site.html", context)


def get_resultado_analise_site(request):
    pass


def get_analise_resultados(request):
    todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao = get_todos_dados()

    template = loader.get_template('analise_resultados.html')
    context = {
        'site_mais_violacao': site_mais_violacao,
        'maior_numero_violacoes': maior_numero_violacoes,
        'numero_ocorrencias_violacao': numero_ocorrencias_violacao
    }
    return HttpResponse(template.render(context, request))


def get_classifica_violacao(request):
    if request.method == 'POST':
        if 'insere' in request.POST and request.POST['insere'] == 'Inserir':
            form = TipoDeficienciaForm(request.POST)
            if form.is_valid():
                deficiencia = form.cleaned_data['deficiencia'].lower().capitalize()
                td_index = TipoDeficiencia.objects.aggregate(Max("index", default=-1))['index__max'] + 1
                try:
                    TipoDeficiencia.objects.get(deficiencia=deficiencia)
                except:
                    TipoDeficiencia.objects.create(deficiencia=deficiencia, index=td_index)
        elif 'delete' in request.POST and request.POST['delete'] == 'Delete':
            try:
                deficiencia_a_ser_apagada = TipoDeficiencia.objects.get(deficiencia=request.POST['td'])
                deficiencia_a_ser_apagada.delete()
            except:
                print("Não foi possível apagar o tipo de deficiência do banco de dados")
        elif 'put' in request.POST and request.POST['put'] == 'Salvar':
            # Verifica se o tipo de deficiência existe na base de dados
            try:
                acv = AxeCoreViolacoes.objects.get(violacao=str(request.POST['acv']))
                for td in TipoDeficiencia.objects.all():
                    deficiencia = TipoDeficiencia.objects.get(deficiencia=td.deficiencia)
                    (vtd_get, vtd_create) = ViolacaoTipoDeficiencia.objects.get_or_create(violacao=acv, deficiencia=deficiencia)
                    vtd = vtd_get if vtd_get else vtd_create
                    if td.deficiencia in request.POST:
                        vtd.exist = True
                    else:
                        vtd.exist = False
                    vtd.save()
            except Exception as e:
                print("Erro ao atualizar tipos de deficiência da violação.")
                print(e)

    form = TipoDeficienciaForm()

    contador_violacao_por_deficiencia = {}
    for td in TipoDeficiencia.objects.all():
        contador_violacao_por_deficiencia[td.deficiencia] = 0
    for vtd in ViolacaoTipoDeficiencia.objects.filter(exist=True):
        contador_violacao_por_deficiencia[vtd.deficiencia.deficiencia] += 1

    contador_violacao_por_deficiencia = dict(sorted(contador_violacao_por_deficiencia.items(), key=lambda item: item[1], reverse=True))

    todos_acv = set()
    for ras in ResultadoAnaliseSite.objects.filter(incomplete=False):
        todos_acv.add(ras.violacao)

    context = {
        "form": form,
        "todos_td": TipoDeficiencia.objects.all(),
        "todos_acv": todos_acv, #AxeCoreViolacoes.objects.all(),
        "todos_vtd": ViolacaoTipoDeficiencia.objects.all(),
        "contador_violacao_por_deficiencia": contador_violacao_por_deficiencia
    }

    return render(request, "classifica_violacao.html", context)


def get_criterios_wcag(request):
    if request.method == 'POST':
        if 'insere' in request.POST and request.POST['insere'] == 'Inserir':
            form = NovoCriterioWCAG(request.POST)
            if form.is_valid():
                criterio = form.cleaned_data['criterio'].lower().capitalize()
                prioridade = form.cleaned_data['prioridade'].upper()
                (criterio_get, criterio_create) = CriterioWCAG.objects.get_or_create(criterio=criterio, prioridade=prioridade)
        elif 'delete' in request.POST and request.POST['delete'] == 'Delete':
            try:
                criterio_a_ser_apagado = CriterioWCAG.objects.get(criterio=request.POST['criterio'])
                criterio_a_ser_apagado.delete()
            except:
                print("Não foi possível apagar o critério do banco de dados")
        elif 'put' in request.POST and request.POST['put'] == 'Salvar':
            # Verifica se o tipo de deficiência existe na base de dados
            try:
                acv = AxeCoreViolacoes.objects.get(violacao=str(request.POST['acv']))
                for criterio_aux in CriterioWCAG.objects.all():
                    criterio = CriterioWCAG.objects.get(criterio=criterio_aux.criterio)
                    (vcw_get, vcw_create) = ViolacaoCriterioWCAG.objects.get_or_create(violacao=acv, criterio=criterio)
                    vcw = vcw_get if vcw_get else vcw_create
                    if criterio_aux.criterio in request.POST:
                        vcw.exist = True
                    else:
                        vcw.exist = False
                    vcw.save()
            except Exception as e:
                print("Erro ao atualizar tipos de deficiência da violação.")
                print(e)

    form = NovoCriterioWCAG()

    todos_acv = set()
    for ras in ResultadoAnaliseSite.objects.filter(incomplete=False):
        todos_acv.add(ras.violacao)

    contador_violacao_por_criterio = {}
    for criterio in CriterioWCAG.objects.all():
        contador_violacao_por_criterio[criterio] = 0
    for vcw in ViolacaoCriterioWCAG.objects.filter(exist=True):
        contador_violacao_por_criterio[vcw.criterio] += 1

    contador_violacao_por_criterio = dict(sorted(contador_violacao_por_criterio.items(), key=lambda item: item[1], reverse=True))

    context = {
        "form": form,
        "todos_td": TipoDeficiencia.objects.all(),
        "todos_acv": todos_acv,
        "todos_vtd": ViolacaoTipoDeficiencia.objects.all(),
        "todos_criterios": CriterioWCAG.objects.all(),
        "todos_vcw": ViolacaoCriterioWCAG.objects.all(),
        "contador_violacao_por_criterio": contador_violacao_por_criterio
    }
    return render(request, "criterios_wcag.html", context)


def get_categoriza_site(request):
    if request.method == 'POST':
        if 'insere' in request.POST and request.POST['insere'] == 'Inserir':
            form = NovaCategoriaForm(request.POST)
            if form.is_valid():
                categoria = form.cleaned_data['categoria'].lower().capitalize()
                cs_index = SiteCategoria.objects.aggregate(Max("index", default=-1))['index__max'] + 1
                try:
                    SiteCategoria.objects.get(categoria=categoria)
                except:
                    SiteCategoria.objects.create(categoria=categoria, index=cs_index)
        elif 'delete' in request.POST and request.POST['delete'] == 'Delete':
            try:
                categoria_a_ser_apagada = SiteCategoria.objects.get(categoria=request.POST['cs'])
                categoria_a_ser_apagada.delete()
            except:
                print("Não foi possível apagar a categoria de site do banco de dados")
        elif 'put' in request.POST and request.POST['put'] == 'Salvar':
            # Verifica se a categoria de site existe na base de dados
            try:
                cs = SiteCategoria.objects.get(categoria=request.POST['categoria'])
                site = SiteAnalisado.objects.get(url=request.POST['site'])
                site.categoria = cs
                site.save()
            except:
                print("Falha ao atualizar categoria de site")

    form = NovaCategoriaForm()

    contagem_categoria = {cs: 0 for cs in SiteCategoria.objects.all()}

    todos_sites = SiteAnalisado.objects.all()
    for sa in todos_sites:
        if sa.categoria:
            contagem_categoria[sa.categoria] += 1

    contagem_categoria = dict(sorted(contagem_categoria.items(), key=lambda item: item[1], reverse=True))

    context = {
        "form": form,
        "todos_cs": SiteCategoria.objects.all(),
        "todos_sites": todos_sites,
        "contagem_categoria": contagem_categoria
    }
    return render(request, "categoriza_site.html", context)


def absoluto_para_porcentagem(numero_ocorrencias, count, ordenar=True):
    if count == 0:
        count = 1
    for k, nov in numero_ocorrencias.items():
        nov[1] = nov[0] / count
        nov[1] = '%.2f' % (nov[1] * 100)
        nov[1] = nov[1] + "%"
    if ordenar:
        numero_ocorrencias = dict(sorted(numero_ocorrencias.items(), key=lambda item: item[1][0], reverse=True))

    return numero_ocorrencias


def get_estatisticas_axe_core(request):
    todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao = get_todos_dados()

    numero_total_violacoes = len(ResultadoAnaliseSite.objects.filter(incomplete=False))

    # Quantidade de vezes que uma deficiência é afetada por uma violação
    numero_deficiencia_por_violacao = {}
    count_ndv = 0
    for td in TipoDeficiencia.objects.all():
        numero_deficiencia_por_violacao[td.deficiencia] = [0, 0]

    # Quantidade de vezes que uma violação ocorre
    numero_ocorrencias_violacao = {}
    count_nov = 0
    for k, v in todos_ras.items():
        for violacao in v:
            count_nov += 1
            if not violacao in numero_ocorrencias_violacao.keys():
                numero_ocorrencias_violacao[violacao] = [1, 0, set()]
            else:
                numero_ocorrencias_violacao[violacao][0] += 1

    # Quantidade de violações por grau de prioridade
    de_para_grau_prioridade = {
        'critical': 'Crítico',
        'serious': 'Sério',
        'moderate': 'Moderado',
        'minor': 'Baixo'
    }
    numero_violacoes_por_prioridade = {
        'Crítico': [0, 0],
        'Sério': [0, 0],
        'Moderado': [0, 0],
        'Baixo': [0, 0]
    }
    count_nvp = 0

    # Ocorrências por categoria de site
    numero_violacoes_por_categoria_de_site = {}
    for sa in SiteAnalisado.objects.all():
        if not sa.categoria.categoria in numero_violacoes_por_categoria_de_site:
            numero_violacoes_por_categoria_de_site[sa.categoria.categoria] = [0, 0, 1]
        else:
            numero_violacoes_por_categoria_de_site[sa.categoria.categoria][2] += 1
    count_nvcs = 0

    # Violação por categoria de site
    vcs_aux = {}
    violacao_por_categoria_de_site = {}
    ## Conta quantas vezes cada violação ocorreu para cada categoria de site
    for sc in SiteCategoria.objects.all():
        vcs_aux[sc.categoria] = {}

    for ras in ResultadoAnaliseSite.objects.filter(incomplete=False):
        numero_ocorrencias_violacao[ras.violacao.violacao][2].add(ras.url.categoria.categoria)

        for vtd in ViolacaoTipoDeficiencia.objects.filter(violacao=ras.violacao, exist=True):
            numero_deficiencia_por_violacao[vtd.deficiencia.deficiencia][0] += 1
            count_ndv += 1

        count_nvp += 1
        numero_violacoes_por_prioridade[de_para_grau_prioridade[ras.violacao.impact]][0] += 1

        count_nvcs += 1
        numero_violacoes_por_categoria_de_site[ras.url.categoria.categoria][0] += 1

        categoria = ras.url.categoria.categoria
        violacao = ras.violacao.violacao

        if not violacao in vcs_aux[categoria]:
            vcs_aux[categoria][violacao] = 1
        else:
            vcs_aux[categoria][violacao] += 1

    ## Em porcentagem
    numero_deficiencia_por_violacao = absoluto_para_porcentagem(numero_deficiencia_por_violacao, count_ndv)
    numero_ocorrencias_violacao = absoluto_para_porcentagem(numero_ocorrencias_violacao, count_nov)
    numero_violacoes_por_prioridade = absoluto_para_porcentagem(numero_violacoes_por_prioridade, count_nvp, False)
    numero_violacoes_por_categoria_de_site = absoluto_para_porcentagem(numero_violacoes_por_categoria_de_site, count_nvcs)

    ## Cria uma lista de listas qual que cada lista mais interna tem tamanho máximo de 5
    ## elementos para melhor organizar na apresentação da tela
    linha_tam_maximo = 5
    for cat, vcs_di in vcs_aux.items():
        # Ordena pela quantidade de ocorrências
        vcs_di_aux = sorted(list(vcs_di.items()), key=lambda item: item[1], reverse=True)
        aux = []
        for i, vcs in enumerate(vcs_di_aux):
            if i % linha_tam_maximo == 0:
                aux.append([(vcs[0], vcs[1])])
            else:
                aux[int(i / linha_tam_maximo)].append((vcs[0], vcs[1]))
        violacao_por_categoria_de_site[cat] = aux

    context = {
        "todos_sa": todos_sa,
        "todos_acv": todos_acv,
        "todos_ras": todos_ras,
        "numero_total_violacoes": numero_total_violacoes,
        "site_mais_violacao": site_mais_violacao,
        "maior_numero_violacoes": maior_numero_violacoes,
        "numero_ocorrencias_violacao": numero_ocorrencias_violacao,
        "numero_deficiencia_por_violacao": numero_deficiencia_por_violacao,
        "numero_violacoes_por_prioridade": numero_violacoes_por_prioridade,
        "numero_violacoes_por_categoria_de_site": numero_violacoes_por_categoria_de_site,
        "violacao_por_categoria_de_site": violacao_por_categoria_de_site,
        "contador_linha": 0
    }
    return render(request, 'estatisticas.html', context)

# Continuação das estatísticas geradas para o trabalho
def get_estatisticas_axe_core_cont(request):
    todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao = get_todos_dados()

    numero_total_violacoes = len(ResultadoAnaliseSite.objects.filter(incomplete=False))

    # Associação entre violações
    labels = [acv.violacao for acv in AxeCoreViolacoes.objects.all()]
    tabela = pd.DataFrame(0, columns=labels, index=labels)
    for site in SiteAnalisado.objects.all():
        violacoes_ja_percorridas = set()
        for ras_x in ResultadoAnaliseSite.objects.filter(url=site, incomplete=False).order_by('violacao'):
            violacoes_ja_percorridas.add(ras_x.violacao.violacao)
            for ras_y in ResultadoAnaliseSite.objects.filter(url=site, incomplete=False).exclude(violacao__in=violacoes_ja_percorridas).order_by('violacao'):
                tabela.at[ras_x.violacao.violacao, ras_y.violacao.violacao] += 1
                tabela.at[ras_y.violacao.violacao, ras_x.violacao.violacao] += 1
    tabela_maior_valor = tabela.max().max()
    branco = Color("white")
    cores = list(branco.range_to(Color("green"), tabela_maior_valor + 1))
    cores_barras = [cor.hex for cor in cores]
    cores_index = [i for i in range(len(cores))]

    # Dados para desenhar o histograma
    tabela[:] = np.tril(tabela.values)
    eixo_x = [i for i in range(tabela_maior_valor+1)]
    tabela_histograma_aux = {}
    for i in range(tabela.shape[0]):
        for j in range(tabela.shape[1]):
            if j >= i:
                tabela.iat[i, j] = -1
            else:
                if not tabela.iat[i, j] in tabela_histograma_aux:
                    tabela_histograma_aux[tabela.iat[i, j]] = 1
                else:
                    tabela_histograma_aux[tabela.iat[i, j]] += 1

    tabela_histograma = [tabela_histograma_aux[x] if x in tabela_histograma_aux else 0 for x in eixo_x]
    del eixo_x[0]
    del tabela_histograma[0]

    context = {
        "todos_sa": todos_sa,
        "todos_acv": todos_acv,
        "todos_ras": todos_ras,
        "numero_total_violacoes": numero_total_violacoes,
        "site_mais_violacao": site_mais_violacao,
        "maior_numero_violacoes": maior_numero_violacoes,
        "numero_ocorrencias_violacao": numero_ocorrencias_violacao,
        "contador_linha": 0,
        "tabela": tabela,
        "tabela_histograma": tabela_histograma,
        "eixo_x": eixo_x,
        "cores": cores,
        "cores_barras": cores_barras,
        "cores_index": cores_index
    }
    return render(request, 'estatisticas_2.html', context)


def get_estatisticas_wcag(request):
    todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao = get_todos_dados()

    numero_total_violacoes = 0
    for ras in ResultadoAnaliseSite.objects.filter(incomplete=False):
        numero_total_violacoes += len(ViolacaoCriterioWCAG.objects.filter(violacao=ras.violacao, exist=True))

    # Quantidade de vezes que uma deficiência é afetada por uma violação
    numero_criterios_por_deficiencia = {}
    count_ndv = 0
    for td in TipoDeficiencia.objects.all():
        numero_criterios_por_deficiencia[td.deficiencia] = [0, 0]

    # Quantidade de vezes que uma violação ocorre
    numero_ocorrencias_criterio = {}
    count_noc = 0
    for url, violacoes in todos_ras.items():
        for violacao in violacoes:
            for vcw in ViolacaoCriterioWCAG.objects.filter(violacao=violacao, exist=True):
                count_noc += 1
                if not vcw.criterio.criterio in numero_ocorrencias_criterio.keys():
                    numero_ocorrencias_criterio[vcw.criterio.criterio] = [1, 0, set()]
                else:
                    numero_ocorrencias_criterio[vcw.criterio.criterio][0] += 1

    # Quantidade de violações por grau de prioridade
    numero_violacoes_por_prioridade = {
        'A': [0, 0],
        'AA': [0, 0],
        'AAA': [0, 0]
    }
    count_nvp = 0

    # Ocorrências por categoria de site
    numero_criterios_reprovados_por_site = {}
    for sa in SiteAnalisado.objects.all():
        if not sa.categoria.categoria in numero_criterios_reprovados_por_site:
            numero_criterios_reprovados_por_site[sa.categoria.categoria] = [0, 0, 1]
        else:
            numero_criterios_reprovados_por_site[sa.categoria.categoria][2] += 1
    count_nvcs = 0

    # Critério reprovado por categoria de site
    vcs_aux = {}
    dpc_aux = {}
    dpc_total = {}
    criterios_reprovados_por_categoria_de_site = {}
    ## Conta quantas vezes cada critério reprovado ocorreu para cada categoria de site
    for sc in SiteCategoria.objects.all():
        vcs_aux[sc.categoria] = {}
        dpc_aux[sc.categoria] = {}
        dpc_total[sc.categoria] = 0

    for ras in ResultadoAnaliseSite.objects.filter(incomplete=False):
        categoria = ras.url.categoria.categoria
        violacao = ras.violacao
        for vcw in ViolacaoCriterioWCAG.objects.filter(violacao=violacao, exist=True):
            numero_ocorrencias_criterio[vcw.criterio.criterio][2].add(categoria)

            count_nvp += 1
            prioridade = vcw.criterio.prioridade
            numero_violacoes_por_prioridade[prioridade][0] += 1

            count_nvcs += 1
            numero_criterios_reprovados_por_site[categoria][0] += 1

            for vtd in ViolacaoTipoDeficiencia.objects.filter(violacao=violacao, exist=True):
                numero_criterios_por_deficiencia[vtd.deficiencia.deficiencia][0] += 1
                count_ndv += 1

            criterio = vcw.criterio.criterio
            if not vcw.criterio.criterio in vcs_aux[categoria]:
                vcs_aux[categoria][criterio] = 1
            else:
                vcs_aux[categoria][criterio] += 1
        for vtd in ViolacaoTipoDeficiencia.objects.filter(violacao=violacao, exist=True):
            deficiencia = vtd.deficiencia.deficiencia
            if not deficiencia in dpc_aux[categoria]:
                dpc_aux[categoria][deficiencia] = 1
            else:
                dpc_aux[categoria][deficiencia] += 1
            dpc_total[categoria] += 1

    ## Em porcentagem
    numero_criterios_por_deficiencia = absoluto_para_porcentagem(numero_criterios_por_deficiencia, count_ndv)
    numero_ocorrencias_criterio = absoluto_para_porcentagem(numero_ocorrencias_criterio, count_noc)
    numero_violacoes_por_prioridade = absoluto_para_porcentagem(numero_violacoes_por_prioridade, count_nvp, False)
    numero_criterios_reprovados_por_site = absoluto_para_porcentagem(numero_criterios_reprovados_por_site, count_nvcs)

    ## Cria uma lista de listas tal que cada lista mais interna tem tamanho máximo de 5
    ## elementos para melhor organizar na apresentação da tela
    linha_tam_maximo = 2
    for cat, vcs_di in vcs_aux.items():
        # Ordena pela quantidade de ocorrências
        vcs_di_aux = sorted(list(vcs_di.items()), key=lambda item: item[1], reverse=True)
        aux = []
        for i, vcs in enumerate(vcs_di_aux):
            if i % linha_tam_maximo == 0:
                aux.append([(vcs[0], vcs[1])])
            else:
                aux[int(i / linha_tam_maximo)].append((vcs[0], vcs[1]))
        criterios_reprovados_por_categoria_de_site[cat] = [aux]

    print(dpc_total)
    for cat, dpc_di in dpc_aux.items():
        dpc_di_aux = sorted(list(dpc_di.items()), key=lambda item: item[1], reverse=True)
        aux = []
        for i, dpc in enumerate(dpc_di_aux):
            dpc_porcentagem = (u"{:.2f}%".format(dpc[1] / dpc_total[cat] * 100))
            if i % linha_tam_maximo == 0:
                aux.append([(dpc[0], dpc[1], dpc_porcentagem)])
            else:
                aux[int(i / linha_tam_maximo)].append((dpc[0], dpc[1], dpc_porcentagem))
            #print(dpc)
        #print(aux)

        criterios_reprovados_por_categoria_de_site[cat].append(aux)


    context = {
        "todos_sa": todos_sa,
        "todos_acv": todos_acv,
        "todos_ras": todos_ras,
        "numero_total_violacoes": numero_total_violacoes,
        "site_mais_violacao": site_mais_violacao,
        "maior_numero_violacoes": maior_numero_violacoes,
        "numero_ocorrencias_criterio": numero_ocorrencias_criterio,
        "numero_criterios_por_deficiencia": numero_criterios_por_deficiencia,
        "numero_violacoes_por_prioridade": numero_violacoes_por_prioridade,
        "numero_criterios_reprovados_por_site": numero_criterios_reprovados_por_site,
        "criterios_reprovados_por_categoria_de_site": criterios_reprovados_por_categoria_de_site,
        "contador_linha": 0
    }
    return render(request, 'estatisticas_wcag.html', context)


# Continuação das estatísticas geradas para o trabalho
def get_estatisticas_wcag_cont(request):
    todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao = get_todos_dados()

    numero_total_violacoes = 0
    for ras in ResultadoAnaliseSite.objects.filter(incomplete=False):
        numero_total_violacoes += len(ViolacaoCriterioWCAG.objects.filter(violacao=ras.violacao, exist=True))

    # Associação entre violações
    labels = [acv.violacao for acv in AxeCoreViolacoes.objects.all()]
    labels = [criterio.criterio for criterio in CriterioWCAG.objects.all()]
    tabela = pd.DataFrame(0, columns=labels, index=labels)

    for site in SiteAnalisado.objects.all():
        criterios_reprovados_pelo_site = set()
        for ras in ResultadoAnaliseSite.objects.filter(url=site, incomplete=False):
            for vcw in ViolacaoCriterioWCAG.objects.filter(violacao=ras.violacao, exist=True):
                criterios_reprovados_pelo_site.add(vcw.criterio.criterio)

        criterios_reprovados_pelo_site = list(criterios_reprovados_pelo_site)
        criterios_reprovados_pelo_site.sort()
        criterios_reprovados_ja_percorridas = set()
        for vcw_x in criterios_reprovados_pelo_site:
            criterios_reprovados_ja_percorridas.add(vcw_x)
            criterios_reprovados_pelo_site_y = list(set(criterios_reprovados_pelo_site) - criterios_reprovados_ja_percorridas)
            criterios_reprovados_pelo_site_y.sort()
            for vcw_y in criterios_reprovados_pelo_site_y:
                tabela.at[vcw_x, vcw_y] += 1
                tabela.at[vcw_y, vcw_x] += 1
    tabela_maior_valor = tabela.max().max()
    branco = Color("white")
    cores = list(branco.range_to(Color("green"), tabela_maior_valor + 1))
    cores_barras = [cor.hex for cor in cores]
    cores_index = [i for i in range(len(cores))]

    # Dados para desenhar o histograma
    tabela[:] = np.tril(tabela.values)
    eixo_x = [i for i in range(tabela_maior_valor+1)]
    tabela_histograma_aux = {}
    for i in range(tabela.shape[0]):
        for j in range(tabela.shape[1]):
            if j >= i:
                tabela.iat[i, j] = -1
            else:
                if not tabela.iat[i, j] in tabela_histograma_aux:
                    tabela_histograma_aux[tabela.iat[i, j]] = 1
                else:
                    tabela_histograma_aux[tabela.iat[i, j]] += 1

    tabela_histograma = [tabela_histograma_aux[x] if x in tabela_histograma_aux else 0 for x in eixo_x]
    del eixo_x[0]
    del tabela_histograma[0]

    context = {
        "todos_sa": todos_sa,
        "todos_acv": todos_acv,
        "todos_ras": todos_ras,
        "numero_total_violacoes": numero_total_violacoes,
        "site_mais_violacao": site_mais_violacao,
        "maior_numero_violacoes": maior_numero_violacoes,
        "numero_ocorrencias_violacao": numero_ocorrencias_violacao,
        "contador_linha": 0,
        "tabela": tabela,
        "tabela_histograma": tabela_histograma,
        "eixo_x": eixo_x,
        "cores": cores,
        "cores_barras": cores_barras,
        "cores_index": cores_index
    }
    return render(request, 'estatisticas_wcag_2.html', context)


def get_estatisticas_cont_2(request):
    todos_sa, todos_acv, todos_ras, site_mais_violacao, maior_numero_violacoes, numero_ocorrencias_violacao = get_todos_dados()

    violacoes_totais_por_categoria_de_site = {}

    context = {
        "todos_sa": todos_sa,
        "todos_acv": todos_acv,
        "todos_ras": todos_ras,
        "site_mais_violacao": site_mais_violacao,
        "maior_numero_violacoes": maior_numero_violacoes,
        "numero_ocorrencias_violacao": numero_ocorrencias_violacao,
        "contador_linha": 0,
    }
    return render(request, 'estatisticas_3.html', context)

    ########################################################
    ########################################################
    ########################################################

# Testes pandas
def get_pandas_testes(request):
    legenda_categoria_site = [[cs.index, cs.categoria] for cs in SiteCategoria.objects.all()]
    legends_violacao = [[acv.index, acv.violacao] for acv in AxeCoreViolacoes.objects.all()]
    legenda_deficiencia = [[td.index, td.deficiencia] for td in TipoDeficiencia.objects.all()]

    csv_consolidacao_dados_tabela = []
    i = -1
    for ras in ResultadoAnaliseSite.objects.filter(incomplete=False):
        # Recebe URL, categoria, violacao e impacto da violacao
        ras_aux = [i, ras.url.url, ras.url.categoria.index if ras.url.categoria else '', ras.violacao.index, ras.violacao.impact]

        # Recebe os tipos de deficiências afetadas
        for vtd in ViolacaoTipoDeficiencia.objects.filter(violacao=ras.violacao, exist=True):
            ras_aux.append(vtd.deficiencia.index)
            ras_aux[0] += 1
            csv_consolidacao_dados_tabela.append(ras_aux[:])
            ras_aux.pop()
        i = ras_aux[0]

    df = pd.DataFrame(csv_consolidacao_dados_tabela)
    df.columns = ["ID", "URL", "Categoria", "Violação", "Impacto", "Deficiência"]
    x = df[['Categoria', 'Violação', 'Deficiência']]

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)

    """
    # melhor é k=4
    inertia = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, random_state=21)
        kmeans.fit(x_scaled)
        inertia.append(kmeans.inertia_)
        print(u"k={} / inertia={} / hipotenusa={}".format(k, kmeans.inertia_/100, math.hypot(k, kmeans.inertia_/100)))

    plt.figure(figsize=(8, 8))
    plt.plot(range(1, 11), inertia, marker='o')
    plt.title('Elbow method')
    plt.xlabel('Number of clusters')
    plt.ylabel('Inertia')
    plt.show()
    """

    kmeans = KMeans(n_clusters=4, random_state=21)
    kmeans.fit(x_scaled)

    df['Cluster'] = kmeans.labels_

    """
    # Visualize the clusters using annual income and spending score
    plt.figure(figsize=(6, 6))
    #sns.scatterplot(x=df['Categoria'], y=df['Violação'], hue=df['Cluster'], palette='viridis', s=100)
    sns.scatterplot(x=df['Categoria'], y=df['Deficiência'], hue=df['Cluster'], palette='viridis', s=100)
    #plt.scatter(kmeans.cluster_centers_[:, 1], kmeans.cluster_centers_[:, 2], s=300, c='red', label='Centroids')
    plt.title('Customer Segments based on income and spending Score')
    plt.legend()
    plt.show()
    """

    context = {
        "df": df,
        "df_head": df.head(),
        "legenda_categoria_site": legenda_categoria_site,
        "legends_violacao": legends_violacao,
        "legenda_deficiencia": legenda_deficiencia
    }
    return render(request, 'testes.html', context)