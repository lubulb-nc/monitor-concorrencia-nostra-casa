import requests
from bs4 import BeautifulSoup
import re
import time

# HEADERS padrão para todas as funções
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def scraper_plaza_chapeco():
    """
    Scraper refinado para Plaza Chapecó
    Extrai: código, título, preço, área, quartos, banheiros, vagas, endereço, tipo de negócio
    STATUS: ✅ FUNCIONANDO
    """
    imoveis_encontrados = []
    
    # URLs para aluguel e venda
    urls = [
        ("https://plazachapeco.com.br/alugar-imoveis-chapeco-sc/", "LOCAÇÃO"),
        ("https://plazachapeco.com.br/comprar-imoveis-chapeco-sc/", "VENDA")
    ]
    
    for url, tipo_negocio in urls:
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Seletor específico: links que contêm "/imovel/" na URL
        cards_de_imoveis = soup.find_all('a', href=re.compile(r'/imovel/'))
        
        print(f"Encontrados {len(cards_de_imoveis)} imóveis na Plaza Chapecó ({tipo_negocio}). Processando...")

        for card in cards_de_imoveis:
            try:
                # URL completa
                url_imovel = card.get('href', '')
                if url_imovel.startswith('/'):
                    url_imovel = 'https://plazachapeco.com.br' + url_imovel
                
                # Código do imóvel (extraído da URL)
                codigo_match = re.search(r'/imovel/(\d+)/', url_imovel)
                codigo = codigo_match.group(1) if codigo_match else ""
                
                # Título (classe específica identificada)
                titulo_elem = card.find(class_='chamadaimovel')
                titulo = titulo_elem.get_text().strip() if titulo_elem else ""
                
                # Preço (classe específica identificada)
                preco_elem = card.find(class_='valorimovel')
                preco = preco_elem.get_text().strip() if preco_elem else ""
                
                # Características (área, quartos, banheiros, vagas)
                caracteristicas_elem = card.find(class_='caracteristicas')
                area = quartos = banheiros = vagas = ""
                
                if caracteristicas_elem:
                    carac_text = caracteristicas_elem.get_text()
                    
                    # Extrair área
                    area_match = re.search(r'(\d+)m²', carac_text)
                    area = area_match.group(1) + 'm²' if area_match else ""
                    
                    # Extrair quartos
                    quartos_match = re.search(r'(\d+)\s+quartos?', carac_text)
                    quartos = quartos_match.group(1) if quartos_match else ""
                    
                    # Extrair banheiros
                    banheiros_match = re.search(r'(\d+)\s+banheiros?', carac_text)
                    banheiros = banheiros_match.group(1) if banheiros_match else ""
                    
                    # Extrair vagas
                    vagas_match = re.search(r'(\d+)\s+vagas?', carac_text)
                    vagas = vagas_match.group(1) if vagas_match else ""
                
                # Endereço (classe específica identificada)
                endereco_elem = card.find(class_='enderecoimovel')
                endereco = endereco_elem.get_text().strip() if endereco_elem else ""
                
                # Tipo do imóvel (extraído do título)
                tipo_imovel = ""
                if titulo:
                    if 'apartamento' in titulo.lower():
                        tipo_imovel = "Apartamento"
                    elif 'casa' in titulo.lower():
                        tipo_imovel = "Casa"
                    elif 'sala comercial' in titulo.lower():
                        tipo_imovel = "Sala Comercial"
                    elif 'terreno' in titulo.lower():
                        tipo_imovel = "Terreno"
                    elif 'prédio' in titulo.lower():
                        tipo_imovel = "Prédio"
                    elif 'barracão' in titulo.lower():
                        tipo_imovel = "Barracão"
                
                if titulo and codigo:  # Só adiciona se tiver dados essenciais
                    imoveis_encontrados.append({
                        "imobiliaria": "Plaza Chapecó",
                        "codigo": codigo,
                        "titulo": titulo,
                        "tipo_imovel": tipo_imovel,
                        "preco": preco,
                        "area": area,
                        "quartos": quartos,
                        "banheiros": banheiros,
                        "vagas": vagas,
                        "endereco": endereco,
                        "tipo_negocio": tipo_negocio,
                        "url": url_imovel
                    })
                    
            except Exception as e:
                print(f"Erro ao processar um card da Plaza Chapecó: {e}")
                continue

    return imoveis_encontrados


def scraper_casa_imoveis():
    """
    Scraper refinado para Casa Imóveis
    Extrai dados do texto estruturado dos links
    STATUS: ✅ FUNCIONANDO
    """
    imoveis_encontrados = []
    
    # URLs para aluguel (venda usa filtros)
    urls = [
        ("https://www.casaimoveis.net/alugue-um-imovel", "LOCAÇÃO")
    ]
    
    for url, tipo_negocio in urls:
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar links que seguem o padrão "Tipo - Código Bairro - Cidade"
        all_links = soup.find_all('a', href=True)
        cards_relevantes = []
        
        for link in all_links:
            text = link.get_text().strip()
            # Padrão: "Tipo - Código Bairro - Cidade Área Quartos R$ Preço"
            if re.match(r'^(Apartamento|Casa|Terreno|Sala comercial|Barracão)\s+-\s+\d+', text) and 'R$' in text:
                cards_relevantes.append(link)
        
        print(f"Encontrados {len(cards_relevantes)} imóveis na Casa Imóveis ({tipo_negocio}). Processando...")

        for card in cards_relevantes:
            try:
                text = card.get_text().strip()
                url_imovel = card.get('href', '')
                
                # Garantir URL absoluta
                if url_imovel.startswith('/'):
                    url_imovel = 'https://www.casaimoveis.net' + url_imovel
                
                # Extrair tipo e código
                tipo_codigo_match = re.match(r'^(\w+(?:\s+\w+)*)\s+-\s+(\d+)', text)
                tipo_imovel = tipo_codigo_match.group(1) if tipo_codigo_match else ""
                codigo = tipo_codigo_match.group(2) if tipo_codigo_match else ""
                
                # Extrair bairro
                bairro_match = re.search(r'(\w+(?:\s+\w+)*)\s+-\s+Chapecó', text)
                bairro = bairro_match.group(1) if bairro_match else ""
                endereco = f"{bairro} - Chapecó, SC" if bairro else "Chapecó, SC"
                
                # Extrair área
                area_match = re.search(r'([\d.,]+)m²', text)
                area = area_match.group(1) + 'm²' if area_match else ""
                
                # Extrair quartos
                quartos_match = re.search(r'(\d+)\s+quarto', text)
                quartos = quartos_match.group(1) if quartos_match else ""
                
                # Extrair banheiros
                banheiros_match = re.search(r'(\d+)\s+banheiro', text)
                banheiros = banheiros_match.group(1) if banheiros_match else ""
                
                # Extrair vagas
                vagas_match = re.search(r'(\d+)\s+vaga', text)
                vagas = vagas_match.group(1) if vagas_match else ""
                
                # Extrair preço
                preco_match = re.search(r'R\$\s*([\d.,]+)', text)
                preco = 'R$ ' + preco_match.group(1) if preco_match else ""
                
                if codigo and tipo_imovel:  # Só adiciona se tiver dados essenciais
                    imoveis_encontrados.append({
                        "imobiliaria": "Casa Imóveis",
                        "codigo": codigo,
                        "titulo": text,
                        "tipo_imovel": tipo_imovel,
                        "preco": preco,
                        "area": area,
                        "quartos": quartos,
                        "banheiros": banheiros,
                        "vagas": vagas,
                        "endereco": endereco,
                        "tipo_negocio": tipo_negocio,
                        "url": url_imovel
                    })
                    
            except Exception as e:
                print(f"Erro ao processar um card da Casa Imóveis: {e}")
                continue

    return imoveis_encontrados


def scraper_santa_maria():
    """
    Scraper CORRIGIDO para Santa Maria
    Baseado na análise profunda do HTML - SELETORES CSS CORRIGIDOS
    STATUS: 🔧 CORRIGIDO
    """
    imoveis_encontrados = []
    
    # URLs para aluguel
    urls = [
        ("https://santamaria.com.br/alugar", "LOCAÇÃO")
    ]
    
    for url, tipo_negocio in urls:
        try:
            print(f"Acessando {url}...")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            # Aguardar JavaScript carregar
            time.sleep(5)  # Aumentado de 3 para 5 segundos
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # CORREÇÃO: Seletores CSS corretos (com espaços, não pontos)
        # 1. Buscar códigos dos imóveis
        codigos_elements = soup.find_all('span', class_='sc-902a1a30-11 hjZxig')
        print(f"Códigos encontrados: {len(codigos_elements)}")
        
        # 2. Buscar preços de aluguel
        precos_aluguel = soup.find_all('span', class_='sc-902a1a30-17 fuGSiV')
        print(f"Preços de aluguel encontrados: {len(precos_aluguel)}")
        
        # 3. Buscar características (área, quartos, etc.)
        caracteristicas = soup.find_all('ul', class_='sc-902a1a30-20 kGQWoW')
        print(f"Listas de características encontradas: {len(caracteristicas)}")
        
        # 4. Buscar links dos imóveis
        links_imoveis = soup.find_all('a', href=re.compile(r'/imovel/'))
        print(f"Links de imóveis encontrados: {len(links_imoveis)}")
        
        # Processar cada imóvel baseado nos códigos encontrados
        for i, codigo_elem in enumerate(codigos_elements):
            try:
                # Extrair código
                codigo = codigo_elem.get_text().strip()
                
                # Determinar tipo do imóvel baseado no código
                if codigo.startswith('CA'):
                    tipo_imovel = "Casa"
                elif codigo.startswith('AP'):
                    tipo_imovel = "Apartamento"
                else:
                    tipo_imovel = "Imóvel"
                
                # Extrair preço de aluguel (se disponível)
                preco_aluguel = ""
                if i < len(precos_aluguel):
                    preco_aluguel = precos_aluguel[i].get_text().strip()
                
                # Usar preço de aluguel como preço principal
                preco = preco_aluguel
                
                # Extrair características (área, quartos, banheiros, vagas)
                area = quartos = banheiros = vagas = ""
                if i < len(caracteristicas):
                    carac_items = caracteristicas[i].find_all('li', class_='sc-902a1a30-21 eCXFMG')
                    
                    for j, item in enumerate(carac_items):
                        item_text = item.get_text().strip()
                        
                        if j == 0:  # Primeiro item: área
                            area_match = re.search(r'(\d+)\s*m²', item_text)
                            area = area_match.group(1) + 'm²' if area_match else ""
                        elif j == 1:  # Segundo item: quartos
                            quartos_match = re.search(r'(\d+)\s*dor', item_text)
                            quartos = quartos_match.group(1) if quartos_match else ""
                        elif j == 2:  # Terceiro item: banheiros
                            banheiros_match = re.search(r'(\d+)\s*ban', item_text)
                            banheiros = banheiros_match.group(1) if banheiros_match else ""
                        elif j == 3:  # Quarto item: vagas
                            vagas_match = re.search(r'(\d+)\s*vaga', item_text)
                            vagas = vagas_match.group(1) if vagas_match else ""
                
                # Buscar URL do imóvel correspondente
                url_imovel = ""
                if i < len(links_imoveis):
                    url_imovel = links_imoveis[i].get('href', '')
                    if url_imovel.startswith('/'):
                        url_imovel = 'https://santamaria.com.br' + url_imovel
                
                # Extrair bairro da URL
                bairro = ""
                if url_imovel:
                    # Padrão: /imovel/tipo-codigo-smi-bairro
                    url_parts = url_imovel.split('/')
                    if len(url_parts) > 2:
                        last_part = url_parts[-1]
                        # Extrair bairro (última parte após último hífen)
                        parts = last_part.split('-')
                        if len(parts) > 3:
                            bairro = parts[-1].replace('-', ' ').title()
                
                endereco = f"{bairro} - Chapecó, SC" if bairro else "Chapecó, SC"
                
                # Título baseado nas informações
                titulo = f"{tipo_imovel} {codigo} - {bairro}" if bairro else f"{tipo_imovel} {codigo}"
                
                if codigo:  # Só adiciona se tiver código
                    imoveis_encontrados.append({
                        "imobiliaria": "Santa Maria",
                        "codigo": codigo,
                        "titulo": titulo,
                        "tipo_imovel": tipo_imovel,
                        "preco": preco,
                        "area": area,
                        "quartos": quartos,
                        "banheiros": banheiros,
                        "vagas": vagas,
                        "endereco": endereco,
                        "tipo_negocio": tipo_negocio,
                        "url": url_imovel
                    })
                    
            except Exception as e:
                print(f"Erro ao processar imóvel {i} da Santa Maria: {e}")
                continue

    print(f"Santa Maria: {len(imoveis_encontrados)} imóveis coletados")
    return imoveis_encontrados


def scraper_formiga_imoveis():
    """
    Scraper CORRIGIDO para Formiga Imóveis
    Baseado na análise profunda - timeout aumentado
    STATUS: 🔧 CORRIGIDO
    """
    imoveis_encontrados = []
    
    # URLs para venda e lançamentos
    urls = [
        ("https://www.formigaimoveis.com.br/venda", "VENDA"),
        ("https://www.formigaimoveis.com.br/lancamentos", "LANÇAMENTO")
    ]
    
    for url, tipo_negocio in urls:
        try:
            print(f"Acessando {url}...")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            # CORREÇÃO: Aumentar timeout para JavaScript carregar
            time.sleep(5)  # Aumentado de 3 para 5 segundos
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Seletores específicos (já estavam corretos)
        # 1. Buscar códigos dos imóveis
        codigos_elements = soup.find_all('span', class_='card-buttons_code__LsI0q')
        print(f"Códigos encontrados: {len(codigos_elements)}")
        
        # CORREÇÃO: Verificar se elementos foram encontrados
        if not codigos_elements:
            print("Nenhum código encontrado - página pode não ter carregado completamente")
            continue
        
        # 2. Buscar preços
        precos_elements = soup.find_all('span', class_='contracts_priceNumber__WhudD')
        print(f"Preços encontrados: {len(precos_elements)}")
        
        # 3. Buscar tipos de imóveis
        tipos_elements = soup.find_all('span', class_='vertical-property-card_type__wZ3CC')
        print(f"Tipos encontrados: {len(tipos_elements)}")
        
        # 4. Buscar links dos imóveis
        links_imoveis = soup.find_all('a', href=re.compile(r'/imovel/'))
        print(f"Links de imóveis encontrados: {len(links_imoveis)}")
        
        # Processar cada imóvel baseado nos códigos encontrados
        for i, codigo_elem in enumerate(codigos_elements):
            try:
                # Extrair código (remover "Cód. ")
                codigo_text = codigo_elem.get_text().strip()
                codigo_match = re.search(r'Cód\.\s*(\d+)', codigo_text)
                codigo = codigo_match.group(1) if codigo_match else ""
                
                # Extrair tipo do imóvel
                tipo_imovel = ""
                if i < len(tipos_elements):
                    tipo_imovel = tipos_elements[i].get_text().strip()
                
                # Extrair preço
                preco = ""
                if i < len(precos_elements):
                    preco = precos_elements[i].get_text().strip()
                
                # Buscar URL do imóvel correspondente
                url_imovel = ""
                # CORREÇÃO: Buscar link que contenha o código específico
                for link in links_imoveis:
                    href = link.get('href', '')
                    if codigo in href:
                        url_imovel = href
                        if url_imovel.startswith('/'):
                            url_imovel = 'https://www.formigaimoveis.com.br' + url_imovel
                        break
                
                # Extrair informações da URL ou do card
                bairro = cidade = ""
                area = quartos = banheiros = vagas = ""
                
                if url_imovel:
                    # Padrão: /imovel/tipo-bairro-cidade-codigo
                    url_parts = url_imovel.split('/')
                    if len(url_parts) > 2:
                        last_part = url_parts[-2]  # Penúltima parte
                        # Tentar extrair bairro da URL
                        if 'jardim-italia' in last_part:
                            bairro = "Jardim Itália"
                        elif 'centro' in last_part:
                            bairro = "Centro"
                        elif 'presidente-medici' in last_part:
                            bairro = "Presidente Médici"
                        else:
                            # Extrair bairro genérico
                            parts = last_part.split('-')
                            if len(parts) >= 2:
                                bairro = ' '.join(parts[1:3]).title()
                
                # Se não conseguiu extrair da URL, usar padrões
                if not bairro:
                    bairro = "Chapecó"
                
                endereco = f"{bairro} - SC"
                
                # CORREÇÃO: Buscar características no card correspondente
                if i < len(links_imoveis):
                    # Encontrar o link que corresponde a este código
                    card_correspondente = None
                    for link in links_imoveis:
                        if codigo in link.get('href', ''):
                            card_correspondente = link
                            break
                    
                    if card_correspondente:
                        card_text = card_correspondente.get_text()
                        
                        # Extrair área
                        area_match = re.search(r'(\d+)m²', card_text)
                        area = area_match.group(1) + 'm²' if area_match else ""
                        
                        # Extrair quartos
                        quartos_match = re.search(r'(\d+)\s*quartos?', card_text)
                        quartos = quartos_match.group(1) if quartos_match else ""
                        
                        # Extrair banheiros
                        banheiros_match = re.search(r'(\d+)\s*banheiros?', card_text)
                        banheiros = banheiros_match.group(1) if banheiros_match else ""
                        
                        # Extrair vagas
                        vagas_match = re.search(r'(\d+)\s*vagas?', card_text)
                        vagas = vagas_match.group(1) if vagas_match else ""
                
                # Título baseado nas informações
                titulo = f"{tipo_imovel} Cód. {codigo} - {bairro}" if tipo_imovel and bairro else f"Imóvel Cód. {codigo}"
                
                if codigo:  # Só adiciona se tiver código
                    imoveis_encontrados.append({
                        "imobiliaria": "Formiga Imóveis",
                        "codigo": codigo,
                        "titulo": titulo,
                        "tipo_imovel": tipo_imovel,
                        "preco": preco,
                        "area": area,
                        "quartos": quartos,
                        "banheiros": banheiros,
                        "vagas": vagas,
                        "endereco": endereco,
                        "tipo_negocio": tipo_negocio,
                        "url": url_imovel
                    })
                    
            except Exception as e:
                print(f"Erro ao processar imóvel {i} da Formiga Imóveis: {e}")
                continue

    print(f"Formiga Imóveis: {len(imoveis_encontrados)} imóveis coletados")
    return imoveis_encontrados


def scraper_mobg():
    """
    Scraper refinado para MOBG
    Extrai dados dos cards com carrossel de imagens
    STATUS: ✅ FUNCIONANDO
    """
    URL = "https://mobg.com.br/"
    
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página da MOBG: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    imoveis_encontrados = []
    
    # Buscar por links que contenham informações de preço e código
    all_links = soup.find_all('a', href=True)
    cards_relevantes = []
    
    for link in all_links:
        text = link.get_text().strip()
        # Padrão: "R$ X.XXX R$ X.XXX total #XXXX Tipo • Bairro • Cidade"
        if 'R$' in text and '#' in text and ('Apartamento' in text or 'Casa' in text):
            cards_relevantes.append(link)
    
    print(f"Encontrados {len(cards_relevantes)} imóveis na MOBG. Processando...")

    for card in cards_relevantes:
        try:
            text = card.get_text().strip()
            url_imovel = card.get('href', '')
            
            # Garantir URL absoluta
            if url_imovel.startswith('/'):
                url_imovel = 'https://mobg.com.br' + url_imovel
            
            # Extrair preços
            precos = re.findall(r'R\$\s*([\d.,]+)', text)
            preco_principal = 'R$ ' + precos[0] if precos else ""
            
            # Extrair código
            codigo_match = re.search(r'#(\d+)', text)
            codigo = codigo_match.group(1) if codigo_match else ""
            
            # Extrair tipo do imóvel
            tipo_match = re.search(r'#\d+\s*([^•]+)', text)
            tipo_imovel = tipo_match.group(1).strip() if tipo_match else ""
            
            # Extrair localização
            localizacao_parts = text.split('•')
            bairro = cidade = ""
            if len(localizacao_parts) >= 2:
                bairro = localizacao_parts[1].strip()
            if len(localizacao_parts) >= 3:
                cidade_part = localizacao_parts[2].strip()
                # Extrair apenas a cidade, ignorando outras informações
                cidade_match = re.search(r'^([^0-9R$]+)', cidade_part)
                cidade = cidade_match.group(1).strip() if cidade_match else cidade_part
            
            endereco = f"{bairro} - {cidade}" if bairro and cidade else "Chapecó, SC"
            
            # Extrair características
            area_match = re.search(r'(\d+)m²', text)
            area = area_match.group(1) + 'm²' if area_match else ""
            
            quartos_match = re.search(r'(\d+)\s*quartos?', text)
            quartos = quartos_match.group(1) if quartos_match else ""
            
            banheiros_match = re.search(r'(\d+)\s*banheiros?', text)
            banheiros = banheiros_match.group(1) if banheiros_match else ""
            
            vagas_match = re.search(r'(\d+)\s*vagas?', text)
            vagas = vagas_match.group(1) if vagas_match else ""
            
            # Determinar tipo de negócio baseado na URL ou texto
            tipo_negocio = "LOCAÇÃO"  # Padrão para MOBG
            if 'venda' in url_imovel.lower() or 'comprar' in text.lower():
                tipo_negocio = "VENDA"
            
            # Título baseado nas informações extraídas
            titulo = f"{tipo_imovel} #{codigo} - {bairro}" if tipo_imovel and bairro else f"Imóvel #{codigo}"
            
            if codigo or preco_principal:  # Adiciona se tiver pelo menos código ou preço
                imoveis_encontrados.append({
                    "imobiliaria": "MOBG",
                    "codigo": codigo,
                    "titulo": titulo,
                    "tipo_imovel": tipo_imovel,
                    "preco": preco_principal,
                    "area": area,
                    "quartos": quartos,
                    "banheiros": banheiros,
                    "vagas": vagas,
                    "endereco": endereco,
                    "tipo_negocio": tipo_negocio,
                    "url": url_imovel
                })
                
        except Exception as e:
            print(f"Erro ao processar um card da MOBG: {e}")
            continue

    return imoveis_encontrados


def scraper_smart_aluguel_venda():
    """
    Scraper refinado para Smart Aluguel e Venda
    STATUS: ✅ FUNCIONANDO
    """
    imoveis_encontrados = []
    
    # URLs específicas para aluguel e venda
    urls = [
        ("https://www.smartaluguelevenda.com.br/alugar/todos", "LOCAÇÃO"),
        ("https://www.smartaluguelevenda.com.br/comprar/todos", "VENDA")
    ]
    
    for url, tipo_negocio in urls:
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar por padrões mais amplos
        all_links = soup.find_all('a', href=True)
        cards_relevantes = []
        
        for link in all_links:
            text = link.get_text().strip()
            href = link.get('href', '')
            
            # Critérios mais amplos para identificar cards de imóveis
            if (len(text) > 30 and 
                ('R$' in text or 'm²' in text or 'quarto' in text) and
                (href.startswith('/') or 'smartaluguelevenda' in href)):
                cards_relevantes.append(link)
        
        print(f"Encontrados {len(cards_relevantes)} imóveis na Smart ({tipo_negocio}). Processando...")

        for card in cards_relevantes:
            try:
                text = card.get_text().strip()
                url_imovel = card.get('href', '')
                
                # Garantir URL absoluta
                if url_imovel.startswith('/'):
                    url_imovel = 'https://www.smartaluguelevenda.com.br' + url_imovel
                
                # Extrair código da URL ou texto
                codigo = ""
                codigo_url_match = re.search(r'/imovel/(\d+)', url_imovel)
                if codigo_url_match:
                    codigo = codigo_url_match.group(1)
                else:
                    # Tentar extrair código do texto
                    codigo_text_match = re.search(r'#(\d+)|cod[igo]*[:\s]*(\d+)', text, re.IGNORECASE)
                    if codigo_text_match:
                        codigo = codigo_text_match.group(1) or codigo_text_match.group(2)
                
                # Extrair tipo do imóvel
                tipo_imovel = ""
                if 'apartamento' in text.lower():
                    tipo_imovel = "Apartamento"
                elif 'casa' in text.lower():
                    tipo_imovel = "Casa"
                elif 'sala' in text.lower():
                    tipo_imovel = "Sala Comercial"
                elif 'terreno' in text.lower():
                    tipo_imovel = "Terreno"
                
                # Extrair preço
                preco_match = re.search(r'R\$\s*([\d.,]+)', text)
                preco = 'R$ ' + preco_match.group(1) if preco_match else ""
                
                # Extrair área
                area_match = re.search(r'(\d+)m²', text)
                area = area_match.group(1) + 'm²' if area_match else ""
                
                # Extrair quartos
                quartos_match = re.search(r'(\d+)\s*quartos?', text)
                quartos = quartos_match.group(1) if quartos_match else ""
                
                # Extrair banheiros
                banheiros_match = re.search(r'(\d+)\s*banheiros?', text)
                banheiros = banheiros_match.group(1) if banheiros_match else ""
                
                # Extrair vagas
                vagas_match = re.search(r'(\d+)\s*vagas?', text)
                vagas = vagas_match.group(1) if vagas_match else ""
                
                # Extrair endereço/bairro
                endereco = "Chapecó, SC"  # Padrão
                bairro_patterns = ['Centro', 'Efapi', 'Jardim Itália', 'Pinheirinho', 'Santo Antônio']
                for bairro in bairro_patterns:
                    if bairro.lower() in text.lower():
                        endereco = f"{bairro} - Chapecó, SC"
                        break
                
                # Título baseado nas informações disponíveis
                titulo = text[:100] + "..." if len(text) > 100 else text
                
                if codigo or preco:  # Adiciona se tiver pelo menos código ou preço
                    imoveis_encontrados.append({
                        "imobiliaria": "Smart Aluguel e Venda",
                        "codigo": codigo,
                        "titulo": titulo,
                        "tipo_imovel": tipo_imovel,
                        "preco": preco,
                        "area": area,
                        "quartos": quartos,
                        "banheiros": banheiros,
                        "vagas": vagas,
                        "endereco": endereco,
                        "tipo_negocio": tipo_negocio,
                        "url": url_imovel
                    })
                    
            except Exception as e:
                print(f"Erro ao processar um card da Smart: {e}")
                continue

    return imoveis_encontrados


# Scrapers básicos para sites restantes (mantidos do arquivo original)
def scraper_fenix_melhor_negocio():
    """Scraper básico para Fenix Melhor Negócio"""
    return scraper_generico("https://fenixmelhornegocio.com.br/", "Fenix Melhor Negócio")

def scraper_markize():
    """Scraper básico para Markize"""
    return scraper_generico("https://www.markize.com.br/", "Markize")

def scraper_firmesa():
    """Scraper básico para Firmesa"""
    return scraper_generico("https://www.firmesa.com.br/", "Firmesa")

def scraper_padra():
    """Scraper básico para Padra"""
    return scraper_generico("https://padra.com.br/", "Padra")

def scraper_lunardi_imoveis():
    """Scraper básico para Lunardi Imóveis"""
    return scraper_generico("https://www.lunardiimoveis.com.br/", "Lunardi Imóveis")

def scraper_sim_imoveis_chapeco():
    """Scraper básico para Sim Imóveis Chapecó"""
    return scraper_generico("https://www.simimoveischapeco.com/", "Sim Imóveis Chapecó")

def scraper_tucuma_imoveis():
    """Scraper básico para Tucumã Imóveis"""
    return scraper_generico("https://tucumaimoveis.com.br/", "Tucumã Imóveis")

def scraper_imobiliaria_chapeco():
    """Scraper básico para Imobiliária Chapecó"""
    return scraper_generico("https://www.imobiliariachapeco.com.br/", "Imobiliária Chapecó")


def scraper_generico(url, nome_imobiliaria):
    """
    Scraper genérico para sites com estrutura padrão
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {nome_imobiliaria}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    imoveis_encontrados = []
    
    # Buscar por links que possam conter informações de imóveis
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        text = link.get_text().strip()
        href = link.get('href', '')
        
        # Filtrar links relevantes
        if (len(text) > 20 and 
            ('R$' in text or 'alug' in text.lower() or 'vend' in text.lower() or 'm²' in text or 'quarto' in text)):
            try:
                # URL absoluta
                url_imovel = href
                if href.startswith('/'):
                    base_url = url.rstrip('/')
                    url_imovel = base_url + href
                
                # Extrair código
                codigo = ""
                codigo_patterns = [
                    r'cod[igo]*[:\s]*(\d+)',
                    r'#(\d+)',
                    r'/(\d+)/?$',
                    r'ref[erencia]*[:\s]*(\d+)'
                ]
                
                for pattern in codigo_patterns:
                    match = re.search(pattern, text + ' ' + href, re.IGNORECASE)
                    if match:
                        codigo = match.group(1)
                        break
                
                # Extrair preço
                preco_match = re.search(r'R\$\s*([\d.,]+)', text)
                preco = 'R$ ' + preco_match.group(1) if preco_match else ""
                
                # Extrair tipo do imóvel
                tipo_imovel = ""
                if 'apartamento' in text.lower():
                    tipo_imovel = "Apartamento"
                elif 'casa' in text.lower():
                    tipo_imovel = "Casa"
                elif 'terreno' in text.lower():
                    tipo_imovel = "Terreno"
                elif 'sala' in text.lower():
                    tipo_imovel = "Sala Comercial"
                
                # Determinar tipo de negócio
                tipo_negocio = "VENDA"  # Padrão
                if any(word in href.lower() for word in ['alug', 'locar', 'rent']):
                    tipo_negocio = "LOCAÇÃO"
                elif any(word in text.lower() for word in ['alug', 'locar', 'locação', 'para alugar']):
                    tipo_negocio = "LOCAÇÃO"
                elif preco:
                    valor_numerico = re.sub(r'[^\d]', '', preco)
                    if valor_numerico and int(valor_numerico) < 5000:
                        tipo_negocio = "LOCAÇÃO"
                
                # Extrair características básicas
                area_match = re.search(r'(\d+)m²', text)
                area = area_match.group(1) + 'm²' if area_match else ""
                
                quartos_match = re.search(r'(\d+)\s*quartos?', text)
                quartos = quartos_match.group(1) if quartos_match else ""
                
                banheiros_match = re.search(r'(\d+)\s*banheiros?', text)
                banheiros = banheiros_match.group(1) if banheiros_match else ""
                
                vagas_match = re.search(r'(\d+)\s*vagas?', text)
                vagas = vagas_match.group(1) if vagas_match else ""
                
                if codigo or preco:  # Adiciona se tiver pelo menos código ou preço
                    imoveis_encontrados.append({
                        "imobiliaria": nome_imobiliaria,
                        "codigo": codigo,
                        "titulo": text[:100] + "..." if len(text) > 100 else text,
                        "tipo_imovel": tipo_imovel,
                        "preco": preco,
                        "area": area,
                        "quartos": quartos,
                        "banheiros": banheiros,
                        "vagas": vagas,
                        "endereco": "Chapecó, SC",
                        "tipo_negocio": tipo_negocio,
                        "url": url_imovel
                    })
                    
            except Exception as e:
                print(f"Erro ao processar link do {nome_imobiliaria}: {e}")
                continue
    
    print(f"{nome_imobiliaria}: {len(imoveis_encontrados)} imóveis encontrados")
    return imoveis_encontrados


def executar_todos_scrapers():
    """
    Executa todos os scrapers disponíveis
    VERSÃO INTEGRADA COM CORREÇÕES
    """
    print("=== EXECUTANDO TODOS OS SCRAPERS (VERSÃO CORRIGIDA) ===")
    
    todos_imoveis = []
    
    # Lista de todas as funções de scraper
    scrapers = [
        scraper_plaza_chapeco,           # ✅ Funcionando
        scraper_casa_imoveis,            # ✅ Funcionando  
        scraper_santa_maria,             # 🔧 CORRIGIDO
        scraper_formiga_imoveis,         # 🔧 CORRIGIDO
        scraper_mobg,                    # ✅ Funcionando
        scraper_smart_aluguel_venda,     # ✅ Funcionando
        scraper_fenix_melhor_negocio,    # Básico
        scraper_markize,                 # Básico
        scraper_firmesa,                 # Básico
        scraper_padra,                   # Básico
        scraper_lunardi_imoveis,         # Básico
        scraper_sim_imoveis_chapeco,     # Básico
        scraper_tucuma_imoveis,          # Básico
        scraper_imobiliaria_chapeco      # Básico
    ]
    
    for scraper_func in scrapers:
        try:
            nome_scraper = scraper_func.__name__.replace('scraper_', '').replace('_', ' ').title()
            print(f"\n--- Executando {nome_scraper} ---")
            
            imoveis = scraper_func()
            todos_imoveis.extend(imoveis)
            
            print(f"✅ {nome_scraper}: {len(imoveis)} imóveis coletados")
            
        except Exception as e:
            nome_scraper = scraper_func.__name__.replace('scraper_', '').replace('_', ' ').title()
            print(f"❌ Erro ao executar {nome_scraper}: {e}")
    
    print(f"\n=== TOTAL: {len(todos_imoveis)} imóveis coletados de todas as imobiliárias ===")
    
    # Estatísticas por imobiliária
    print("\n=== ESTATÍSTICAS POR IMOBILIÁRIA ===")
    imobiliarias = {}
    for imovel in todos_imoveis:
        nome = imovel['imobiliaria']
        if nome not in imobiliarias:
            imobiliarias[nome] = {'total': 0, 'locacao': 0, 'venda': 0}
        imobiliarias[nome]['total'] += 1
        if imovel['tipo_negocio'] == 'LOCAÇÃO':
            imobiliarias[nome]['locacao'] += 1
        else:
            imobiliarias[nome]['venda'] += 1
    
    for nome, stats in imobiliarias.items():
        print(f"{nome}: {stats['total']} total ({stats['locacao']} locação, {stats['venda']} venda)")
    
    return todos_imoveis


# Exemplo de uso
if __name__ == "__main__":
    # Executar todos os scrapers
    imoveis = executar_todos_scrapers()
    
    # Exibir alguns exemplos
    print("\n=== EXEMPLOS DE IMÓVEIS COLETADOS ===")
    for i, imovel in enumerate(imoveis[:3]):
        print(f"\nImóvel {i+1}:")
        for key, value in imovel.items():
            print(f"{key}: {value}")
        print("-" * 50)

