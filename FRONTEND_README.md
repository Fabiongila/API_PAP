# 🌿 AgroCaua Frontend

Sistema de monitoramento agrícola inteligente com dashboard moderno construído com Flask, Tailwind CSS v4, e Chart.js.

## 📋 Estrutura do Projeto

```
API_PAP/
├── static/
│   ├── css/
│   │   ├── main.css          # Tailwind source com design tokens
│   │   └── output.css        # CSS compilado
│   └── js/
│       ├── api.js            # Cliente API com autenticação JWT
│       ├── formatters.js     # Formatadores de data/números
│       └── notifications.js  # Sistema de notificações toast
├── templates/
│   ├── base.html            # Layout base com sidebar/topbar
│   ├── base_auth.html       # Layout para páginas de autenticação
│   ├── components/
│   │   ├── sidebar.html     # Navegação lateral
│   │   └── topbar.html      # Barra superior com busca e perfil
│   ├── auth/
│   │   ├── login.html       # Página de login
│   │   └── register.html    # Página de registro
│   └── dashboard/
│       ├── index.html       # Dashboard principal com KPIs e gráficos
│       ├── gps.html         # Monitoramento GPS
│       ├── clima.html       # Dados climáticos (BME280)
│       ├── solo.html        # Humidade do solo
│       └── visao.html       # Detecção de pragas
├── app.py                   # Aplicação Flask principal
├── dashboard_routes.py      # Rotas do frontend
├── routes.py               # Rotas da API
└── auth_routes.py          # Rotas de autenticação

package.json                 # Dependências npm
postcss.config.js           # Configuração PostCSS + Tailwind v4
```

## 🚀 Instalação e Execução

### 1. Instalar Dependências Python

```bash
cd API_PAP
pip install -r requirements.txt
```

### 2. Instalar Dependências Node.js

```bash
npm install
```

### 3. Compilar CSS

```bash
# Build uma vez
npm run build

# Ou modo watch para desenvolvimento
npm run dev
```

### 4. Executar o Servidor Flask

```bash
cd API_PAP
python app.py
```

O servidor estará rodando em:
- **Frontend**: http://localhost:5000
- **API**: http://localhost:5000/api

## 🎨 Design System

### Paleta de Cores

| Cor | Hex | Uso |
|-----|-----|-----|
| green-900 | #0F3D2E | Headers, textos escuros |
| green-700 | #1F6F54 | Sidebar ativa |
| green-600 | #2F855A | Botões primários |
| green-500 | #38A169 | Hover states |
| green-100 | #D1FAE5 | Backgrounds claros |
| earth-500 | #C19A6B | Elementos secundários |
| soil-700 | #8B5E3C | Dados de solo |
| success | #10B981 | Estados de sucesso |
| warning | #F59E0B | Alertas |
| danger | #EF4444 | Erros, crítico |
| info | #3B82F6 | Informações |

### Tipografia

- **Fonte**: Inter (Google Fonts)
- **Tamanhos**: text-5xl (hero), text-3xl (h1), text-2xl (h2), text-xl (h3), text-base (corpo)

### Componentes

- **Cards**: rounded-2xl, padding 1.5rem, shadow-sm
- **Botões**: rounded-xl, padding 0.75rem 1.5rem, transições suaves
- **Inputs**: rounded-xl, border focus com ring verde
- **Badges**: rounded-xs, cores semânticas

## 📱 Páginas Disponíveis

### Autenticação

- `/login` - Login de utilizadores
- `/register` - Registo de novos utilizadores

### Dashboard (Requer Autenticação)

- `/dashboard` - Dashboard principal com KPIs e gráficos
- `/dashboard/gps` - Monitoramento de localização GPS
- `/dashboard/clima` - Dados climáticos (temperatura, humidade, pressão)
- `/dashboard/solo` - Monitoramento de humidade do solo
- `/dashboard/visao` - Detecção de pragas via visão computacional

## 🔐 Autenticação

O frontend usa JWT (JSON Web Tokens) para autenticação:

1. **Login**: POST `/login` com email e password
2. **Token**: Armazenado em `localStorage` como `agrocaua_token`
3. **API Calls**: Token enviado automaticamente no header `Authorization: Bearer <token>`
4. **Logout**: POST `/api/logout` + limpeza do localStorage
5. **Proteção**: Redirecionamento automático para login se token inválido/expirado

## 📊 Funcionalidades

### Dashboard Principal

- **KPI Cards**: Temperatura, humidade do ar, humidade do solo, detecção de pragas
- **Gráficos**: Tendências de temperatura e humidade (Chart.js)
- **Tabela**: Últimas leituras de todos os sensores
- **Auto-refresh**: Atualização automática a cada 30 segundos

### Páginas de Sensores

Cada página de sensor inclui:
- Cards KPI com valores atuais
- Gráficos de tendência temporal
- Tabela de histórico
- Status e recomendações (solo, visão)
- Alertas visuais para detecção de pragas

### Interatividade

- **Alpine.js**: Dropdowns, menus, modais
- **Vanilla JS**: Fetch API, manipulação DOM, charts
- **Toast Notifications**: Feedback de ações do usuário
- **Loading States**: Spinners durante carregamento
- **Error Handling**: Mensagens de erro amigáveis

## 🛠️ Desenvolvimento

### Modificar Estilos

Edite `API_PAP/static/css/main.css` e execute:

```bash
npm run build
```

### Adicionar Novos Ícones

Lucide Icons via CDN:
```html
<i class="icon-[nome-do-icone]"></i>
```

Lista completa: https://lucide.dev/icons

### Criar Nova Página

1. Criar template em `API_PAP/templates/dashboard/`
2. Adicionar rota em `API_PAP/dashboard_routes.py`
3. Adicionar link na sidebar (`components/sidebar.html`)

## 📦 Dependências

### Frontend

- **Tailwind CSS v4**: Framework CSS utility-first
- **Alpine.js**: Framework JS leve para interatividade
- **Chart.js**: Biblioteca de gráficos
- **Lucide Icons**: Conjunto de ícones

### Backend

- **Flask**: Framework web Python
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-SQLAlchemy**: ORM
- **Flask-CORS**: Suporte CORS

## 🔧 Configuração

### Variáveis de Ambiente (opcional)

```bash
export PORT=5000
export FLASK_ENV=development
```

### PostCSS Plugins

- `postcss-import`: Importar CSS
- `@tailwindcss/postcss`: Tailwind v4
- `postcss-preset-env`: Suporte CSS moderno

## 📝 Notas

- **Tailwind v4**: Usa `@import "tailwindcss"` em vez de `@tailwind` directives
- **JWT Client-Side**: Verificação de token acontece no JavaScript, não em decorators Flask
- **CORS**: Habilitado para permitir chamadas API de diferentes origens
- **Responsivo**: Layout adaptável para mobile (sidebar colapsável)

## 🚀 Deploy

Para produção, considere:

1. Compilar CSS em modo produção
2. Usar servidor WSGI (Gunicorn)
3. Configurar HTTPS
4. Usar variáveis de ambiente para secrets
5. Configurar CORS adequadamente

## 🤝 Próximas Funcionalidades

- [ ] Integração com Google Maps para GPS
- [ ] Gráficos de pressão atmosférica
- [ ] Sistema de notificações push
- [ ] Exportação de dados (CSV, PDF)
- [ ] Dashboard personalizável
- [ ] Modo escuro
- [ ] PWA (Progressive Web App)
- [ ] Gestão de múltiplos dispositivos
- [ ] Análise preditiva com IA

---

**Desenvolvido com** 🌱 **para agricultura inteligente**
