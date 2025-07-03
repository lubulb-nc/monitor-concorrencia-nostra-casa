from datetime import datetime
from src.database import db

class Imovel(db.Model):
    __tablename__ = 'imoveis'
    
    id = db.Column(db.Integer, primary_key=True)
    imobiliaria = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    tipo_imovel = db.Column(db.String(50), nullable=True)
    preco = db.Column(db.String(50), nullable=True)
    area = db.Column(db.String(20), nullable=True)
    quartos = db.Column(db.String(10), nullable=True)
    banheiros = db.Column(db.String(10), nullable=True)
    vagas = db.Column(db.String(10), nullable=True)
    endereco = db.Column(db.String(200), nullable=True)
    tipo_negocio = db.Column(db.String(20), nullable=False)  # LOCAÇÃO ou VENDA
    url = db.Column(db.String(500), nullable=True)
    data_coleta = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Índice único para evitar duplicatas
    __table_args__ = (
        db.Index('idx_imovel_unique', 'imobiliaria', 'codigo', 'tipo_negocio'),
    )
    
    def to_dict(self):
        """Converte o objeto para dicionário para serialização JSON"""
        return {
            'id': self.id,
            'imobiliaria': self.imobiliaria,
            'codigo': self.codigo,
            'titulo': self.titulo,
            'tipo_imovel': self.tipo_imovel,
            'preco': self.preco,
            'area': self.area,
            'quartos': self.quartos,
            'banheiros': self.banheiros,
            'vagas': self.vagas,
            'endereco': self.endereco,
            'tipo_negocio': self.tipo_negocio,
            'url': self.url,
            'data_coleta': self.data_coleta.isoformat() if self.data_coleta else None,
            'ativo': self.ativo
        }
    
    @staticmethod
    def from_scraper_data(data):
        """Cria um objeto Imovel a partir dos dados do scraper"""
        return Imovel(
            imobiliaria=data.get('imobiliaria', ''),
            codigo=data.get('codigo', ''),
            titulo=data.get('titulo', ''),
            tipo_imovel=data.get('tipo_imovel', ''),
            preco=data.get('preco', ''),
            area=data.get('area', ''),
            quartos=data.get('quartos', ''),
            banheiros=data.get('banheiros', ''),
            vagas=data.get('vagas', ''),
            endereco=data.get('endereco', ''),
            tipo_negocio=data.get('tipo_negocio', ''),
            url=data.get('url', '')
        )


class ExecucaoScraper(db.Model):
    __tablename__ = 'execucoes_scraper'
    
    id = db.Column(db.Integer, primary_key=True)
    data_execucao = db.Column(db.DateTime, default=datetime.utcnow)
    scraper_nome = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # SUCESSO, ERRO, EM_ANDAMENTO
    imoveis_coletados = db.Column(db.Integer, default=0)
    tempo_execucao = db.Column(db.Float, nullable=True)  # em segundos
    erro_mensagem = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data_execucao': self.data_execucao.isoformat() if self.data_execucao else None,
            'scraper_nome': self.scraper_nome,
            'status': self.status,
            'imoveis_coletados': self.imoveis_coletados,
            'tempo_execucao': self.tempo_execucao,
            'erro_mensagem': self.erro_mensagem
        }

