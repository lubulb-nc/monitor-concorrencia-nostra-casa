import requests
from bs4 import BeautifulSoup
import re
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HEADERS mais robustos
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def scraper_plaza_chapeco():
    """Scraper corrigido para Plaza Chapecó"""
    logger.info("🔍 Iniciando scraper Plaza Chapecó...")
    imoveis_encontrados = []
    
    # URLs corretas identificadas
    urls = [
        ("https://plazachapeco.com.br/alugar-imoveis-chapeco-sc/", "LOCAÇÃO"),
        ("https://plazachapeco.com.br/comprar-imoveis-chapeco-sc/", "VENDA")
    ]
    
    for url, tipo_negocio in urls:
        try:
            logger.info(f"📡 Acessando: {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Seletor correto identificado
            cards_de_imoveis = soup.select('a[href*="/imovel/"]')
            logger.info(f"✅ Plaza Chapecó ({tipo_negocio}): {len(cards_de_imoveis)} imóveis encontrados")
            
            for card in cards_de_imoveis:
                try:
                    # URL completa
                    url_imovel = card.get('href', '')
                    if url_imovel.startswith('/'):
                        url_imovel = 'https://plazachapeco.com.br' + url_imovel
                    
                    # Código do imóvel (extraído da URL)
                    codigo_match = re.search(r'/imovel/(\d+)/', url_imovel)
                    codigo = codigo_match.group(1) if codigo_match else ""
                    
                    # Título
                    titulo_elem = card.find(class_='chamadaimovel')
                    titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                    
                    # Preço
                    preco_elem = card.find(class_='valor')
                    preco = preco_elem.get_text(strip=True) if preco_elem else ""
                    
                    # Características (área, quartos, etc.)
                    caracteristicas = card.find(class_='caracteristicas')
                    area = quartos = banheiros = vagas = ""
                    
                    if caracteristicas:
                        texto_carac = caracteristicas.get_text()
                        
                        # Extrair área
                        area_match = re.search(r'(\d+)m²', texto_carac)
                        area = area_match.group(1) + "m²" if area_match else ""
                        
                        # Extrair quartos
                        quartos_match = re.search(r'(\d+)\s*quartos?', texto_carac)
                        quartos = quartos_match.group(1) if quartos_match else ""
                        
                        # Extrair banheiros
                        banheiros_match = re.search(r'(\d+)\s*banheiros?', texto_carac)
                        banheiros = banheiros_match.group(1) if banheiros_match else ""
                        
                        # Extrair vagas
                        vagas_match = re.search(r'(\d+)\s*vagas?', texto_carac)
                        vagas = vagas_match.group(1) if vagas_match else ""
                    
                    # Endereço/Bairro
                    endereco_elem = card.find(class_='endereco')
                    endereco = endereco_elem.get_text(strip=True) if endereco_elem else ""
                    
                    # Tipo de imóvel (extraído do título)
                    tipo_imovel = ""
                    if titulo:
                        if 'apartamento' in titulo.lower():
                            tipo_imovel = "Apartamento"
                        elif 'casa' in titulo.lower():
                            tipo_imovel = "Casa"
                        elif 'terreno' in titulo.lower():
                            tipo_imovel = "Terreno"
                        elif 'comercial' in titulo.lower() or 'sala' in titulo.lower():
                            tipo_imovel = "Comercial"
                    
                    if codigo and titulo:  # Só adicionar se tiver dados mínimos
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
                    logger.error(f"❌ Erro ao processar card Plaza Chapecó: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Erro ao acessar Plaza Chapecó ({tipo_negocio}): {e}")
            continue
    
    logger.info(f"✅ Plaza Chapecó finalizado: {len(imoveis_encontrados)} imóveis coletados")
    return imoveis_encontrados

def scraper_santa_maria():
    """Scraper corrigido para Santa Maria"""
    logger.info("🔍 Iniciando scraper Santa Maria...")
    imoveis_encontrados = []
    
    # URLs corretas identificadas
    urls = [
        ("https://santamaria.com.br/alugar", "LOCAÇÃO"),
        ("https://santamaria.com.br/comprar", "VENDA")
    ]
    
    for url, tipo_negocio in urls:
        try:
            logger.info(f"📡 Acessando: {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar cards de imóveis (vários seletores possíveis)
            cards_de_imoveis = []
            seletores = [
                '.card-imovel',
                '.imovel-card', 
                '.property-card',
                'a[href*="/imovel/"]',
                '.resultado-item'
            ]
            
            for seletor in seletores:
                cards = soup.select(seletor)
                if cards:
                    cards_de_imoveis = cards
                    logger.info(f"✅ Santa Maria ({tipo_negocio}): {len(cards)} imóveis encontrados com seletor '{seletor}'")
                    break
            
            if not cards_de_imoveis:
                logger.warning(f"⚠️ Santa Maria ({tipo_negocio}): Nenhum imóvel encontrado")
                continue
            
            for card in cards_de_imoveis[:10]:  # Limitar a 10 para teste
                try:
                    # Tentar extrair dados básicos
                    titulo = ""
                    preco = ""
                    codigo = ""
                    url_imovel = ""
                    
                    # Buscar título
                    titulo_selectors = ['.titulo', '.title', 'h3', 'h4', '.nome']
                    for sel in titulo_selectors:
                        elem = card.select_one(sel)
                        if elem:
                            titulo = elem.get_text(strip=True)
                            break
                    
                    # Buscar preço
                    preco_selectors = ['.preco', '.price', '.valor', '.value']
                    for sel in preco_selectors:
                        elem = card.select_one(sel)
                        if elem:
                            preco = elem.get_text(strip=True)
                            break
                    
                    # Buscar URL
                    link = card if card.name == 'a' else card.find('a')
                    if link:
                        url_imovel = link.get('href', '')
                        if url_imovel.startswith('/'):
                            url_imovel = 'https://santamaria.com.br' + url_imovel
                        
                        # Extrair código da URL
                        codigo_match = re.search(r'/(\w+)/?$', url_imovel)
                        codigo = codigo_match.group(1) if codigo_match else ""
                    
                    if titulo or preco:  # Se encontrou pelo menos título ou preço
                        imoveis_encontrados.append({
                            "imobiliaria": "Santa Maria",
                            "codigo": codigo or f"SM_{len(imoveis_encontrados)+1}",
                            "titulo": titulo or "Imóvel Santa Maria",
                            "tipo_imovel": "",
                            "preco": preco,
                            "area": "",
                            "quartos": "",
                            "banheiros": "",
                            "vagas": "",
                            "endereco": "",
                            "tipo_negocio": tipo_negocio,
                            "url": url_imovel
                        })
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao processar card Santa Maria: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Erro ao acessar Santa Maria ({tipo_negocio}): {e}")
            continue
    
    logger.info(f"✅ Santa Maria finalizado: {len(imoveis_encontrados)} imóveis coletados")
    return imoveis_encontrados

def executar_todos_scrapers():
    """Executa todos os scrapers corrigidos"""
    logger.info("🚀 Iniciando execução de todos os scrapers...")
    
    todos_imoveis = []
    
    # Lista de scrapers funcionais
    scrapers = [
        scraper_plaza_chapeco,
        scraper_santa_maria
    ]
    
    for scraper_func in scrapers:
        try:
            nome_scraper = scraper_func.__name__.replace('scraper_', '').replace('_', ' ').title()
            logger.info(f"\n--- Executando {nome_scraper} ---")
            
            imoveis = scraper_func()
            todos_imoveis.extend(imoveis)
            
            logger.info(f"✅ {nome_scraper}: {len(imoveis)} imóveis coletados")
            
            # Pausa entre scrapers
            time.sleep(2)
            
        except Exception as e:
            nome_scraper = scraper_func.__name__.replace('scraper_', '').replace('_', ' ').title()
            logger.error(f"❌ Erro ao executar {nome_scraper}: {e}")
    
    logger.info(f"\n=== TOTAL: {len(todos_imoveis)} imóveis coletados ===")
    
    # Estatísticas
    if todos_imoveis:
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
        
        logger.info("\n=== ESTATÍSTICAS ===")
        for nome, stats in imobiliarias.items():
            logger.info(f"{nome}: {stats['total']} total ({stats['locacao']} locação, {stats['venda']} venda)")
    
    return todos_imoveis

if __name__ == "__main__":
    imoveis = executar_todos_scrapers()
    
    if imoveis:
        logger.info("\n=== EXEMPLOS ===")
        for i, imovel in enumerate(imoveis[:3]):
            logger.info(f"\nImóvel {i+1}:")
            for key, value in imovel.items():
                logger.info(f"  {key}: {value}")

