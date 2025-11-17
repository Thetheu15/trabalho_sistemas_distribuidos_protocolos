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

## Protocolo Strings

No protocolo **Strings**, todas as mensagens trafegam como texto puro, estruturado manualmente usando separadores.  
O formato segue a convenção:

AUTH/OP/INFO/LOGOUT|param1|param2|...|FIM

O protocolo baseado em Strings organiza todas as mensagens como sequências de texto simples, nas quais:

- O primeiro campo indica o **tipo de resposta** (normalmente `OK` ou `ERR`).
- Os campos seguintes seguem o formato **chave=valor**, separados por barras verticais (`|`).
- A mensagem é sempre finalizada com o marcador `|FIM`, que o cliente utiliza como delimitador para encerrar a leitura do socket.

Esse modelo exige que o receptor faça o *parsing* manual, dividindo o texto com `split("|")` e validando a presença dos campos obrigatórios — o que torna o protocolo mais suscetível a erros estruturais caso algum caractere inesperado apareça.

Por outro lado, trata-se do protocolo mais simples e com maior **legibilidade imediata para humanos**, além de não requerer bibliotecas externas, sendo ideal para depuração rápida e interoperabilidade mínima.

## Protocolo JSON

No protocolo **JSON**, as mensagens são estruturadas usando objetos JSON convertidos para texto.  
Toda requisição e resposta segue uma estrutura semelhante a:

```json
{
    "tipo": "operacao",
    "token": "abc123",
    "operacao": "soma",
    "parametros": { "numeros": [1, 2, 3] },
    "timestamp": "2025-11-16T20:30:00"
}´´´

JSON permite aninhamento por meio de listas e objetos, o que facilita o envio e a organização de informações complexas, além de ser autodescritivo e amplamente compatível com praticamente qualquer linguagem. No protocolo utilizado, o servidor envia as respostas também em JSON, sempre finalizadas por um caractere de nova linha (\n) para facilitar a delimitação e leitura; já o cliente, ao receber esses dados, realiza a validação da estrutura antes de processá-la, garantindo que o conteúdo seja bem formado. Como resultado, este protocolo alcança um bom equilíbrio entre legibilidade, padronização e simplicidade de implementação, sendo também menos suscetível a ambiguidades quando comparado ao protocolo baseado em Strings.

## Protocolo Protobuf

O **Protobuf** utiliza mensagens binárias serializadas, compactas e rigidamente definidas através de um arquivo `.proto`. A estrutura segue:

- Cada mensagem é enviada com um **header de 4 bytes (big-endian)** indicando o tamanho do payload.
- O **payload** é um bloco binário gerado pela serialização de uma mensagem `Requisicao` ou `Resposta`.

### Exemplo

[00 00 01 2E][payload binário...]


O formato de mensagens no protocolo Protobuf é altamente estruturado e rigidamente definido no arquivo `.proto`, onde cada tipo, campo e valor possível é especificado antecipadamente, eliminando ambiguidade e garantindo validação automática.

As respostas do servidor utilizam:

- **maps** (`map<string, string>`)
- Estruturas **oneof** (como `ok` ou `erro`)

Esses elementos permitem que o cliente interprete corretamente o tipo e conteúdo da mensagem recebida.

Além disso, o Protobuf se destaca pela **eficiência**:

- Gera payloads muito menores  
- Possui parsing significativamente mais rápido que JSON ou Strings  
- É ideal para comunicação de alta performance

A principal desvantagem está na **baixa legibilidade humana**: as mensagens não podem ser facilmente compreendidas sem ferramentas ou bibliotecas específicas, dificultando a depuração ou inspeção manual durante o desenvolvimento.


