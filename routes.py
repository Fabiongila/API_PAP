from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, DadosIoT

api_routes = Blueprint('api', __name__)


# Rota para receber dados do dispositivo IoT
@api_routes.route('/api/dados', methods=['POST'])
def receber_dados():

    dados = request.get_json()

    record = DadosIoT(
        device_id=dados['device_id'],
        timestamp=dados.get('timestamp', datetime.utcnow().isoformat()),

        latitude=dados['gps']['latitude'],
        longitude=dados['gps']['longitude'],

        temperatura_ar=dados['bme280']['temperatura'],
        humidade_ar=dados['bme280']['humidade'],
        pressao_ar=dados['bme280']['pressao'],

        humidade_solo=dados['solo']['humidade'],
        vibracao=dados['vibracao']['detectada'],

        detecao_praga=dados['visao']['detecao_praga'],
        tipo_praga=dados['visao']['tipo_praga'],
        confianca=dados['visao']['confianca']
    )

    db.session.add(record)
    db.session.commit()
    print("API is running...")
    return jsonify({
        "status": "sucesso",
        'mensagems': 'API is running',
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

            "visao": {
                "detecao_praga": r.detecao_praga,
                "tipo_praga": r.tipo_praga,
                "confianca": r.confianca
            }
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
@api_routes.route('/api/visao', methods=['GET'])
def listar_visao():
    r = DadosIoT.query.order_by(DadosIoT.id.desc()).first()
    if not r:
        return jsonify({"erro": "Nenhum registro encontrado"}), 404

    resultado = {
        "id": r.id,
        "device_id": r.device_id,
        "timestamp": r.timestamp,
        "visao": {
            "detecao_praga": r.detecao_praga,
            "tipo_praga": r.tipo_praga,
            "confianca": r.confianca
        }
    }

    return jsonify(resultado), 200