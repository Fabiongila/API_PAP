from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, DadosIoT
from sqlalchemy.exc import SQLAlchemyError

api_routes = Blueprint('api', __name__)


# Rota para receber dados do dispositivo IoT
@api_routes.route('/api/dados', methods=['POST'])
def receber_dados():

    dados = request.get_json(silent=True)
    if not dados or not isinstance(dados, dict):
        return jsonify({"erro": "JSON inválido ou ausente"}), 400

    erros = []

    # device_id (obrigatório)
    device_id = dados.get('device_id')
    if not isinstance(device_id, str) or not device_id.strip():
        erros.append("device_id obrigatório (string)")

    # timestamp (opcional, padrão: ISO8601 atual)
    timestamp = dados.get('timestamp')
    if timestamp is None:
        timestamp = datetime.utcnow()
    elif not isinstance(timestamp, str):
        erros.append("timestamp deve ser string ISO8601")

    # gps (obrigatório)
    gps = dados.get('gps')
    latitude = longitude = None
    if not isinstance(gps, dict):
        erros.append("gps obrigatório (objeto com latitude e longitude)")
    else:
        latitude = gps.get('latitude')
        longitude = gps.get('longitude')
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            erros.append("gps.latitude e gps.longitude devem ser numéricos")
            
    
    
    localizacao = dados.get('localizacao')

    if not isinstance(localizacao, dict):
        erros.append("localizacao deve ser objeto")
    else:
        localizacao = localizacao.get("localizacao")
        if not localizacao:
            erros.append("localizacao obrigatória")

    
                    

    # bme280 (opcional)
    bme = dados.get('bme280') or {}
    temperatura_ar = humidade_ar = pressao_ar = None
    if isinstance(bme, dict):
        if 'temperatura' in bme:
            try:
                temperatura_ar = float(bme['temperatura'])
            except (TypeError, ValueError):
                erros.append("bme280.temperatura deve ser numérico")
        if 'humidade' in bme:
            try:
                humidade_ar = float(bme['humidade'])
            except (TypeError, ValueError):
                erros.append("bme280.humidade deve ser numérico")
        if 'pressao' in bme:
            try:
                pressao_ar = float(bme['pressao'])
            except (TypeError, ValueError):
                erros.append("bme280.pressao deve ser numérico")
    elif bme is not None:
        erros.append("bme280 deve ser objeto")

    # solo (opcional)
    solo = dados.get('solo') or {}
    humidade_solo = None
    if isinstance(solo, dict):
        if 'humidade' in solo:
            try:
                humidade_solo = float(solo['humidade'])
            except (TypeError, ValueError):
                erros.append("solo.humidade deve ser numérico")
    elif solo is not None:
        erros.append("solo deve ser objeto")

    # vibracao (opcional) - suporta 'detectada' (correto) e 'detejctada' (retrocompatibilidade)
    vib = dados.get('vibracao') or {}
    vibracao = None
    if isinstance(vib, dict):
        if 'detectada' in vib:
            vibracao = bool(vib['detectada'])
        elif 'detejctada' in vib:
            vibracao = bool(vib['detejctada'])
    elif vib is not None:
        erros.append("vibracao deve ser objeto")

    # visao (opcional)
    #visao = dados.get('visao') or {}
    #detecao_praga = tipo_praga = confianca = None
    #if isinstance(visao, dict):
     #   if 'detecao_praga' in visao:
      #      detecao_praga = bool(visao['detecao_praga'])
       # if 'tipo_praga' in visao:
        #    if visao['tipo_praga'] is not None and not isinstance(visao['tipo_praga'], str):
         #       erros.append("visao.tipo_praga deve ser string ou null")
          #  else:
           #     tipo_praga = visao['tipo_praga']
    #    if 'confianca' in visao:
     #       try:
      #          if visao['confianca'] is not None:
       #             confianca = float(visao['confianca'])
        #    except (TypeError, ValueError):
         #       erros.append("visao.confianca deve ser numérico ou null")
    #elif visao is not None:
     #   erros.append("visao deve ser objeto")

    # Se houver erros de validação, retornar 400 com detalhes
    if erros:
        return jsonify({"erro": "Validação falhou", "detalhes": erros}), 400

    record = DadosIoT(
        device_id=device_id,
        timestamp=timestamp,
        latitude=latitude,
        longitude=longitude,
        localizacao=localizacao,
        temperatura_ar=temperatura_ar,
        humidade_ar=humidade_ar,
        pressao_ar=pressao_ar,
        humidade_solo=humidade_solo,
        vibracao=vibracao
        #detecao_praga=detecao_praga,
        #tipo_praga=tipo_praga,
        #confianca=confianca
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

    return jsonify({
        "status": "sucesso",
        "mensagem": "Dados recebidos e armazenados"
    }), 201


# Rota para listar os dados mais recentes do dispositivo IoT@api_routes.route('/api/dados_sensores', methods=['GET'])
@api_routes.route('/api/dados_sensores', methods=['GET'])
def listar_dados():
    registros = DadosIoT.query.order_by(DadosIoT.id.desc()).all()

    resultado = []

    for r in registros:
        resultado.append({
            "id": r.id,
            "device_id": r.device_id,
            "timestamp": r.timestamp,

            "gps": {
                "latitude": r.latitude,
                "longitude": r.longitude
            },
            
            "localizacao":{
                "localizacao": r.localizacao
            },

            "bme280": {
                "temperatura": r.temperatura_ar,
                "humidade": r.humidade_ar,
                "pressao": r.pressao_ar
            },

            "solo": {
                "humidade": r.humidade_solo
            },

            "vibracao": {
                "detectada": r.vibracao
            },

            #"visao": {
             #   "detecao_praga": r.detecao_praga,
              #  "tipo_praga": r.tipo_praga,
               # "confianca": r.confianca
           # }
        })

    return jsonify(resultado), 200


# Rotas para listar dados específico (GPS)
@api_routes.route('/api/gps', methods=['GET'])
def listar_gps():
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r:
        return jsonify({"erro": "Nenhum registro encontrado"}), 404

    resultado = {
        "id": r.id,
        "device_id": r.device_id,
        "timestamp": r.timestamp,
        "gps": {
            "latitude": r.latitude,
            "longitude": r.longitude
        }
    }

    return jsonify(resultado), 200



# Rotas para listar dados específico (BME280)
@api_routes.route('/api/bme280', methods=['GET'])
def listar_bme280():
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r:
        return jsonify({"erro": "Nenhum registro encontrado"}), 404

    resultado = {
        "id": r.id,
        "device_id": r.device_id,
        "timestamp": r.timestamp,
        "bme280": {
            "temperatura": r.temperatura_ar,
            "humidade": r.humidade_ar,
            "pressao": r.pressao_ar
        }
    }

    return jsonify(resultado), 200


# Rotas para listar dados específico (Solo)
@api_routes.route('/api/solo', methods=['GET'])
def listar_solo():
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r:
        return jsonify({"erro": "Nenhum registro encontrado"}), 404

    resultado = {
        "id": r.id,
        "device_id": r.device_id,
        "timestamp": r.timestamp,
        "solo": {
            "humidade": r.humidade_solo
        }
    }

    return jsonify(resultado), 200


# Rotas para listar dados específico (Vibração)
@api_routes.route('/api/vibracao', methods=['GET'])
def listar_vibracao():
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r:
        return jsonify({"erro": "Nenhum registro encontrado"}), 404

    resultado = {
        "id": r.id,
        "device_id": r.device_id,
        "timestamp": r.timestamp,
        "vibracao": {
            "detectada": r.vibracao
        }
    }

    return jsonify(resultado), 200


# Rotas para listar dados específico (Visão computacional)
#@api_routes.route('/api/visao', methods=['GET'])
#def listar_visao():
 #   r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
  #  if not r:
   #     return jsonify({"erro": "Nenhum registro encontrado"}), 404

    #resultado = {
     #   "id": r.id,
      #  "device_id": r.device_id,
       # "timestamp": r.timestamp,
        #"visao": {
         #   "detecao_praga": r.detecao_praga,
          #  "tipo_praga": r.tipo_praga,
    #        "confianca": r.confianca
     #   }
    #}

    #return jsonify(resultado), 200


# Rotas para gerar alertas baseado nos dados
@api_routes.route('/api/alertas', methods=['GET'])
def listar_alertas():
    registros = DadosIoT.query.order_by(DadosIoT.id.desc()).limit(100).all()

    resultado = []

    for r in registros:
        # Gerar alertas baseado nas condições dos dados
        #if r.detecao_praga == True:
         #   resultado.append({
          #      "id": f"ALT-{r.id}-praga",
           #     "tipo": "Praga",
        #    #    "mensagem": f"Detecção de praga: {r.tipo_praga or 'desconhecida'}",
         #       "severidade": "crítico" if r.confianca and r.confianca > 0.8 else "aviso",
          #      "timestamp": r.timestamp,
           #     "status": "ativo"
           # })

        if r.humidade_solo is not None and r.humidade_solo < 30:
            resultado.append({
                "id": f"ALT-{r.id}-solo",
                "tipo": "Solo",
                "mensagem": f"Humidade do solo baixa: {r.humidade_solo:.1f}%",
                "severidade": "crítico",
                "timestamp": r.timestamp,
                "status": "ativo"
            })

        if r.temperatura_ar is not None and (r.temperatura_ar < 15 or r.temperatura_ar > 35):
            resultado.append({
                "id": f"ALT-{r.id}-temp",
                "tipo": "Clima",
                "mensagem": f"Temperatura fora dos limites: {r.temperatura_ar:.1f}°C",
                "severidade": "aviso",
                "timestamp": r.timestamp,
                "status": "ativo"
            })

        if r.vibracao == True:
            resultado.append({
                "id": f"ALT-{r.id}-vib",
                "tipo": "Sensor",
                "mensagem": "Vibração detectada no equipamento",
                "severidade": "aviso",
                "timestamp": r.timestamp,
                "status": "ativo"
            })

    return jsonify(resultado), 200