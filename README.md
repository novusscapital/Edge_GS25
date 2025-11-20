# SkillHub Comfort Monitor — IoT + FIWARE + Dashboard
Projeto desenvolvido para a GS25 — Edge Computing & Web Development

FIAP — 2025

## Visão Geral

O SkillHub Comfort Monitor é um sistema IoT inteligente capaz de medir temperatura, umidade e luminosidade, avaliando em tempo real a confortabilidade do ambiente para estudos e foco.

Ele integra:

- ESP32 (sensores físicos/simulados via Wokwi)
- FIWARE (IoT-Agent, Orion e STH-Comet) em uma VM Azure
- Postman (provisionamento e testes das rotas)
- Dashboard interativo em Python (Dash)
- Widget integrado ao projeto web SkillHub

O objetivo é oferecer uma solução moderna, acessível e inteligente para monitoramento de ambientes, aplicando conceitos de IoT, cloud computing, protocolos Ultralight, Context Broker e visualização profissional de dados.

## Arquitetura Geral do Sistema
```
+-------------------+         UL (HTTP)       +-----------------+
|      ESP32        |  -------------------->  |   IoT-Agent     |
| DHT22 + LDR (Wokwi)|                         |   Ultralight    |
+-------------------+                         +-----------------+
         |                                              |
         | HTTP POST (t|24.5|h|52|l|77)                 |
         v                                              v
+-------------------+                         +-----------------+
|       WIFI        |                         |     ORION       |
|  Wokwi-GUEST      |                         | Context Broker  |
+-------------------+                         +-----------------+
                                                          |
                                                          | Histórico
                                                          v
                                                +---------------------+
                                                |     STH-Comet       |
                                                +---------------------+
                                                          |
                                                          v
                                            +------------------------------+
                                            |   Dashboard Python (Dash)    |
                                            +------------------------------+
                                                          |
                                                          v
                                        +--------------------------------------+
                                        |     Widget SkillHub (Frontend)      |
                                        +--------------------------------------+
```
## Funcionalidades Principais

- Coleta de dados ambientais
  - Temperatura (°C)
  - Umidade (%)
  - Luminosidade (0–100)

- Envio para o FIWARE
  - Formato Ultralight 2.0
  - IoT-Agent Ultralight (porta 7896)
  - Context Broker Orion (porta 1026)

- Processamento e análise
  - O dashboard classifica o ambiente como:

| Condição | Cor | Critério |
|----------|-----|-----------|
| Excelente | Verde | Todos os parâmetros dentro da faixa |
| Atenção | Amarelo | 1 parâmetro fora do ideal |
| Ruim | Vermelho | 2 ou mais fora |
| Não localizado | Azul | Dispositivo offline |

- Visualização em Dashboard
  - Inclui:
    - Condição geral do ambiente
    - Valores atuais
    - Parâmetros fora do ideal
    - Última atualização
    - (Opcional) Gráficos históricos
    - (Opcional) Link para SkillHub

## Faixas Ideais do Sistema

| Parâmetro | Mínimo | Máximo | Unidade |
|-----------|--------|--------|---------|
| Temperatura | 20.0 | 26.0 | °C |
| Umidade | 40 | 60 | % |
| Luminosidade | 30 | 80 | escala 0–100 |

Qualquer valor fora desses limites é detectado automaticamente pelo dashboard.

## Tecnologias Utilizadas

### IoT e Simulação
- ESP32 DevKit v1
- Sensor DHT22
- Sensor LDR
- Wokwi Simulator

### FIWARE Platform
- IoT-Agent Ultralight
- Orion Context Broker
- STH-Comet (histórico)
- MongoDB
- Mosquitto (brokers auxiliares)

### Cloud
- Máquina Virtual Azure Ubuntu 24.04
- Docker + Docker Compose

### Web & Dev Tools
- Postman Collections (provisionamento)
- SkillHub Frontend (React + Vite)
- Python (Dash) — Dashboard

## Provisionamento (Postman)

A collection inclui:

### Health Checks
- IoT-Agent
- Orion
- STH-Comet

### Service Groups
- Criar serviço
- Listar serviços
- Deletar serviços

### Devices
- Registrar dispositivo
- Listar dispositivos
- Deletar dispositivos

### Measurements
- Enviar métricas simuladas
- Validar integração

### Context & Histórico
- Get contexto atual
- Get histórico de temperatura (STH-Comet)

Arquivo para import: `SkillHub_Comfort_Monitor.postman_collection.json`

## Código do ESP32 (Resumo)

Conecta ao Wi-Fi
Lê DHT22 e LDR
Monta payload Ultralight
Envia para: `http://<AZURE_IP>:7896/iot/d?i=comfort001&k=comfortkey`

Headers essenciais:
- Fiware-Service: skillhub
- Fiware-ServicePath: /

## Dashboard Python (Dash)

O dashboard:
- Lê dados do Orion via HTTP
- Classifica o ambiente
- Exibe parâmetros
- Simula modo offline
- Atualiza automaticamente a cada 5 segundos

Opcional:
- gráfico de histórico
- filtro entre temperatura / umidade / luminosidade

Execução:
- python -m venv venv
- venv\Scripts\activate
- gitclone no EdgeGS_25
- cd em EdgeGS_25
- pip install -r requirements.txt
- python skillhub.py

Acessar: `http://localhost:8050`

## Integração com o SkillHub

Este projeto também funciona como um Widget IoT do SkillHub, possibilitando:
- Visualização em tempo real no painel do usuário
- Alertas ambientais
- Personalização por cômodo
- Expansão futura para outros sensores

## Vídeo de Demonstração
- SkillHub Comfort Monitor - Youtube: [https://youtu.be/bYOBxKSQ-5E]
- SkillHub Comfort Monitor - Wowki: [https://wokwi.com/projects/448084989566067713]


O vídeo inclui:
- Arquitetura do sistema
- Funcionamento no Wokwi
- Integração com FIWARE (Azure)
- Testes via Postman
- Dashboard em operação
- Cenário de uso e dificuldades enfrentadas
- Relação com o projeto SkillHub

## Equipe

- Henrique Keigo Nakashima Minowa — RM 564091
- Eduardo Delorenzo Moraes — RM 561749
- Matheus Bispo Faria Barbosa — RM 562140

## Licença

Uso acadêmico — FIAP 2025.
