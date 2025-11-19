# Relatório do trabalho de sistemas distribuidos protocolos de comunicação

- Link para o vídeo: https://youtu.be/4pUbes9OSLw?feature=shared

**Aluno:** Antonio Matheus Monteiro da Silva
**Matrícula:** 554229

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

{
    "tipo": "operacao",
    "token": "abc123",
    "operacao": "soma",
    "parametros": { "numeros": [1, 2, 3] },
    "timestamp": "2025-11-16T20:30:00"
}

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

# Análise comparativa

A partir da execução dos códigos, e a realização das consultas a cada método disponível no servidor, foi obtido as seguintes métricas:

**1. Soma**

| Protocolo | Tamanho (bytes) | Serialização (ms) | Tempo total (ms) |
|-----------|------------------|-------------------|------------------|
| Strings   | 114              | 0.00              | 101.92           |
| JSON      | 171              | 0.05              | 95.41            |
| Protobuf  | 100              | 0.08              | 95.48            |

**2. Echo**

| Protocolo | Tamanho (bytes) | Serialização (ms) | Tempo total (ms) |
|-----------|------------------|-------------------|------------------|
| Strings   | 114              | 0.00              | 95.24            |
| JSON      | 171              | 0.04              | 95.50            |
| Protobuf  | 100              | 0.02              | 96.02            |

**3. Timestamp**

| Protocolo | Tamanho (bytes) | Serialização (ms) | Tempo total (ms) |
|-----------|------------------|-------------------|------------------|
| Strings   | 114              | 0.00              | 96.62            |
| JSON      | 171              | 0.05              | 95.40            |
| Protobuf  | 100              | 0.04              | 95.01            |

**4. Status**

| Protocolo | Tamanho (bytes) | Serialização (ms) | Tempo total (ms) |
|-----------|------------------|-------------------|------------------|
| Strings   | 114              | 0.00              | 98.29            |
| JSON      | 171              | 0.05              | 95.85            |
| Protobuf  | 100              | 0.04              | 95.86            |

**5. Histórico**

| Protocolo | Tamanho (bytes) | Serialização (ms) | Tempo total (ms) |
|-----------|------------------|-------------------|------------------|
| Strings   | 114              | 0.00              | 127.06           |
| JSON      | 171              | 0.05              | 99.63            |
| Protobuf  | 100              | 0.07              | 98.31            |

**6. Info**

| Protocolo | Tamanho (bytes) | Serialização (ms) | Tempo total (ms) |
|-----------|------------------|-------------------|------------------|
| Strings   | 114              | 0.00              | 88.25            |
| JSON      | 171              | 0.08              | 88.35            |
| Protobuf  | 100              | 0.02              | 87.78            |

**Comparativo geral**

| Métrica              | Strings       | JSON          | Protobuf      |
|---------------------|---------------|---------------|---------------|
| Tamanho Médio       | ~114 bytes    | ~171 bytes    | **~100 bytes** |
| Serialização Média  | ~0.00 ms      | ~0.05 ms      | ~0.05 ms      |
| Tempo Médio         | ~101 ms       | ~95 ms        | **~95 ms**     |
| Sucesso             | 100%          | 100%          | 100%          |
| Legibilidade        | Alta          | Alta          | Baixa         |
| Eficiência Geral    | Regular       | Boa           | **Excelente** |


A partir dos resultados obtidos, observou-se que o protocolo Protobuf apresentou o melhor desempenho geral, com o menor tamanho médio de mensagem (~100 bytes) e tempo médio de resposta equivalente ao JSON (~95 ms). O JSON se destacou pelo equilíbrio entre legibilidade e eficiência, sendo altamente estruturado, facilmente interpretável e apresentando tempos similares ao Protobuf, apesar do tamanho médio de mensagem aproximadamente 70% maior (~171 bytes). O protocolo Strings, após a correção de formato do token, passou a executar todas as operações corretamente, porém apresentou mensagens maiores que o Protobuf (~114 bytes) e maior tempo médio de processamento (~101 ms), sobretudo na operação Histórico, que exigiu tratamento de dados mais volumosos. Além disso, por ser baseado em texto puro, o protocolo Strings demonstrou maior suscetibilidade a erros de formatação. Conclui-se que, para cenários de alta performance e otimização de rede, o Protobuf é a melhor opção, enquanto o JSON é mais indicado quando legibilidade e interoperabilidade são relevantes, e o Strings é adequado apenas para ambientes simples ou com baixo nível de estruturação dos dados.

## Conclusão

Com base nos resultados obtidos, conclui-se que a implementação dos três protocolos foi realizada com sucesso, permitindo uma avaliação comparativa precisa entre suas características de desempenho, eficiência e adequação a diferentes contextos de uso. O protocolo Protobuf demonstrou a melhor performance geral, apresentando as menores mensagens transmitidas, baixa latência e excelente estabilidade, sendo ideal para aplicações de alto desempenho e sistemas distribuídos com grande volume ou frequência de requisições. O protocolo JSON apresentou comportamento consistente e equilibrado, combinando legibilidade, estruturação de dados e bons resultados de tempo de resposta, o que o torna altamente recomendável para sistemas que priorizam facilidade de manutenção, integração e interoperabilidade entre serviços. Já o protocolo Strings, embora funcional e de fácil interpretação humana, mostrou-se menos robusto e mais suscetível a erros de formatação, além de apresentar menor eficiência na troca de dados, sendo mais adequado a implementações simples ou em fases iniciais de prototipagem.

De forma geral, a experiência adquirida com este trabalho permitiu compreender a importância de escolher corretamente o protocolo de comunicação com base nas necessidades do sistema, considerando fatores como complexidade da aplicação, disponibilidade de recursos computacionais, requisitos de interoperabilidade e desempenho. A implementação dos clientes, aliada aos testes realizados, proporcionou uma visão prática sobre os impactos do formato de mensagem, da estruturação dos dados e dos mecanismos de serialização no funcionamento de aplicações distribuídas. Assim, recomenda-se o uso de Protobuf para ambientes críticos e de alto desempenho, JSON para soluções escaláveis e de fácil integração, e Strings apenas em cenários com baixo volume de dados e requisitos mínimos de estruturação.
