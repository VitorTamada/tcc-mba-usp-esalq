import re
from selenium import webdriver
from axe_selenium_python import Axe
from .models import SiteAnalisado, ResultadoAnaliseSite, AxeCoreViolacoes
from django.db.models import Max


def trata_url(url):
    if url[-1] == '/':
        url = url[:-1]

    # Usada como chave nas tabelas do banco de dados
    url_limpa = re.sub("https://", "", url)

    # Usada para análise pelo axe-core
    url_completa = url
    https = re.search("https://", url)
    if not https:
        https = re.search("http://", url)
        if not https:
            url_completa = "https://" + url

    return url_limpa, url_completa


def insere_resultados_banco_de_dados(url, results):
    for r in results['violations']:
        if any("wcag" in tag for tag in r['tags']):
            acv_index = AxeCoreViolacoes.objects.aggregate(Max("index", default=-1))['index__max'] + 1
            (sa_get, sa_create) = SiteAnalisado.objects.get_or_create(url=url)
            try:
                acv = AxeCoreViolacoes.objects.get(violacao=r["id"],
                                                    impact=r["impact"],
                                                    description=r["description"])
            except:
                acv = AxeCoreViolacoes.objects.create(violacao=r["id"],
                                                    impact=r["impact"],
                                                    description=r["description"],
                                                    index=acv_index)
            sa = sa_get if sa_get else sa_create
            print()
            print(sa)
            print(acv)
            ResultadoAnaliseSite.objects.get_or_create(url=sa, violacao=acv)

    for r in results['incomplete']:
        if any("wcag" in tag for tag in r['tags']):
            acv_index = AxeCoreViolacoes.objects.aggregate(Max("index", default=-1))['index__max'] + 1
            (sa_get, sa_create) = SiteAnalisado.objects.get_or_create(url=url)
            try:
                acv = AxeCoreViolacoes.objects.get(violacao=r["id"],
                                                    impact=r["impact"],
                                                    description=r["description"])
            except:
                acv = AxeCoreViolacoes.objects.create(violacao=r["id"],
                                                    impact=r["impact"],
                                                    description=r["description"],
                                                    index=acv_index)
            sa = sa_get if sa_get else sa_create
            try:
                ResultadoAnaliseSite.objects.get_or_create(url=sa, violacao=acv, incomplete=True)
            except Exception as e:
                print()
                print(e)
                print(sa)
                print(acv)


def analisa_site(form_data):
    try:
        url_lote = form_data['url'].split(',')

        for url in url_lote:
            print("Site analisado: " + url)
            # Tratamento da string URL
            url_limpa, url_completa = trata_url(url)
            try:
                sa = SiteAnalisado.objects.get(url=url_limpa)
                #return
            except Exception as e:
                print(e)

            # Abre navegador e axe-core
            driver = webdriver.Firefox()
            driver.get(url_completa)
            axe = Axe(driver)

            # Inject axe-core javascript into page.
            axe.inject()

            # Run axe accessibility checks.
            results = axe.run()

            # Write results to file
            #axe.write_results(results, 'a11y.json')
            insere_resultados_banco_de_dados(url_limpa, results)
            driver.close()

            # Assert no violations are found
            #assert len(results["violations"]) == 0, axe.report(results["violations"])
    except Exception as e:
        print("Não foi possível analisar o site: " + form_data['url'])
        print(e)