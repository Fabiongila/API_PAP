from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, DadosIoT
from sqlalchemy.exc import SQLAlchemyError
import os
import sys

try:
    from ML.predictor import fazer_prevensoes
except ModuleNotFoundError:
    projeto_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if projeto_root not in sys.path:
        sys.path.insert(0, projeto_root)
    from ML.predictor import fazer_prevensoes

api_routes = Blueprint('api', __name__)


# ===== PARÂMETROS IDEAIS PARA CULTIVO DE MILHO =====
PARAMETROS_MILHO = {
    "umidade_solo": {"min": 20, "max": 60, "unidade": "%"},
    "umidade_ar": {"min": 50, "max": 60, "unidade": "%"},
    "temperatura_ar": {"min": 24, "max": 30, "unidade": "°C"},
}

# ===== PARÂMETROS IDEAIS PARA CULTIVO DE CAFÉ =====
PARAMETROS_CAFE = {
    "umidade_solo": {"min": 20, "max": 50, "unidade": "%"},
    "umidade_ar": {"min": 70, "max": 85, "unidade": "%"},
    "temperatura_ar": {"min": 20, "max": 28, "unidade": "°C"},  # Robusta em Angola
}

# ===== PARÂMETROS IDEAIS PARA CULTIVO DE SOJA =====
PARAMETROS_SOJA = {
    "umidade_solo": {"min": 20, "max": 60, "unidade": "%"},
    "umidade_ar": {"min": 50, "max": 70, "unidade": "%"},
    "temperatura_ar": {"min": 20, "max": 30, "unidade": "°C"},
}


def analisar_condicoes_milho(temperatura_ar=None, humidade_ar=None, humidade_solo=None):
    """
    Analisa as condições do ambiente para cultivo de milho
    Retorna um dicionário com análises para cada parâmetro
    """
    analise = {
        "temperatura_ar": {"ideal": False, "valor": temperatura_ar, "detalhes": ""},
        "humidade_ar": {"ideal": False, "valor": humidade_ar, "detalhes": ""},
        "humidade_solo": {"ideal": False, "valor": humidade_solo, "detalhes": ""},
        "status_geral": "sem dados"
    }
    
    total_verificado = 0
    total_ideal = 0
    
    # Analisar temperatura do ar (24°C - 30°C)
    if temperatura_ar is not None:
        total_verificado += 1
        if PARAMETROS_MILHO["temperatura_ar"]["min"] <= temperatura_ar <= PARAMETROS_MILHO["temperatura_ar"]["max"]:
            analise["temperatura_ar"]["ideal"] = True
            analise["temperatura_ar"]["detalhes"] = f"✓ Ideal ({temperatura_ar}°C está entre 24°C-30°C)"
            total_ideal += 1
        elif temperatura_ar < PARAMETROS_MILHO["temperatura_ar"]["min"]:
            analise["temperatura_ar"]["detalhes"] = f"✗ Muito baixa ({temperatura_ar}°C < 24°C)"
        else:
            analise["temperatura_ar"]["detalhes"] = f"✗ Muito alta ({temperatura_ar}°C > 30°C)"
    else:
        analise["temperatura_ar"]["detalhes"] = "Sem dados"
    
    # Analisar umidade do ar (50% - 60%)
    if humidade_ar is not None:
        total_verificado += 1
        if PARAMETROS_MILHO["umidade_ar"]["min"] <= humidade_ar <= PARAMETROS_MILHO["umidade_ar"]["max"]:
            analise["humidade_ar"]["ideal"] = True
            analise["humidade_ar"]["detalhes"] = f"✓ Ideal ({humidade_ar}% está entre 50%-60%)"
            total_ideal += 1
        elif humidade_ar < PARAMETROS_MILHO["umidade_ar"]["min"]:
            analise["humidade_ar"]["detalhes"] = f"✗ Muito baixa ({humidade_ar}% < 50%)"
        else:
            analise["humidade_ar"]["detalhes"] = f"✗ Muito alta ({humidade_ar}% > 60%)"
    else:
        analise["humidade_ar"]["detalhes"] = "Sem dados"
    
    # Analisar umidade do solo (20% - 60%)
    if humidade_solo is not None:
        total_verificado += 1
        if PARAMETROS_MILHO["umidade_solo"]["min"] <= humidade_solo <= PARAMETROS_MILHO["umidade_solo"]["max"]:
            analise["humidade_solo"]["ideal"] = True
            analise["humidade_solo"]["detalhes"] = f"✓ Ideal ({humidade_solo}% está entre 20%-60%)"
            total_ideal += 1
        elif humidade_solo < PARAMETROS_MILHO["umidade_solo"]["min"]:
            analise["humidade_solo"]["detalhes"] = f"✗ Muito baixa ({humidade_solo}% < 20%)"
        else:
            analise["humidade_solo"]["detalhes"] = f"✗ Muito alta ({humidade_solo}% > 60%)"
    else:
        analise["humidade_solo"]["detalhes"] = "Sem dados"
    
    # Determinar status geral
    if total_verificado == 0:
        analise["status_geral"] = "sem dados"
    elif total_ideal == total_verificado:
        analise["status_geral"] = "✓ Condições ideais"
    elif total_ideal >= total_verificado * 0.66:
        analise["status_geral"] = "⚠ Maioria de condições ideais"
    elif total_ideal > 0:
        analise["status_geral"] = "⚠ Algumas condições ideais"
    else:
        analise["status_geral"] = "✗ Nenhuma condição ideal"
    
    return analise


def analisar_condicoes_cafe(temperatura_ar=None, humidade_ar=None, humidade_solo=None):
    """
    Analisa as condições do ambiente para cultivo de café (Robusta em Angola)
    Retorna um dicionário com análises para cada parâmetro
    """
    analise = {
        "temperatura_ar": {"ideal": False, "valor": temperatura_ar, "detalhes": ""},
        "humidade_ar": {"ideal": False, "valor": humidade_ar, "detalhes": ""},
        "humidade_solo": {"ideal": False, "valor": humidade_solo, "detalhes": ""},
        "status_geral": "sem dados"
    }
    
    total_verificado = 0
    total_ideal = 0
    
    # Analisar temperatura do ar (20°C - 28°C para Robusta)
    if temperatura_ar is not None:
        total_verificado += 1
        if PARAMETROS_CAFE["temperatura_ar"]["min"] <= temperatura_ar <= PARAMETROS_CAFE["temperatura_ar"]["max"]:
            analise["temperatura_ar"]["ideal"] = True
            analise["temperatura_ar"]["detalhes"] = f"✓ Ideal ({temperatura_ar}°C está entre 20°C-28°C)"
            total_ideal += 1
        elif temperatura_ar < PARAMETROS_CAFE["temperatura_ar"]["min"]:
            analise["temperatura_ar"]["detalhes"] = f"✗ Muito baixa ({temperatura_ar}°C < 20°C)"
        else:
            analise["temperatura_ar"]["detalhes"] = f"✗ Muito alta ({temperatura_ar}°C > 28°C)"
    else:
        analise["temperatura_ar"]["detalhes"] = "Sem dados"
    
    # Analisar umidade do ar (70% - 85%)
    if humidade_ar is not None:
        total_verificado += 1
        if PARAMETROS_CAFE["umidade_ar"]["min"] <= humidade_ar <= PARAMETROS_CAFE["umidade_ar"]["max"]:
            analise["humidade_ar"]["ideal"] = True
            analise["humidade_ar"]["detalhes"] = f"✓ Ideal ({humidade_ar}% está entre 70%-85%)"
            total_ideal += 1
        elif humidade_ar < PARAMETROS_CAFE["umidade_ar"]["min"]:
            analise["humidade_ar"]["detalhes"] = f"✗ Muito baixa ({humidade_ar}% < 70%)"
        else:
            analise["humidade_ar"]["detalhes"] = f"✗ Muito alta ({humidade_ar}% > 85%)"
    else:
        analise["humidade_ar"]["detalhes"] = "Sem dados"
    
    # Analisar umidade do solo (20% - 50%)
    if humidade_solo is not None:
        total_verificado += 1
        if PARAMETROS_CAFE["umidade_solo"]["min"] <= humidade_solo <= PARAMETROS_CAFE["umidade_solo"]["max"]:
            analise["humidade_solo"]["ideal"] = True
            analise["humidade_solo"]["detalhes"] = f"✓ Ideal ({humidade_solo}% está entre 20%-50%)"
            total_ideal += 1
        elif humidade_solo < PARAMETROS_CAFE["umidade_solo"]["min"]:
            analise["humidade_solo"]["detalhes"] = f"✗ Muito baixa ({humidade_solo}% < 20%)"
        else:
            analise["humidade_solo"]["detalhes"] = f"✗ Muito alta ({humidade_solo}% > 50%)"
    else:
        analise["humidade_solo"]["detalhes"] = "Sem dados"
    
    # Determinar status geral
    if total_verificado == 0:
        analise["status_geral"] = "sem dados"
    elif total_ideal == total_verificado:
        analise["status_geral"] = "✓ Condições ideais"
    elif total_ideal >= total_verificado * 0.66:
        analise["status_geral"] = "⚠ Maioria de condições ideais"
    elif total_ideal > 0:
        analise["status_geral"] = "⚠ Algumas condições ideais"
    else:
        analise["status_geral"] = "✗ Nenhuma condição ideal"
    
    return analise


def analisar_condicoes_soja(temperatura_ar=None, humidade_ar=None, humidade_solo=None):
    """
    Analisa as condições do ambiente para cultivo de soja em Angola
    Retorna um dicionário com análises para cada parâmetro
    """
    analise = {
        "temperatura_ar": {"ideal": False, "valor": temperatura_ar, "detalhes": ""},
        "humidade_ar": {"ideal": False, "valor": humidade_ar, "detalhes": ""},
        "humidade_solo": {"ideal": False, "valor": humidade_solo, "detalhes": ""},
        "status_geral": "sem dados"
    }
    
    total_verificado = 0
    total_ideal = 0
    
    # Analisar temperatura do ar (20°C - 30°C)
    if temperatura_ar is not None:
        total_verificado += 1
        if PARAMETROS_SOJA["temperatura_ar"]["min"] <= temperatura_ar <= PARAMETROS_SOJA["temperatura_ar"]["max"]:
            analise["temperatura_ar"]["ideal"] = True
            analise["temperatura_ar"]["detalhes"] = f"✓ Ideal ({temperatura_ar}°C está entre 20°C-30°C)"
            total_ideal += 1
        elif temperatura_ar < PARAMETROS_SOJA["temperatura_ar"]["min"]:
            analise["temperatura_ar"]["detalhes"] = f"✗ Muito baixa ({temperatura_ar}°C < 20°C)"
        else:
            analise["temperatura_ar"]["detalhes"] = f"✗ Muito alta ({temperatura_ar}°C > 30°C)"
    else:
        analise["temperatura_ar"]["detalhes"] = "Sem dados"
    
    # Analisar umidade do ar (50% - 70%)
    if humidade_ar is not None:
        total_verificado += 1
        if PARAMETROS_SOJA["umidade_ar"]["min"] <= humidade_ar <= PARAMETROS_SOJA["umidade_ar"]["max"]:
            analise["humidade_ar"]["ideal"] = True
            analise["humidade_ar"]["detalhes"] = f"✓ Ideal ({humidade_ar}% está entre 50%-70%)"
            total_ideal += 1
        elif humidade_ar < PARAMETROS_SOJA["umidade_ar"]["min"]:
            analise["humidade_ar"]["detalhes"] = f"✗ Muito baixa ({humidade_ar}% < 50%)"
        else:
            analise["humidade_ar"]["detalhes"] = f"✗ Muito alta ({humidade_ar}% > 70%)"
    else:
        analise["humidade_ar"]["detalhes"] = "Sem dados"
    
    # Analisar umidade do solo (20% - 60%)
    if humidade_solo is not None:
        total_verificado += 1
        if PARAMETROS_SOJA["umidade_solo"]["min"] <= humidade_solo <= PARAMETROS_SOJA["umidade_solo"]["max"]:
            analise["humidade_solo"]["ideal"] = True
            analise["humidade_solo"]["detalhes"] = f"✓ Ideal ({humidade_solo}% está entre 20%-60%)"
            total_ideal += 1
        elif humidade_solo < PARAMETROS_SOJA["umidade_solo"]["min"]:
            analise["humidade_solo"]["detalhes"] = f"✗ Muito baixa ({humidade_solo}% < 20%)"
        else:
            analise["humidade_solo"]["detalhes"] = f"✗ Muito alta ({humidade_solo}% > 60%)"
    else:
        analise["humidade_solo"]["detalhes"] = "Sem dados"
    
    # Determinar status geral
    if total_verificado == 0:
        analise["status_geral"] = "sem dados"
    elif total_ideal == total_verificado:
        analise["status_geral"] = "✓ Condições ideais"
    elif total_ideal >= total_verificado * 0.66:
        analise["status_geral"] = "⚠ Maioria de condições ideais"
    elif total_ideal > 0:
        analise["status_geral"] = "⚠ Algumas condições ideais"
    else:
        analise["status_geral"] = "✗ Nenhuma condição ideal"
    
    return analise


# POST /api/dados
@api_routes.route('/api/dados', methods=['POST'])
def receber_dados():
    dados = request.get_json(silent=True)
    if not dados or not isinstance(dados, dict):
        return jsonify({"erro": "JSON inválido ou ausente"}), 400

    erros = []

    device_id = dados.get('device_id')
    if not isinstance(device_id, str) or not device_id.strip():
        erros.append("device_id obrigatório (string)")

    timestamp = dados.get('timestamp')
    if timestamp is None:
        timestamp = datetime.utcnow()
    elif not isinstance(timestamp, str):
        erros.append("timestamp deve ser string ISO8601")
    else:
        # Converter string ISO para datetime
        try:
            # Tentar formato ISO com fromisoformat (Python 3.7+)
            if 'T' in timestamp:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            erros.append("timestamp deve ser string ISO8601 válida")

    gps = dados.get('gps')
    latitude = longitude = None
    if not isinstance(gps, dict):
        erros.append("gps obrigatório (objeto com latitude e longitude)")
    else:
        try:
            latitude  = float(gps.get('latitude'))
            longitude = float(gps.get('longitude'))
        except (TypeError, ValueError):
            erros.append("gps.latitude e gps.longitude devem ser numéricos")

    localizacao = dados.get('localizacao')
    if isinstance(localizacao, dict):
        localizacao = localizacao.get('localizacao')
    elif localizacao is not None and not isinstance(localizacao, str):
        erros.append("localizacao deve ser string ou objeto")

    bme = dados.get('bme280') or {}
    temperatura_ar = humidade_ar = pressao_ar = None
    if isinstance(bme, dict):
        try:
            if 'temperatura' in bme: temperatura_ar = float(bme['temperatura'])
        except (TypeError, ValueError): erros.append("bme280.temperatura deve ser numérico")
        try:
            if 'humidade' in bme: humidade_ar = float(bme['humidade'])
        except (TypeError, ValueError): erros.append("bme280.humidade deve ser numérico")
        try:
            if 'pressao' in bme: pressao_ar = float(bme['pressao'])
        except (TypeError, ValueError): erros.append("bme280.pressao deve ser numérico")
    elif bme is not None:
        erros.append("bme280 deve ser objeto")

    solo = dados.get('solo') or {}
    humidade_solo = None
    if isinstance(solo, dict):
        try:
            if 'humidade' in solo: humidade_solo = float(solo['humidade'])
        except (TypeError, ValueError): erros.append("solo.humidade deve ser numérico")
    elif solo is not None:
        erros.append("solo deve ser objeto")

    vib = dados.get('vibracao') or {}
    vibracao = None
    if isinstance(vib, dict):
        if 'detectada' in vib:    vibracao = bool(vib['detectada'])
        elif 'detejctada' in vib: vibracao = bool(vib['detejctada'])
    elif vib is not None:
        erros.append("vibracao deve ser objeto")

    visao = dados.get('visao') or {}
    detecao_praga = tipo_praga = confianca = None
    if isinstance(visao, dict):
        if 'detecao_praga' in visao:
            detecao_praga = bool(visao['detecao_praga'])
        if 'tipo_praga' in visao:
            if visao['tipo_praga'] is not None and not isinstance(visao['tipo_praga'], str):
                erros.append("visao.tipo_praga deve ser string ou null")
            else:
                tipo_praga = visao['tipo_praga']
        if 'confianca' in visao:
            try:
                if visao['confianca'] is not None:
                    confianca = float(visao['confianca'])
            except (TypeError, ValueError):
                erros.append("visao.confianca deve ser numérico ou null")
    elif visao is not None:
        erros.append("visao deve ser objeto")

    if erros:
        return jsonify({"erro": "Validação falhou", "detalhes": erros}), 400

    record = DadosIoT(
        device_id=device_id, timestamp=timestamp,
        latitude=latitude, longitude=longitude, localizacao=localizacao,
        temperatura_ar=temperatura_ar, humidade_ar=humidade_ar, pressao_ar=pressao_ar,
        humidade_solo=humidade_solo, vibracao=vibracao,
        detecao_praga=detecao_praga, tipo_praga=tipo_praga, confianca=confianca
    )

    try:
        db.session.add(record)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"erro": "Falha ao salvar", "detalhe": str(e)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"erro": "Erro interno ao salvar"}), 500

    # ===== FAZER PREVISÕES ML =====
    previsoes_resultado = {}
    try:
        # Preparar dados atuais para previsão
        dados_atuais = {
            'temperatura_ar': temperatura_ar,
            'humidade_ar': humidade_ar,
            'pressao_ar': pressao_ar,
            'humidade_solo': humidade_solo
        }

        # Tentar fazer previsões com dados históricos recentes
        dados_historico = DadosIoT.query.order_by(DadosIoT.id.desc()).limit(10).all()
        if len(dados_historico) >= 3:
            # Usar dados históricos para análise agregada
            dados_lista = []
            for d in dados_historico:
                dados_lista.append({
                    'temperatura_ar': d.temperatura_ar,
                    'humidade_ar': d.humidade_ar,
                    'pressao_ar': d.pressao_ar,
                    'humidade_solo': d.humidade_solo
                })
            previsoes_resultado = fazer_prevensoes(dados_lista=dados_lista)
        else:
            # Usar apenas dados atuais
            previsoes_resultado = fazer_prevensoes(dados_sensor=dados_atuais)

    except Exception as e:
        print(f"Erro ao fazer previsões: {e}")
        previsoes_resultado = {"aviso": "Previsões não disponíveis"}

    # ===== ANÁLISES DE CONDIÇÕES IDEAIS =====
    analise_milho = analisar_condicoes_milho(
        temperatura_ar=temperatura_ar,
        humidade_ar=humidade_ar,
        humidade_solo=humidade_solo
    )
    
    analise_cafe = analisar_condicoes_cafe(
        temperatura_ar=temperatura_ar,
        humidade_ar=humidade_ar,
        humidade_solo=humidade_solo
    )
    
    analise_soja = analisar_condicoes_soja(
        temperatura_ar=temperatura_ar,
        humidade_ar=humidade_ar,
        humidade_solo=humidade_solo
    )

    return jsonify({
        "status": "sucesso",
        "mensagem": "Dados recebidos e armazenados",
        "analise_condicoes": {
            "milho": analise_milho,
            "cafe": analise_cafe,
            "soja": analise_soja
        },
        "previsoes": previsoes_resultado
    }), 201


# GET /api/dados_sensores
@api_routes.route('/api/dados_sensores', methods=['GET'])
def listar_dados():
    registros = DadosIoT.query.order_by(DadosIoT.id.desc()).all()
    resultado = []
    for r in registros:
        analise = analisar_condicoes_milho(
            temperatura_ar=r.temperatura_ar,
            humidade_ar=r.humidade_ar,
            humidade_solo=r.humidade_solo
        )
        resultado.append({
            "id": r.id, "device_id": r.device_id, "timestamp": r.timestamp,
            "gps":         {"latitude": r.latitude, "longitude": r.longitude},
            "localizacao": r.localizacao,
            "bme280":      {"temperatura": r.temperatura_ar, "humidade": r.humidade_ar, "pressao": r.pressao_ar},
            "solo":        {"humidade": r.humidade_solo},
            "vibracao":    {"detectada": r.vibracao},
            "visao":       {"detecao_praga": r.detecao_praga, "tipo_praga": r.tipo_praga, "confianca": r.confianca},
            "analise_condicoes": analise
        })
    return jsonify(resultado), 200


# GET /api/gps
@api_routes.route('/api/gps', methods=['GET'])
def listar_gps():
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r: return jsonify({"erro": "Nenhum registro encontrado"}), 404
    return jsonify({"id": r.id, "device_id": r.device_id, "timestamp": r.timestamp,
                    "gps": {"latitude": r.latitude, "longitude": r.longitude}}), 200


# GET /api/bme280
@api_routes.route('/api/bme280', methods=['GET'])
def listar_bme280():
    cultura = request.args.get('cultura', 'ambos')
    if cultura not in ['milho', 'cafe', 'soja', 'ambos']:
        return jsonify({"erro": "cultura deve ser 'milho', 'cafe', 'soja' ou 'ambos'"}), 400
    
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r: return jsonify({"erro": "Nenhum registro encontrado"}), 404
    
    analises = {}
    if cultura in ['milho', 'ambos']:
        analises['milho'] = analisar_condicoes_milho(
            temperatura_ar=r.temperatura_ar,
            humidade_ar=r.humidade_ar
        )
    if cultura in ['cafe', 'ambos']:
        analises['cafe'] = analisar_condicoes_cafe(
            temperatura_ar=r.temperatura_ar,
            humidade_ar=r.humidade_ar
        )
    if cultura in ['soja', 'ambos']:
        analises['soja'] = analisar_condicoes_soja(
            temperatura_ar=r.temperatura_ar,
            humidade_ar=r.humidade_ar
        )
    
    return jsonify({
        "id": r.id, "device_id": r.device_id, "timestamp": r.timestamp,
        "bme280": {"temperatura": r.temperatura_ar, "humidade": r.humidade_ar, "pressao": r.pressao_ar},
        "analises_condicoes": analises,
        "cultura": cultura
    }), 200


# GET /api/solo
@api_routes.route('/api/solo', methods=['GET'])
def listar_solo():
    cultura = request.args.get('cultura', 'ambos')
    if cultura not in ['milho', 'cafe', 'soja', 'ambos']:
        return jsonify({"erro": "cultura deve ser 'milho', 'cafe', 'soja' ou 'ambos'"}), 400
    
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r: return jsonify({"erro": "Nenhum registro encontrado"}), 404
    
    analises = {}
    if cultura in ['milho', 'ambos']:
        analises['milho'] = analisar_condicoes_milho(humidade_solo=r.humidade_solo)
    if cultura in ['cafe', 'ambos']:
        analises['cafe'] = analisar_condicoes_cafe(humidade_solo=r.humidade_solo)
    if cultura in ['soja', 'ambos']:
        analises['soja'] = analisar_condicoes_soja(humidade_solo=r.humidade_solo)
    
    return jsonify({
        "id": r.id, "device_id": r.device_id, "timestamp": r.timestamp,
        "solo": {"humidade": r.humidade_solo},
        "analises_condicoes": analises,
        "cultura": cultura
    }), 200


# GET /api/vibracao
@api_routes.route('/api/vibracao', methods=['GET'])
def listar_vibracao():
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r: return jsonify({"erro": "Nenhum registro encontrado"}), 404
    return jsonify({"id": r.id, "device_id": r.device_id, "timestamp": r.timestamp,
                    "vibracao": {"detectada": r.vibracao}}), 200


# GET /api/visao
@api_routes.route('/api/visao', methods=['GET'])
def listar_visao():
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r: return jsonify({"erro": "Nenhum registro encontrado"}), 404
    return jsonify({"id": r.id, "device_id": r.device_id, "timestamp": r.timestamp,
                    "visao": {"detecao_praga": r.detecao_praga, "tipo_praga": r.tipo_praga, "confianca": r.confianca}}), 200


# GET /api/alertas
@api_routes.route('/api/alertas', methods=['GET'])
def listar_alertas():
    registros = DadosIoT.query.order_by(DadosIoT.id.desc()).limit(100).all()
    resultado = []
    for r in registros:
        if r.detecao_praga:
            resultado.append({"id": f"ALT-{r.id}-praga", "tipo": "Praga",
                "mensagem": f"Detecção de praga: {r.tipo_praga or 'desconhecida'}",
                "severidade": "crítico" if r.confianca and r.confianca > 0.8 else "aviso",
                "timestamp": r.timestamp, "status": "ativo"})
        if r.humidade_solo is not None and r.humidade_solo < 30:
            resultado.append({"id": f"ALT-{r.id}-solo", "tipo": "Solo",
                "mensagem": f"Humidade do solo baixa: {r.humidade_solo:.1f}%",
                "severidade": "crítico", "timestamp": r.timestamp, "status": "ativo"})
        if r.temperatura_ar is not None and (r.temperatura_ar < 15 or r.temperatura_ar > 35):
            resultado.append({"id": f"ALT-{r.id}-temp", "tipo": "Clima",
                "mensagem": f"Temperatura fora dos limites: {r.temperatura_ar:.1f}°C",
                "severidade": "aviso", "timestamp": r.timestamp, "status": "ativo"})
        if r.vibracao:
            resultado.append({"id": f"ALT-{r.id}-vib", "tipo": "Sensor",
                "mensagem": "Vibração detectada no equipamento",
                "severidade": "aviso", "timestamp": r.timestamp, "status": "ativo"})
    return jsonify(resultado), 200


# GET /api/analises_ml
@api_routes.route('/api/analises_ml', methods=['GET'])
def analises_ml():
    """
    Endpoint dedicado para análises ML
    Parâmetros opcionais:
    - device_id: filtro por dispositivo específico
    - limit: número de registros históricos (padrão: 10)
    - dados_json: JSON string com dados atuais para análise (opcional)
    """

    device_id = request.args.get('device_id')
    limit = int(request.args.get('limit', 10))
    dados_json = request.args.get('dados_json')

    # Se dados_json fornecido, usar dados atuais
    if dados_json:
        try:
            import json
            dados_atuais = json.loads(dados_json)
            if not isinstance(dados_atuais, dict):
                return jsonify({"erro": "dados_json deve ser objeto JSON válido"}), 400

            # Preparar dados para ML
            dados_sensor = {
                'temperatura_ar': dados_atuais.get('temperatura_ar'),
                'humidade_ar': dados_atuais.get('humidade_ar'),
                'pressao_ar': dados_atuais.get('pressao_ar'),
                'humidade_solo': dados_atuais.get('humidade_solo')
            }

            # Fazer previsões
            previsoes_resultado = fazer_prevensoes(dados_sensor=dados_sensor)

            return jsonify({
                "status": "sucesso",
                "tipo": "analise_dados_atuais",
                "dados_analisados": dados_sensor,
                "previsoes": previsoes_resultado
            }), 200

        except json.JSONDecodeError:
            return jsonify({"erro": "dados_json deve ser JSON válido"}), 400
        except Exception as e:
            return jsonify({"erro": f"Erro na análise: {str(e)}"}), 500

    # Senão, usar dados históricos
    query = DadosIoT.query
    if device_id:
        query = query.filter_by(device_id=device_id)

    registros = query.order_by(DadosIoT.id.desc()).limit(limit).all()

    if not registros:
        return jsonify({"erro": "Nenhum dado encontrado para análise"}), 404

    # Preparar lista de dados para agregação
    dados_lista = []
    for r in registros:
        dados_lista.append({
            'temperatura_ar': r.temperatura_ar,
            'humidade_ar': r.humidade_ar,
            'pressao_ar': r.pressao_ar,
            'humidade_solo': r.humidade_solo
        })

    # Fazer previsões agregadas
    try:
        previsoes_resultado = fazer_prevensoes(dados_lista=dados_lista)
    except Exception as e:
        return jsonify({"erro": f"Erro nas previsões ML: {str(e)}"}), 500

    # Retornar resultado
    return jsonify({
        "status": "sucesso",
        "tipo": "analise_historica_agregada",
        "device_id": device_id,
        "registros_analisados": len(registros),
        "periodo": {
            "mais_antigo": registros[-1].timestamp.isoformat() if registros else None,
            "mais_recente": registros[0].timestamp.isoformat() if registros else None
        },
        "previsoes": previsoes_resultado
    }), 200


# GET /api/analises_condicoes
@api_routes.route('/api/analises_condicoes', methods=['GET'])
def analises_condicoes():
    """
    Endpoint para análises de CONDIÇÕES IDEAIS (milho, café e soja)
    Valida múltiplas culturas sem usar ML
    
    Parâmetros opcionais:
    - cultura: 'milho' | 'cafe' | 'soja' | 'ambos' (padrão: ambos)
    - device_id: filtro por dispositivo específico
    - limit: número de registros históricos (padrão: 20)
    - dados_json: JSON string com dados atuais para análise (opcional)
    
    Retorna análise para cada parâmetro com:
    - ideal: booleano indicando se está ideal
    - valor: valor atual
    - detalhes: mensagem descritiva
    - status_geral: resumo das condições
    """
    
    cultura = request.args.get('cultura', 'ambos').lower()
    device_id = request.args.get('device_id')
    limit = int(request.args.get('limit', 20))
    dados_json = request.args.get('dados_json')
    
    if cultura not in ['milho', 'cafe', 'soja', 'ambos']:
        return jsonify({"erro": "cultura deve ser 'milho', 'cafe', 'soja' ou 'ambos'"}), 400
    
    # Se dados_json fornecido, usar dados atuais
    if dados_json:
        try:
            import json
            dados_atuais = json.loads(dados_json)
            if not isinstance(dados_atuais, dict):
                return jsonify({"erro": "dados_json deve ser objeto JSON válido"}), 400
            
            temp = dados_atuais.get('temperatura_ar')
            humid_ar = dados_atuais.get('humidade_ar')
            humid_solo = dados_atuais.get('humidade_solo')
            
            resultado = {
                "status": "sucesso",
                "tipo": "analise_condicoes_atuais",
                "parametros_ideais": {},
                "dados_analisados": {"temperatura_ar": temp, "humidade_ar": humid_ar, "humidade_solo": humid_solo},
                "analises": {}
            }
            
            if cultura in ['milho', 'ambos']:
                analise_m = analisar_condicoes_milho(temperatura_ar=temp, humidade_ar=humid_ar, humidade_solo=humid_solo)
                resultado["parametros_ideais"]["milho"] = PARAMETROS_MILHO
                resultado["analises"]["milho"] = analise_m
            
            if cultura in ['cafe', 'ambos']:
                analise_c = analisar_condicoes_cafe(temperatura_ar=temp, humidade_ar=humid_ar, humidade_solo=humid_solo)
                resultado["parametros_ideais"]["cafe"] = PARAMETROS_CAFE
                resultado["analises"]["cafe"] = analise_c
            
            if cultura in ['soja', 'ambos']:
                analise_s = analisar_condicoes_soja(temperatura_ar=temp, humidade_ar=humid_ar, humidade_solo=humid_solo)
                resultado["parametros_ideais"]["soja"] = PARAMETROS_SOJA
                resultado["analises"]["soja"] = analise_s
            
            return jsonify(resultado), 200
        
        except json.JSONDecodeError:
            return jsonify({"erro": "dados_json deve ser JSON válido"}), 400
        except Exception as e:
            return jsonify({"erro": f"Erro na análise: {str(e)}"}), 500
    
    # Senão, usar dados históricos
    query = DadosIoT.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    
    registros = query.order_by(DadosIoT.id.desc()).limit(limit).all()
    
    if not registros:
        return jsonify({"erro": "Nenhum dado encontrado para análise"}), 404
    
    # Analisar cada registro
    registros_analise = []
    totais_ideais = {"milho": 0, "cafe": 0, "soja": 0}
    totais_verificadas = {"milho": 0, "cafe": 0, "soja": 0}
    
    for r in registros:
        analise_r = {"id": r.id, "device_id": r.device_id, "timestamp": r.timestamp.isoformat()}
        
        if cultura in ['milho', 'ambos']:
            analise_m = analisar_condicoes_milho(
                temperatura_ar=r.temperatura_ar,
                humidade_ar=r.humidade_ar,
                humidade_solo=r.humidade_solo
            )
            analise_r["milho"] = analise_m
            
            ideais_m = sum([
                analise_m["temperatura_ar"]["ideal"],
                analise_m["humidade_ar"]["ideal"],
                analise_m["humidade_solo"]["ideal"]
            ])
            totais_ideais["milho"] += ideais_m
            totais_verificadas["milho"] += 3
        
        if cultura in ['cafe', 'ambos']:
            analise_c = analisar_condicoes_cafe(
                temperatura_ar=r.temperatura_ar,
                humidade_ar=r.humidade_ar,
                humidade_solo=r.humidade_solo
            )
            analise_r["cafe"] = analise_c
            
            ideais_c = sum([
                analise_c["temperatura_ar"]["ideal"],
                analise_c["humidade_ar"]["ideal"],
                analise_c["humidade_solo"]["ideal"]
            ])
            totais_ideais["cafe"] += ideais_c
            totais_verificadas["cafe"] += 3
        
        if cultura in ['soja', 'ambos']:
            analise_s = analisar_condicoes_soja(
                temperatura_ar=r.temperatura_ar,
                humidade_ar=r.humidade_ar,
                humidade_solo=r.humidade_solo
            )
            analise_r["soja"] = analise_s
            
            ideais_s = sum([
                analise_s["temperatura_ar"]["ideal"],
                analise_s["humidade_ar"]["ideal"],
                analise_s["humidade_solo"]["ideal"]
            ])
            totais_ideais["soja"] += ideais_s
            totais_verificadas["soja"] += 3
        
        registros_analise.append(analise_r)
    
    # Calcular percentuais
    percentuais = {}
    for cult in ["milho", "cafe", "soja"]:
        if totais_verificadas[cult] > 0:
            percentuais[cult] = round(totais_ideais[cult] / totais_verificadas[cult] * 100, 2)
        else:
            percentuais[cult] = 0
    
    resumo = {}
    if cultura in ['milho', 'ambos']:
        resumo["milho"] = {
            "condicoes_ideais_total": totais_ideais["milho"],
            "condicoes_verificadas": totais_verificadas["milho"],
            "percentual_ideal": percentuais["milho"]
        }
    if cultura in ['cafe', 'ambos']:
        resumo["cafe"] = {
            "condicoes_ideais_total": totais_ideais["cafe"],
            "condicoes_verificadas": totais_verificadas["cafe"],
            "percentual_ideal": percentuais["cafe"]
        }
    if cultura in ['soja', 'ambos']:
        resumo["soja"] = {
            "condicoes_ideais_total": totais_ideais["soja"],
            "condicoes_verificadas": totais_verificadas["soja"],
            "percentual_ideal": percentuais["soja"]
        }
    
    parametros = {}
    if cultura in ['milho', 'ambos']:
        parametros["milho"] = PARAMETROS_MILHO
    if cultura in ['cafe', 'ambos']:
        parametros["cafe"] = PARAMETROS_CAFE
    if cultura in ['soja', 'ambos']:
        parametros["soja"] = PARAMETROS_SOJA
    
    return jsonify({
        "status": "sucesso",
        "tipo": "analise_condicoes_historica",
        "parametros_ideais": parametros,
        "cultura": cultura,
        "device_id": device_id,
        "registros_analisados": len(registros),
        "periodo": {
            "mais_antigo": registros[-1].timestamp.isoformat() if registros else None,
            "mais_recente": registros[0].timestamp.isoformat() if registros else None
        },
        "resumo": resumo,
        "registros": registros_analise
    }), 200
