# scraper_nfce.py

import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

# --- Configuração do Selenium ---

def iniciar_driver():
    """Configura e inicia o WebDriver com opções headless."""
    print("Iniciando WebDriver em modo Headless...")
    
    # 1. Configurações Headless para rodar sem interface gráfica
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Simula um navegador comum para evitar bloqueios
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"]) # Evita logs excessivos

    # 2. Instala/Usa o driver correto
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

# --- Funções de Limpeza de Dados ---

def limpar_valor(texto):
    """Extrai e limpa valores numéricos de R$ X.XX."""
    if not texto:
        return 0.0
    # Remove qualquer coisa que não seja dígito, vírgula ou ponto
    valor_limpo = re.sub(r'[^\d,\.]', '', texto)
    # Substitui vírgula por ponto para conversão float (padrão brasileiro -> americano)
    valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0

# --- Função Principal de Raspagem de Dados ---

def raspar_dados_nfce(url_nfce: str) -> tuple[dict, list]:
    """
    Navega até a URL da NFC-e e raspa dados do cabeçalho e da lista de itens.
    
    Args:
        url_nfce: URL completa da NFC-e (do QR Code).
        
    Returns:
        Um tuple contendo: (dados_nota_dict, lista_itens).
    """
    driver = None
    dados_nota = {}
    lista_itens = []
    
    # Define um tempo máximo de espera
    MAX_WAIT = 15 

    try:
        driver = iniciar_driver()
        print(f"DEBUG: Navegando para: {url_nfce}")
        driver.get(url_nfce)
        
        # 1. Espera Condicional: Espera até que o elemento do Valor Total esteja visível
        # Se este seletor estiver errado, a raspagem falhará aqui.
        try:
            WebDriverWait(driver, MAX_WAIT).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "txtValorTotal")) 
            )
            print("DEBUG: Página da NFC-e carregada com sucesso.")
        except Exception:
            print("ERRO CRÍTICO: Não foi possível carregar o elemento chave (txtValorTotal) dentro do tempo.")
            # Salva screenshot para debug
            driver.save_screenshot("erro_carregamento.png")
            return None, None
            
        # 2. Extração dos Dados do Cabeçalho (NOTA)
        
        # ATENÇÃO: VERIFIQUE E ADAPTE ESTES SELETORES PARA O SITE DA SEFAZ DO SEU ESTADO
        
        # Exemplo de extração de Valor Total e Data/Hora:
        valor_total_text = driver.find_element(By.CLASS_NAME, "txtValorTotal").text
        data_hora_text = driver.find_element(By.ID, "datEmi").text
        
        dados_nota['valor_total'] = limpar_valor(valor_total_text)
        dados_nota['data_hora_nfce'] = data_hora_text # Formatação será feita no salvador_csv
        
        # 3. Extração da Lista de Itens
        
        # ATENÇÃO: O SELETOR DA TABELA DE ITENS É CRUCIAL AQUI
        
        # Este seletor assume que a tabela de itens tem o ID 'tabProdutos'
        tabela_itens = driver.find_element(By.ID, "tabProdutos") 
        
        # Encontra todas as linhas da tabela (exceto o cabeçalho)
        linhas_itens = tabela_itens.find_elements(By.TAG_NAME, "tr")[1:] 

        print(f"DEBUG: Encontradas {len(linhas_itens)} linhas de itens.")
        
        for linha in linhas_itens:
            # Seletores comuns para as colunas de um item:
            colunas = linha.find_elements(By.TAG_NAME, "td")
            
            if len(colunas) < 4:
                continue # Pula linhas inválidas
            
            # ATENÇÃO: OS ÍNDICES DE COLUNA DEVEM SER VERIFICADOS NO SEU SITE
            
            item = {
                'descricao_produto': colunas[0].text.strip(),
                'quantidade': limpar_valor(colunas[1].text),
                'unidade': colunas[2].text.strip(),
                'preco_unitario': limpar_valor(colunas[3].text),
                'total_item': limpar_valor(colunas[4].text)
            }
            lista_itens.append(item)
            
        print(f"SUCESSO: Raspagem concluída. {len(lista_itens)} itens extraídos.")

        # Adiciona a data de hoje à nota (para fins de auditoria)
        dados_nota['data_extracao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return dados_nota, lista_itens

    except Exception as e:
        print(f"ERRO DE SCRAPING GERAL: {e}")
        # Salva screenshot para debug
        if driver:
             driver.save_screenshot("erro_scraper_final.png")
             print("Screenshot 'erro_scraper_final.png' salvo.")
        return None, None
        
    finally:
        # Garante que o navegador seja fechado
        if driver:
            driver.quit()

# --- Exemplo de Teste ---
if __name__ == '__main__':
    # Use uma URL de teste REAL que você verificou ser acessível
    TEST_URL = "http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=52250339346861034147651070004999491107141815|2|1|1|DF46C0CAD32EF01BE6B47848D0D7BD145878E215"
    print("--- INICIANDO TESTE DO SCRAPER NFC-e ---")
    nota, itens = raspar_dados_nfce(TEST_URL)
    
    if nota:
        print("\n[SUCESSO] Dados da Nota:")
        for k, v in nota.items():
            print(f"  {k}: {v}")
        
        print("\n[SUCESSO] Detalhes dos Itens (5 primeiros):")
        for item in itens[:5]:
            print(f"  - {item['descricao_produto']} | Qtd: {item['quantidade']} | Total: {item['total_item']}")
    else:
        print("\n[FALHA] Não foi possível extrair dados da NFC-e.")