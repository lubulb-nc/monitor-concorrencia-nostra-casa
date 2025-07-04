from flask import Blueprint, jsonify, request, current_app
from src.database import db
from src.models.imovel import Imovel, ExecucaoScraper
from src.scrapers_gerais import executar_todos_scrapers
import threading
import time
import traceback
import json
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

monitor_bp = Blueprint('monitor', __name__)

# Variável global para controlar execução dos scrapers
scraper_em_execucao = False
ultimo_resultado = []

@monitor_bp.route('/executar-monitoramento', methods=['POST'])
def executar_monitoramento():
    """Executa todos os scrapers e atualiza o banco de dados"""
    global scraper_em_execucao, ultimo_resultado
    
    if scraper_em_execucao:
        return jsonify({
            'status': 'erro',
            'mensagem': 'Monitoramento já está em execução'
        }), 400
    
    # Executar scrapers em thread separada
    app = current_app._get_current_object()  # Obter referência da aplicação atual
    thread = threading.Thread(target=executar_scrapers_background, args=(app,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'sucesso',
        'mensagem': 'Monitoramento iniciado'
    })

@monitor_bp.route('/status-monitoramento', methods=['GET'])
def status_monitoramento():
    """Retorna o status atual do monitoramento"""
    global scraper_em_execucao, ultimo_resultado
    
    # Buscar última execução no banco
    try:
        ultima_execucao = ExecucaoScraper.query.order_by(ExecucaoScraper.data_execucao.desc()).first()
        
        return jsonify({
            'em_execucao': scraper_em_execucao,
            'ultimo_resultado': ultimo_resultado,
            'ultima_execucao': ultima_execucao.to_dict() if ultima_execucao else None
        })
    except Exception as e:
        return jsonify({
            'em_execucao': scraper_em_execucao,
            'ultimo_resultado': ultimo_resultado,
            'ultima_execucao': None,
            'erro': str(e)
        })

@monitor_bp.route('/imoveis', methods=['GET'])
def listar_imoveis():
    """Lista imóveis com filtros opcionais"""
    try:
        # Parâmetros de filtro
        tipo_negocio = request.args.get('tipo_negocio')
        tipo_imovel = request.args.get('tipo_imovel')
        bairro = request.args.get('bairro')
        imobiliaria = request.args.get('imobiliaria')
        apenas_novos = request.args.get('apenas_novos', 'false').lower() == 'true'
        
        # SOLUÇÃO ALTERNATIVA: Carregar imóveis do arquivo JSON se o banco estiver vazio
        imoveis_do_banco = Imovel.query.filter(Imovel.ativo == True).count()
        
        if imoveis_do_banco == 0:
            # Tentar carregar do arquivo JSON
            try:
                with open('imoveis_coletados.json', 'r', encoding='utf-8') as f:
                    imoveis_json = json.load(f)
                
                # Filtrar imóveis do JSON conforme os parâmetros
                imoveis_filtrados = []
                
                for imovel in imoveis_json:
                    # Aplicar filtros
                    incluir = True
                    
                    if tipo_negocio and tipo_negocio != 'Todos':
                        if tipo_negocio == 'Locação' and imovel.get('tipo_negocio') != 'LOCAÇÃO':
                            incluir = False
                        elif tipo_negocio == 'Vendas' and imovel.get('tipo_negocio') != 'VENDA':
                            incluir = False
                    
                    if incluir and tipo_imovel and tipo_imovel != 'Todos':
                        if not imovel.get('tipo_imovel') or tipo_imovel.lower() not in imovel.get('tipo_imovel', '').lower():
                            incluir = False
                    
                    if incluir and bairro and bairro != 'Todos':
                        if not imovel.get('endereco') or bairro.lower() not in imovel.get('endereco', '').lower():
                            incluir = False
                    
                    if incluir and imobiliaria and imobiliaria != 'Todas':
                        if imovel.get('imobiliaria') != imobiliaria:
                            incluir = False
                    
                    # Adicionar à lista filtrada
                    if incluir:
                        # Adicionar campos necessários para compatibilidade
                        imovel['id'] = imovel.get('codigo', '0')
                        imovel['data_coleta'] = datetime.utcnow().isoformat()
                        imovel['ativo'] = True
                        imoveis_filtrados.append(imovel)
                
                # Ordenar por data (mais recentes primeiro)
                imoveis_filtrados.sort(key=lambda x: x.get('data_coleta', ''), reverse=True)
                
                # Limitar a 50 resultados
                imoveis_filtrados = imoveis_filtrados[:50]
                
                return jsonify({
                    'status': 'sucesso',
                    'total': len(imoveis_filtrados),
                    'imoveis': imoveis_filtrados,
                    'fonte': 'json'  # Indicar que veio do JSON
                })
                
            except (FileNotFoundError, json.JSONDecodeError) as e:
                # Se não conseguir carregar do JSON, retornar lista vazia
                return jsonify({
                    'status': 'sucesso',
                    'total': 0,
                    'imoveis': [],
                    'erro': f"Arquivo JSON não encontrado ou inválido: {str(e)}"
                })
        
        # FLUXO NORMAL: Buscar do banco de dados
        # Query base
        query = Imovel.query.filter(Imovel.ativo == True)
        
        # Aplicar filtros
        if tipo_negocio and tipo_negocio != 'Todos':
            if tipo_negocio == 'Locação':
                query = query.filter(Imovel.tipo_negocio == 'LOCAÇÃO')
            elif tipo_negocio == 'Vendas':
                query = query.filter(Imovel.tipo_negocio == 'VENDA')
        
        if tipo_imovel and tipo_imovel != 'Todos':
            query = query.filter(Imovel.tipo_imovel.ilike(f'%{tipo_imovel}%'))
        
        if bairro and bairro != 'Todos':
            query = query.filter(Imovel.endereco.ilike(f'%{bairro}%'))
        
        if imobiliaria and imobiliaria != 'Todas':
            query = query.filter(Imovel.imobiliaria == imobiliaria)
        
        # Filtro para imóveis novos (últimas 24 horas)
        if apenas_novos:
            ontem = datetime.utcnow() - timedelta(days=1)
            query = query.filter(Imovel.data_coleta >= ontem)
        
        # Ordenar por data de coleta (mais recentes primeiro)
        imoveis = query.order_by(Imovel.data_coleta.desc()).limit(50).all()
        
        return jsonify({
            'status': 'sucesso',
            'total': len(imoveis),
            'imoveis': [imovel.to_dict() for imovel in imoveis],
            'fonte': 'banco'  # Indicar que veio do banco
        })
        
    except Exception as e:
        # Capturar e logar o erro completo
        erro_detalhado = traceback.format_exc()
        print(f"ERRO AO LISTAR IMÓVEIS: {erro_detalhado}")
        
        return jsonify({
            'status': 'erro',
            'mensagem': f"Erro ao carregar imóveis: {str(e)}",
            'erro_detalhado': erro_detalhado
        }), 500

@monitor_bp.route('/estatisticas', methods=['GET'])
def estatisticas():
    """Retorna estatísticas do sistema"""
    try:
        # Total de imóveis ativos
        total_imoveis = Imovel.query.filter(Imovel.ativo == True).count()
        
        # Imóveis por tipo de negócio
        locacao = Imovel.query.filter(and_(Imovel.ativo == True, Imovel.tipo_negocio == 'LOCAÇÃO')).count()
        venda = Imovel.query.filter(and_(Imovel.ativo == True, Imovel.tipo_negocio == 'VENDA')).count()
        
        # Imóveis por imobiliária
        imobiliarias = db.session.query(
            Imovel.imobiliaria,
            db.func.count(Imovel.id).label('total')
        ).filter(Imovel.ativo == True).group_by(Imovel.imobiliaria).all()
        
        # Imóveis novos (últimas 24 horas)
        ontem = datetime.utcnow() - timedelta(days=1)
        novos_hoje = Imovel.query.filter(and_(
            Imovel.ativo == True,
            Imovel.data_coleta >= ontem
        )).count()
        
        # Última execução
        ultima_execucao = ExecucaoScraper.query.order_by(ExecucaoScraper.data_execucao.desc()).first()
        
        return jsonify({
            'total_imoveis': total_imoveis,
            'locacao': locacao,
            'venda': venda,
            'novos_hoje': novos_hoje,
            'por_imobiliaria': [{'nome': nome, 'total': total} for nome, total in imobiliarias],
            'ultima_execucao': ultima_execucao.to_dict() if ultima_execucao else None
        })
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'mensagem': f"Erro ao carregar estatísticas: {str(e)}"
        }), 500

@monitor_bp.route('/historico-execucoes', methods=['GET'])
def historico_execucoes():
    """Retorna histórico das execuções dos scrapers"""
    try:
        execucoes = ExecucaoScraper.query.order_by(ExecucaoScraper.data_execucao.desc()).limit(20).all()
        
        return jsonify({
            'execucoes': [execucao.to_dict() for execucao in execucoes]
        })
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'mensagem': f"Erro ao carregar histórico: {str(e)}"
        }), 500

def executar_scrapers_background(app):
    """Executa os scrapers em background e salva no banco"""
    global scraper_em_execucao, ultimo_resultado
    
    # Usar contexto da aplicação para acessar o banco de dados
    with app.app_context():
        scraper_em_execucao = True
        inicio = time.time()
        
        try:
            # Registrar início da execução
            execucao = ExecucaoScraper(
                scraper_nome='Todos os Scrapers',
                status='EM_ANDAMENTO'
            )
            db.session.add(execucao)
            db.session.commit()
            
            # Executar scrapers
            imoveis_coletados = executar_todos_scrapers()
            
            # Salvar imóveis no banco
            novos_imoveis = 0
            for imovel_data in imoveis_coletados:
                try:
                    # Verificar se já existe
                    existe = Imovel.query.filter(and_(
                        Imovel.imobiliaria == imovel_data.get('imobiliaria'),
                        Imovel.codigo == imovel_data.get('codigo'),
                        Imovel.tipo_negocio == imovel_data.get('tipo_negocio')
                    )).first()
                    
                    if not existe:
                        novo_imovel = Imovel.from_scraper_data(imovel_data)
                        db.session.add(novo_imovel)
                        novos_imoveis += 1
                except Exception as e:
                    print(f"Erro ao processar imóvel: {str(e)}")
                    continue
            
            db.session.commit()
            
            # Atualizar execução com sucesso
            tempo_execucao = time.time() - inicio
            execucao.status = 'SUCESSO'
            execucao.imoveis_coletados = novos_imoveis
            execucao.tempo_execucao = tempo_execucao
            db.session.commit()
            
            ultimo_resultado = {
                'status': 'sucesso',
                'total_coletados': len(imoveis_coletados),
                'novos_imoveis': novos_imoveis,
                'tempo_execucao': tempo_execucao,
                'data_execucao': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Registrar erro
            erro_detalhado = traceback.format_exc()
            print(f"ERRO NA EXECUÇÃO DOS SCRAPERS: {erro_detalhado}")
            
            tempo_execucao = time.time() - inicio
            execucao.status = 'ERRO'
            execucao.erro_mensagem = str(e)
            execucao.tempo_execucao = tempo_execucao
            db.session.commit()
            
            ultimo_resultado = {
                'status': 'erro',
                'erro': str(e),
                'tempo_execucao': tempo_execucao,
                'data_execucao': datetime.utcnow().isoformat()
            }
        
        finally:
            scraper_em_execucao = False

