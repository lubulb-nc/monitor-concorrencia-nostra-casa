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
    """Scraper FUNCIONAL para Plaza Chapecó com seletores corretos"""
    logger.info("🔍 Iniciando scraper Plaza Chapecó...")
    imoveis_encontrados = []
    
    # URLs corretas confirmadas
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
            
            # SELETOR CORRETO CONFIRMADO
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
                    
                    # TÍTULO - Extrair do texto completo do card
                    texto_completo = card.get_text(strip=True)
                    
                    # Separar título do resto (antes do preço)
                    if 'R$' in texto_completo:
                        titulo = texto_completo.split('R$')[0].strip()
                        # Limpar título (remover características)
                        if '·' in titulo:
                            titulo = titulo.split('·')[0].strip()
                    else:
                        titulo = texto_completo[:100].strip()  # Primeiros 100 chars
                    
                    # PREÇO - Seletor correto identificado
                    preco_elem = card.select_one('[class*="valor"]')
                    preco = preco_elem.get_text(strip=True) if preco_elem else ""
                    
                    # ENDEREÇO - Seletor correto identificado
                    endereco_elem = card.select_one('[class*="endereco"]')
                    endereco = endereco_elem.get_text(strip=True) if endereco_elem else ""
                    
                    # CARACTERÍSTICAS - Extrair do texto
                    area = quartos = banheiros = vagas = ""
                    
                    # Buscar padrões no texto completo
                    area_match = re.search(r'(\d+)m²', texto_completo)
                    area = area_match.group(0) if area_match else ""
                    
                    quartos_match = re.search(r'(\d+)\s*quartos?', texto_completo)
                    quartos = quartos_match.group(1) if quartos_match else ""
                    
                    banheiros_match = re.search(r'(\d+)\s*banheiros?', texto_completo)
                    banheiros = banheiros_match.group(1) if banheiros_match else ""
                    
                    vagas_match = re.search(r'(\d+)\s*vagas?', texto_completo)
                    vagas = vagas_match.group(1) if vagas_match else ""
                    
                    # TIPO DE IMÓVEL - Extrair do título
                    tipo_imovel = ""
                    titulo_lower = titulo.lower()
                    if 'apartamento' in titulo_lower:
                        tipo_imovel = "Apartamento"
                    elif 'casa' in titulo_lower:
                        tipo_imovel = "Casa"
                    elif 'terreno' in titulo_lower:
                        tipo_imovel = "Terreno"
                    elif 'comercial' in titulo_lower or 'sala' in titulo_lower:
                        tipo_imovel = "Comercial"
                    elif 'barracão' in titulo_lower:
                        tipo_imovel = "Barracão"
                    
                    # Só adicionar se tiver dados mínimos
                    if codigo and titulo and len(titulo) > 10:
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
    """Scraper FUNCIONAL para Santa Maria com URLs corretas"""
    logger.info("🔍 Iniciando scraper Santa Maria...")
    imoveis_encontrados = []
    
    # URLs CORRETAS identificadas
    urls = [
        ("https://santamaria.com.br/alugar", "LOCAÇÃO"),
        ("https://santamaria.com.br/comprar-prontos", "VENDA")  # URL corrigida!
    ]
    
    for url, tipo_negocio in urls:
        try:
            logger.info(f"📡 Acessando: {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # AGUARDAR CARREGAMENTO (site usa JavaScript)
            time.sleep(3)
            
            # SELETORES CORRETOS identificados
            # Primeiro tentar articles
            cards_de_imoveis = soup.select('article')
            
            if not cards_de_imoveis:
                # Fallback: tentar links de imóveis
                cards_de_imoveis = soup.select('a[href*="/imovel"]')
            
            logger.info(f"✅ Santa Maria ({tipo_negocio}): {len(cards_de_imoveis)} elementos encontrados")
            
            # Processar apenas primeiros 10 para evitar sobrecarga
            for i, card in enumerate(cards_de_imoveis[:10]):
                try:
                    # EXTRAIR URL DO IMÓVEL
                    url_imovel = ""
                    if card.name == 'a':
                        url_imovel = card.get('href', '')
                    else:
                        link = card.find('a')
                        if link:
                            url_imovel = link.get('href', '')
                    
                    if url_imovel and url_imovel.startswith('/'):
                        url_imovel = 'https://santamaria.com.br' + url_imovel
                    
                    # CÓDIGO DO IMÓVEL (extrair da URL)
                    codigo = ""
                    if url_imovel:
                        codigo_match = re.search(r'/imovel/[^/]+-([^/]+)/?$', url_imovel)
                        if codigo_match:
                            codigo = codigo_match.group(1)
                        else:
                            # Fallback: usar parte final da URL
                            codigo = url_imovel.split('/')[-1] or f"SM_{i+1}"
                    else:
                        codigo = f"SM_{i+1}"
                    
                    # TÍTULO - Tentar extrair do card
                    titulo = ""
                    titulo_selectors = ['h1', 'h2', 'h3', 'h4', '.titulo', '.title']
                    for sel in titulo_selectors:
                        elem = card.select_one(sel)
                        if elem:
                            titulo = elem.get_text(strip=True)
                            break
                    
                    if not titulo:
                        # Fallback: usar texto do card (limitado)
                        texto = card.get_text(strip=True)
                        if texto:
                            titulo = texto[:50].strip() + "..."
                        else:
                            titulo = f"Imóvel Santa Maria {tipo_negocio}"
                    
                    # PREÇO - Tentar extrair
                    preco = ""
                    preco_selectors = ['.preco', '.valor', '.price', '[class*="preco"]', '[class*="valor"]']
                    for sel in preco_selectors:
                        elem = card.select_one(sel)
                        if elem:
                            preco = elem.get_text(strip=True)
                            break
                    
                    # ENDEREÇO - Tentar extrair
                    endereco = ""
                    endereco_selectors = ['.endereco', '.localizacao', '.bairro']
                    for sel in endereco_selectors:
                        elem = card.select_one(sel)
                        if elem:
                            endereco = elem.get_text(strip=True)
                            break
                    
                    # TIPO DE IMÓVEL - Inferir do título ou URL
                    tipo_imovel = ""
                    texto_analise = (titulo + " " + url_imovel).lower()
                    if 'apartamento' in texto_analise:
                        tipo_imovel = "Apartamento"
                    elif 'casa' in texto_analise:
                        tipo_imovel = "Casa"
                    elif 'terreno' in texto_analise:
                        tipo_imovel = "Terreno"
                    elif 'comercial' in texto_analise or 'sala' in texto_analise:
                        tipo_imovel = "Comercial"
                    elif 'sobrado' in texto_analise:
                        tipo_imovel = "Sobrado"
                    
                    # Só adicionar se tiver dados mínimos
                    if codigo and titulo:
                        imoveis_encontrados.append({
                            "imobiliaria": "Santa Maria",
                            "codigo": codigo,
                            "titulo": titulo,
                            "tipo_imovel": tipo_imovel,
                            "preco": preco,
                            "area": "",  # Difícil extrair sem JavaScript
                            "quartos": "",
                            "banheiros": "",
                            "vagas": "",
                            "endereco": endereco,
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
    """Executa todos os scrapers FUNCIONAIS"""
    logger.info("🚀 Iniciando execução de todos os scrapers FUNCIONAIS...")
    
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
    
    # Estatísticas detalhadas
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
        
        logger.info("\n=== ESTATÍSTICAS DETALHADAS ===")
        for nome, stats in imobiliarias.items():
            logger.info(f"{nome}: {stats['total']} total ({stats['locacao']} locação, {stats['venda']} venda)")
    
    return todos_imoveis

if __name__ == "__main__":
    imoveis = executar_todos_scrapers()
    
    if imoveis:
        logger.info("\n=== EXEMPLOS DE IMÓVEIS COLETADOS ===")
        for i, imovel in enumerate(imoveis[:3]):
            logger.info(f"\nImóvel {i+1} ({imovel['imobiliaria']}):")
            for key, value in imovel.items():
                if value:  # Só mostrar campos preenchidos
                    logger.info(f"  {key}: {value}")
    else:
        logger.warning("❌ Nenhum imóvel foi coletado!")

