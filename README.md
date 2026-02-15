# API_PAP
API que recebe dados de sensores e ESP32-CAM





Estrutura exemplar dos dados:

": {
    "detecao_praga": true,
    "tip{
  "device_id": "SENSOR_001",
  "timestamp": "2026-02-14T10:30:45.123456",
  "gps": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "bme280": {
    "temperatura": 24.5,
    "humidade": 65.3,
    "pressao": 1013.25
  },
  "solo": {
    "humidade": 45.2
  },
  "vibracao": {
    "detectada": false
  },
  "visaoo_praga": "Afídeo",
    "confianca": 0.92
  }
}
```

## Endpoints da API

### POST /api/dados
Recebe os dados de todos os sensores e armazena na base de dados.

**Método:** POST  
**Body:** JSON com a estrutura exemplar acima
### POST https://api-pap-dqtp.onrender.com/api/dados
Recebe os dados de todos os sensores e armazena na base de dados.

**Método:** POST  
**Body:** JSON com a estrutura exemplar acima

**Resposta (201):**
```json
{
  "status": "sucesso",
  "mensagem": "Dados recebidos e armazenados"
}
```

---

### GET https://api-pap-dqtp.onrender.com/api/dados_sensores
Retorna os últimos 10 registros de todos os sensores.

**Método:** GET  
**Resposta (200):** Array com todos os dados combinados
### GET https://api-pap-dqtp.onrender.com/api/dados_sensores
Retorna os últimos 10 registros de todos os sensores.

**Método:** GET  
**Resposta (200):** Array com todos os dados combinados

---

### GET https://api-pap-dqtp.onrender.com/api/gps
Retorna o registro mais recente do sensor GPS.

**Método:** GET  
**Resposta (200):**
### GET https://api-pap-dqtp.onrender.com/api/gps
Retorna o registro mais recente do sensor GPS.

**Método:** GET  
**Resposta (200):**
```json
{
  "id": 1,
  "device_id": "SENSOR_001",
  "timestamp": "2026-02-14T10:30:45.123456",
  "gps": {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

---

### GET https://api-pap-dqtp.onrender.com
/api/bme280
Retorna o registro mais recente do sensor BME280 (temperatura, humidade e pressão do ar).

**Método:** GET  
**Resposta (200):**
### GET https://api-pap-dqtp.onrender.com/api/bme280
Retorna o registro mais recente do sensor BME280 (temperatura, humidade e pressão do ar).

**Método:** GET  
**Resposta (200):**
```json
{
  "id": 1,
  "device_id": "SENSOR_001",
  "timestamp": "2026-02-14T10:30:45.123456",
  "bme280": {
    "temperatura": 24.5,
    "humidade": 65.3,
    "pressao": 1013.25
  }
}
```

---

### GET https://api-pap-dqtp.onrender.com/api/solo
Retorna o registro mais recente de humidade do solo.

**Método:** GET  
**Resposta (200):**
### GET https://api-pap-dqtp.onrender.com/api/solo
Retorna o registro mais recente de humidade do solo.

**Método:** GET  
**Resposta (200):**
```json
{
  "id": 1,
  "device_id": "SENSOR_001",
  "timestamp": "2026-02-14T10:30:45.123456",
  "solo": {
    "humidade": 45.2
  }
}
```

---

### GET https://api-pap-dqtp.onrender.com/api/vibracao
Retorna o registro mais recente de vibração.

**Método:** GET  
**Resposta (200):**
### GET https://api-pap-dqtp.onrender.com/api/vibracao
Retorna o registro mais recente de vibração.

**Método:** GET  
**Resposta (200):**
```json
{
  "id": 1,
  "device_id": "SENSOR_001",
  "timestamp": "2026-02-14T10:30:45.123456",
  "vibracao": {
    "detectada": false
  }
}
```

---

### GET https://api-pap-dqtp.onrender.com/api/visao
Retorna o registro mais recente de detecção de pragas.

**Método:** GET  
**Resposta (200):**
### GET https://api-pap-dqtp.onrender.com/api/visao
Retorna o registro mais recente de detecção de pragas.

**Método:** GET  
**Resposta (200):**
```json
{
  "id": 1,
  "device_id": "SENSOR_001",
  "timestamp": "2026-02-14T10:30:45.123456",
  "visao": {
    "detecao_praga": true,
    "tipo_praga": "Afídeo",
    "confianca": 0.92
  }
}
```