# trabalho_sistemas_distribuidos_protocolos

Para a execução correta do código, execute o arquivo denominado main.py e siga as instruções dadas por ele.

# Introdução

Este relatório apresenta o desenvolvimento de um sistema cliente capaz de se comunicar com um servidor remoto utilizando três protocolos distintos: **Strings**, **JSON** e **Protobuf**. O objetivo principal foi projetar uma solução robusta que suportasse comunicação síncrona baseada em sockets TCP, garantindo interoperabilidade, avaliação de desempenho entre formatos e tolerância a falhas de rede.

A metodologia envolveu análise do formato de cada protocolo, implementação de clientes independentes seguindo um padrão arquitetural, criação de camada de tratamento de erros e estruturação de um menu unificado para facilitar o uso pelos testes. Ao final, foi realizada uma análise comparativa considerando desempenho, legibilidade, tamanho das mensagens e resiliência a falhas.

# Metodologia

Para a implementação dos códigos, foi utilizado a linguagem de programação **Python**, pois possui uma diversidade de ferramentas que facilitam o desenvolvimento do trabalho.

Foram implementados três clientes, um para cada protocolo de comunicação, utilizando a biblioteca `sockets` do Python. Os protocolos abordados foram: **Protobuf**, **Strings** e **JSON**. Para cada um, foi criado um mecanismo de envio/recebimento, execução de testes funcionais para cada operação, além da coleta de métricas e análise comparativa entre protocolos.

O código de cada protocolo seguiu uma estrutura similar, possuindo as seguintes funções:

## Funções do cliente

### `enviar_mensagem()`
Esta função encapsula o ato de transmitir dados ao servidor através do socket. Converte a estrutura de dados para o formato apropriado ao protocolo:
- **Strings:** compõe a string com terminador e separadores.
- **JSON:** serializa para JSON com `\n`.
- **Protobuf:** serializa em binário com framing de 4 bytes (big-endian).

Trata exceções de rede (`BrokenPipe`, `connection reset`) lançando `ErroRede` quando necessário. Também registra a mensagem enviada e métricas como tamanho em bytes e timestamp de envio.

### `receber_mensagem()`
Lê do socket a resposta do servidor e converte para estrutura manejável. Implementa timeout para evitar bloqueios indefinidos e valida a integridade da mensagem:
- **Strings:** verifica o terminador `|FIM`.
- **JSON:** verifica parse correto.
- **Protobuf:** lê o cabeçalho de 4 bytes antes do payload e faz `ParseFromString`.

Campos obrigatórios são validados; erros lançam `ErroProtocolo`. Problemas de rede lançam `ErroRede`.

### `autenticar()`
Constrói e envia a mensagem de autenticação (contendo `aluno_id` e `timestamp`), aguarda resposta e extrai o token de sessão. Valida presença do token, sucesso do status e formato da resposta. Em caso de erro, lança `ErroProtocolo`. Mede latência da operação e registra logs.

### `soma()`
Solicita ao servidor o processamento de uma lista de números e recebe estatísticas (soma, média, máximo, mínimo, quantidade, timestamps). Valida campos da resposta e registra logs. Impressão legível inclui soma, média, max, min e tempo da operação.

### `echo()`
Envia mensagem ao servidor e recebe eco enriquecido (mensagem ecoada, hash MD5, tamanho, timestamp do servidor). Valida campos essenciais e registra logs. Mostra resultado legível com tempo da operação.

### `op_timestamp()`
Solicita informações temporais (timestamp Unix, ISO, componentes de data/hora). Valida campos, registra e imprime timestamp legível e latência.

### `status()`
Obtém o estado do servidor (status, número de sessões, operações processadas, métricas simuladas). Valida mapas de métricas, registra logs e imprime tempo de resposta.

### `historico()`
Recupera histórico de operações do aluno. Valida formato (lista/dicionário), imprime tabela legível das últimas operações e registra logs. Tenta parsear strings serializadas se necessário.

### `info()`
Obtém metadados do servidor (nome, versão, host, porta, protocolo, formato aceito, operações disponíveis). Valida retorno e imprime resumo legível, registrando logs.

### `logout()`
Finaliza a sessão no servidor: envia logout e aguarda confirmação. Valida sucesso, registra logs e fecha o socket de forma ordenada. Resiliência a desconexões é garantida.

## Tratamento de erros e métricas
Todas as funções de IO de rede possuem:
- Timeout de **4–5 segundos**.
- Captura de `socket.timeout` transformado em `ErroRede`.
- Validação de protocolo (`ErroProtocolo`) para mensagens malformadas.
- Registro de latência de envio → recebimento.
- Logs completos das respostas brutas e formatação legível para análise comparativa.

## Estrutura de mensagens por protocolo

### Protocolo Strings
Mensagens trafegam como texto puro, estruturado manualmente:

