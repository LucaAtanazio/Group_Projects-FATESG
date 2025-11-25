from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False
    print("AVISO: 'webdriver-manager' não instalado. Certifique-se de que o ChromeDriver está no PATH.")

def inicializar_selenium():
    """Inicializa o driver do Chrome em modo headless."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        if USE_WDM:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        return driver
    except Exception as e:
        print(f"Erro ao inicializar o Selenium: {e}")
        return None

def obter_texto_seguro(soup, seletor, tipo='css'):
    """Tenta extrair texto com um seletor, retornando string vazia em caso de falha."""
    try:
        if tipo == 'css':
            elemento = soup.select_one(seletor)
        elif tipo == 'xpath':
            return soup.select_one(seletor).get_text(strip=True) if soup.select_one(seletor) else ''
        
        return elemento.get_text(strip=True) if elemento else ''
    except Exception:
        return ''

def formatar_valor(valor_str):
    """Limpa e converte string de valor para float, ou retorna 0.0."""
    try:
        limpo = re.sub(r'[^\d,]', '', valor_str).replace(',', '.')
        return float(limpo)
    except:
        return 0.0

def raspar_dados_nfce(url_nfce):
    """
    Acessa a URL da NFC-e, renderiza com Selenium e extrai os dados com BeautifulSoup.

    Args:
        url_nfce (str): URL completa da NFC-e.

    Returns:
        tuple: (dados_nota, lista_itens) ou (None, None) em caso de falha.
    """
    driver = inicializar_selenium()
    if not driver:
        return None, None

    try:
        driver.get(url_nfce)

        # 1. Aguardar o carregamento de um elemento chave (obrigatório)
        # O div#conteudoPrincipal é um bom alvo.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "conteudoPrincipal"))
        )
        
        time.sleep(3) 

        # 2. Obter o HTML completo e passar para o BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # --- Extração dos Dados Gerais ---
        dados_nota = {}
        
        data_venda_hora_raw = obter_texto_seguro(soup, 'div.blocoAbaixo div.txtTit')
        data_match = re.search(r'(\d{2}/\d{2}/\d{4})', data_venda_hora_raw)
        hora_match = re.search(r'(\d{2}:\d{2}:\d{2})', data_venda_hora_raw)
        
        dados_nota['data_venda'] = data_match.group(1) if data_match else ''
        dados_nota['hora_venda'] = hora_match.group(1) if hora_match else ''
        
        valor_total_raw = (
            obter_texto_seguro(soup, 'span.txtValor') or 
            obter_texto_seguro(soup, 'div.txtValorTotal') or
            obter_texto_seguro(soup, '#totalGeral') or 
            obter_texto_seguro(soup, 'div.valorTotal')
        )
        dados_nota['valor_total'] = formatar_valor(valor_total_raw)
        
        # Forma de Pagamento (pode estar em um div.txtObs, div.modalidade, etc.)
        forma_pagamento_raw = (
            obter_texto_seguro(soup, 'div.txtObs') or 
            obter_texto_seguro(soup, 'div.modalidade')
        )
        forma_pagamento = 'Outros'
        pag_options = ['Débito', 'Crédito', 'Dinheiro', 'Pix', 'Voucher', 'Cartão']
        for pag in pag_options:
            if pag.lower() in forma_pagamento_raw.lower():
                forma_pagamento = pag
                break
        dados_nota['forma_pagamento'] = forma_pagamento

        # --- Extração dos Itens ---
        lista_itens = []
        
        # Seletor para a tabela de itens (Exemplo: tbody com a classe ui-datatable-data)
        tabela_itens = soup.select('tbody.ui-datatable-data > tr')
        
        if not tabela_itens:
            tabela_itens = soup.select('div.divItem') 

        for linha in tabela_itens:
            item = {}
            
            # Nome do Produto (Geralmente div.txtTit ou div.txtTit2)
            nome_produto = obter_texto_seguro(linha, 'div.txtTit') or obter_texto_seguro(linha, 'div.txtTit2')
            
            # Padrão 1: Seletor direto para as colunas na linha da tabela
            quant_raw = obter_texto_seguro(linha, '.colunaQuant div.txtTit')
            unit_raw = obter_texto_seguro(linha, '.colunaUnit div.txtTit')
            total_raw = obter_texto_seguro(linha, '.colunaTotal div.txtTit')
            
            if not nome_produto:
                continue 
            if not quant_raw:
                linha_texto = linha.get_text().strip()
                valores_monetarios = re.findall(r'\d{1,3}(?:\.\d{3})*(?:,\d{2})', linha_texto)
                
                if not valores_monetarios:
                    continue
                
                if len(valores_monetarios) >= 3:
                    unit_raw = valores_monetarios[-2]
                    total_raw = valores_monetarios[-1]
                
                quant_match = re.search(r'Qtd\.:\s*([\d,.]+)', linha_texto, re.I)
                quant_raw = quant_match.group(1) if quant_match else '1,00'


            item['produto'] = nome_produto
            item['quantidade'] = formatar_valor(quant_raw)
            item['preco_unitario'] = formatar_valor(unit_raw)
            item['total_item'] = formatar_valor(total_raw)
            
            item['data_venda'] = dados_nota['data_venda']
            item['hora_venda'] = dados_nota['hora_venda']
            item['forma_pagamento'] = dados_nota['forma_pagamento']
            item['valor_total_nota'] = dados_nota['valor_total']
            
            lista_itens.append(item)

        # 3. Limpeza final dos dados gerais
        # Remove chaves do dados_nota que não serão salvas no CSV de notas
        dados_nota.pop('valor_total_nota', None) 
        dados_nota.pop('data_venda', None) 
        dados_nota.pop('hora_venda', None) 
        dados_nota.pop('forma_pagamento', None) 
        dados_nota['valor_total'] = dados_nota.get('valor_total', 0.0)
        
        return dados_nota, lista_itens

    except Exception as e:
        print(f"Erro no scraping da URL {url_nfce}: {e}")
        return None, None
    finally:
        if driver:
            driver.quit()