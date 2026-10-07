# Simulador de Triagem Pré-Hospitalar

Simulador de treino em que o formando regista os sinais vitais e os sinais/sintomas de uma vítima fictícia, livremente ou passo a passo pela abordagem ABCDE, e um motor de pontuação sugere as situações clínicas mais compatíveis, com a atuação recomendada.

**[Abrir a versão online →](https://rolimjeferson26-cyber.github.io/simulador-triagem/)**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-online-2ea44f?logo=github)](https://rolimjeferson26-cyber.github.io/simulador-triagem/)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue)](LICENSE)

> [!WARNING]
> **Uso exclusivamente educativo.** Este simulador destina-se a sala de aula e formação. Não substitui a formação certificada nem os protocolos oficiais em vigor, e **não deve ser usado para apoio a decisão clínica em ocorrência real**.

---

## Sobre o projeto

Na formação de socorristas e bombeiros, treinar o raciocínio de triagem (olhar para um conjunto de achados e chegar à hipótese mais provável) depende muito de haver um formador disponível e de cenários preparados à mão. Este simulador dá ao formando um sítio para praticar esse raciocínio sozinho ou em aula, com casos de treino, gabarito e uma explicação de *porque* uma hipótese ficou à frente de outra.

É pensado para:
- **formandos e bombeiros**, que querem praticar a avaliação de vítimas fora de uma ocorrência real;
- **formadores**, que podem criar os seus próprios casos, ver o gabarito e comparar a resposta do formando com o esperado.

Criei este projeto a partir da minha experiência como Bombeiro EIP, para ter uma ferramenta de treino que refletisse a forma como a avaliação é feita no terreno. O conteúdo clínico foi organizado e revisto por mim, e a pontuação foi afinada com casos de teste até o ranking fazer sentido do ponto de vista operacional. É também o projeto onde junto as duas áreas em que trabalho: a emergência pré-hospitalar e o desenvolvimento de software.

## Capturas de ecrã

| | Desktop | Telemóvel |
|---|---|---|
| **Ecrã inicial** | <img src="docs/screenshots/01-inicio-desktop.webp" width="480" alt="Ecrã inicial com aviso de modo treino"> | <img src="docs/screenshots/01-inicio-mobile.webp" width="180" alt="Ecrã inicial no telemóvel"> |
| **Lista de casos** | <img src="docs/screenshots/02-casos-desktop.webp" width="480" alt="Lista de casos de treino"> | <img src="docs/screenshots/02-casos-mobile.webp" width="180" alt="Lista de casos no telemóvel"> |
| **Avaliação a meio** | <img src="docs/screenshots/03-avaliacao-desktop.webp" width="480" alt="Formulário com sinais vitais e sintomas preenchidos"> | <img src="docs/screenshots/03-avaliacao-mobile.webp" width="180" alt="Avaliação no telemóvel"> |
| **Resultado da triagem** | <img src="docs/screenshots/04-resultado-desktop.webp" width="480" alt="Resultado: Asma (crise moderada), 91% de compatibilidade"> | <img src="docs/screenshots/04-resultado-mobile.webp" width="180" alt="Resultado no telemóvel"> |
| **Parâmetros Vitais (4 anos)** | <img src="docs/screenshots/05-parametros-vitais-desktop.webp" width="480" alt="Parâmetros vitais do grupo 1-5 anos para uma criança de 4 anos"> | <img src="docs/screenshots/05-parametros-vitais-mobile.webp" width="180" alt="Parâmetros vitais no telemóvel"> |
| **Avaliação ABCDE: início** | <img src="docs/screenshots/06-abcde-inicio-desktop.webp" width="480" alt="Escolha entre avaliação livre e casos de treino"> | <img src="docs/screenshots/06-abcde-inicio-mobile.webp" width="180" alt="Início da avaliação ABCDE no telemóvel"> |
| **Avaliação ABCDE: letra B** | <img src="docs/screenshots/07-abcde-letra-b-desktop.webp" width="480" alt="Letra B com sinais vitais e achados marcados, e indicador de progresso"> | <img src="docs/screenshots/07-abcde-letra-b-mobile.webp" width="180" alt="Letra B no telemóvel"> |
| **Avaliação ABCDE: ações da letra** | <img src="docs/screenshots/08-abcde-acoes-desktop.webp" width="480" alt="Card de ações da letra B e caixa Ações realizadas"> | <img src="docs/screenshots/08-abcde-acoes-mobile.webp" width="180" alt="Ações da letra B no telemóvel"> |
| **Avaliação ABCDE: história e sintomas** | <img src="docs/screenshots/09-abcde-historia-desktop.webp" width="480" alt="Etapa História e sintomas com o seletor completo"> | <img src="docs/screenshots/09-abcde-historia-mobile.webp" width="180" alt="História e sintomas no telemóvel"> |
| **Avaliação ABCDE: resultado** | <img src="docs/screenshots/10-abcde-resultado-desktop.webp" width="480" alt="Resultado do motor no fim da avaliação ABCDE"> | <img src="docs/screenshots/10-abcde-resultado-mobile.webp" width="180" alt="Resultado no telemóvel"> |
| **Avaliação ABCDE: comparação com o gabarito** | <img src="docs/screenshots/11-abcde-comparacao-desktop.webp" width="480" alt="Comparação por letra entre achados esperados e marcados"> | <img src="docs/screenshots/11-abcde-comparacao-mobile.webp" width="180" alt="Comparação com o gabarito no telemóvel"> |

## Funcionalidades

**Caso Treino**
- **5 casos de treino incluídos** (2 de nível iniciante, 1 intermédio e 2 avançados, um deles propositadamente ambíguo), cada um com cenário escrito e gabarito.
- **Caso livre:** permite avaliar uma vítima sem cenário pré-definido.
- **Registo de 8 sinais vitais** (FC, FR, PAS, PAD, SpO2, temperatura, glicemia e Glasgow). Cada valor é traduzido de imediato num achado (por exemplo, "Taquicardia"), para o formando ver como o valor foi interpretado.
- **107 sinais e sintomas** organizados por grupos, com pesquisa sem acentos e por sinónimos comuns (ex.: "desmaio", "dor no peito"; lista em [`docs/sinonimos.md`](docs/sinonimos.md)), e destaque para os achados de alta relevância clínica.
- **Contexto da vítima:** os interruptores "trauma / sem trauma" e "adulto / pediátrico" decidem que fichas entram na análise.
- **Idade da vítima pediátrica:** no modo pediátrico, a idade (anos e meses) é obrigatória. Os sinais vitais passam a ser avaliados com os limites do grupo etário do INEM, e o resultado indica o grupo usado (por exemplo, "Sinais vitais avaliados para: 1-12 meses (INEM)").
- **Resultado com ranking** de até 4 hipóteses. Cada uma mostra a percentagem de compatibilidade, os achados que bateram e a indicação de bandeiras vermelhas.
- **Aviso de empate:** quando as hipóteses estão demasiado próximas, o simulador não escolhe uma e diz que faltam achados para diferenciar.
- **Atuação recomendada** para a hipótese destacada, com 47 planos de atuação, um por ficha.

**Modo instrutor**
- **Ver gabarito e preencher o formulário com os dados esperados** de cada caso.
- **Comparação automática** entre o resultado do motor e o gabarito do caso.
- **Editor de casos:** permite criar casos com resposta definida ou ambíguos (com vários candidatos válidos), e indicar a idade da vítima nos casos pediátricos.
- **Exportar e importar** os casos criados em ficheiro JSON, para os partilhar entre computadores.

**Avaliação ABCDE**
- **Ecrã "Antes de começar":** contexto de trauma, faixa etária e idade. Durante a avaliação fica só um resumo discreto no topo (ex.: "Pediátrico · 4 anos · Sem trauma"), com um link para alterar.
- **Avaliação guiada letra a letra:** A (via aérea), B (ventilação e oxigenação), C (circulação), D (função neurológica) e E (outras lesões e temperatura). Cada letra só abre depois de concluída a anterior.
- **Achados para selecionar em cada letra** (53 no total), os campos numéricos dessa letra e, no D, o estado de consciência em AVDS. Um sinal vital fora dos limites conta como achado e aparece como aviso no campo.
- **Uma letra de cada vez, com um só botão principal** (fixo no fundo do ecrã no telemóvel): "Nada encontrado" sem achados, ou "Ver ações" com achados. As ações abrem por baixo dos achados, e "Ações realizadas — avançar" conclui a letra.
- **Indicador de progresso** (A B C D E e história), com o estado de cada letra: bloqueada, em curso, concluída sem achados ou concluída com ações. Pode-se voltar a uma letra concluída. Se algo mudar, essa letra reabre e tem de ser concluída outra vez, e as seguintes mantêm os dados.
- **Etapa final "História e sintomas (CHAMU)"** com uma caixa de pesquisa: sugestões a partir de 2 letras, sem acentos e por sinónimos. O que se escolhe aparece como chips com "×". Os sinais já marcados nas letras não aparecem, e os que pertencem a uma letra aparecem apagados, com "ir para B".
- **Resultado:** resumo por letra (achados e ações realizadas) e o mesmo ranking e explicação do Caso Treino.
- **Dois modos:** avaliação livre, ou um dos casos de treino com cenário. No fim, o caso mostra a comparação com o gabarito: o diagnóstico e, por letra, os achados esperados vs. os marcados, com destaque para as letras onde havia achados e foi escolhido "Nada encontrado".

**Parâmetros Vitais**
- **Pesquisa por idade (anos + meses)** que devolve o grupo etário e, para esse grupo, os mesmos valores que o motor usa: FC, FR (com o aviso de bradipneia abaixo do mínimo), PAS normal e PAS mínima aceitável, SpO2, glicemia, temperatura e peso estimado. Para adultos, mostra as regras de adulto do motor.
- **Tabela de resumo dos 5 grupos etários**, para ver todos os valores de uma vez.
- **Uma só fonte de dados:** a consulta e o motor leem os mesmos limites (`limites_alerta_inem`, através da mesma função do `motor.js`), por isso nunca podem mostrar valores diferentes.

## Como funciona o motor de pontuação

O motor está em [`motor_pontuacao.py`](motor_pontuacao.py) e foi replicado em JavaScript em [`motor.js`](motor.js), com as mesmas constantes e a mesma lógica. O `motor.js` é partilhado pelo Caso Treino e pela Avaliação ABCDE e corre no browser. O script Python serve para testar e afinar o motor, e um teste automático confirma que as duas versões dão os mesmos resultados.

```mermaid
flowchart LR
    V["Sinais vitais<br/>(FC, FR, PAS, SpO2…)"] -->|"regras da taxonomia<br/>ou limites INEM<br/>por idade"| T["Conjunto de tags"]
    S["Sinais e sintomas<br/>selecionados"] --> T
    C{"Contexto<br/>trauma / pediátrico"} -->|"filtra as fichas<br/>em disputa"| P
    T --> P["Pontuação de cada<br/>ficha / variante<br/>precisão × cobertura → F1"]
    P --> F["Filtros: ≥ 2 critérios,<br/>F1 ≥ 25%, top 4"]
    F --> D{"Outras hipóteses a<br/>menos de 12 pontos<br/>do 1.º lugar?"}
    D -->|sim| E["Grupo empatado:<br/>achados insuficientes<br/>para diferenciar"]
    D -->|não| R["Hipótese destacada<br/>+ atuação recomendada"]
```

### 1. Dos dados da vítima às tags
Tudo o que o motor compara é uma **tag** (por exemplo, `dispneia`, `taquicardia`). Os sinais e sintomas já são tags. Os sinais vitais são convertidos pelas regras de [`taxonomia.json`](taxonomia.json), que tem 14 regras para 8 parâmetros. Cada regra tem um mínimo e/ou um máximo: FC ≥ 101 bpm ativa `taquicardia`, SpO2 abaixo do limite ativa `spo2_baixo`, e assim por diante. Estas são as regras de adulto. Em vítimas pediátricas, algumas são substituídas pelos limites do grupo etário (ver o ponto 7).

### 2. Cada ficha tem critérios com peso
Em [`criterios.json`](criterios.json) há **47 fichas** em 10 categorias. Cada critério é uma tag com **peso de 1 a 3**. Algumas fichas dividem-se em variantes que disputam o ranking como se fossem fichas separadas:
- 33 fichas simples;
- 7 divididas **por gravidade** (ex.: asma ligeira / moderada / grave);
- 7 divididas **por subtipo** (ex.: as lesões do trauma torácico, as síndromes tóxicas).

No total entram na disputa **79 variantes**.

### 3. Porquê F1 e não uma percentagem simples
Uma percentagem do tipo "quantos critérios desta ficha bateram" favorece fichas com poucos critérios. O motor calcula duas métricas e combina-as:

- **Precisão:** do peso total dos critérios da ficha, quanto bateu. Responde à pergunta: "o que a vítima apresenta é compatível com esta ficha?"
- **Cobertura:** das tags que o formando registou, quantas a ficha explica. Responde à pergunta: "esta ficha dá conta de tudo o que foi observado?"
- **F1:** a média harmónica das duas, `2 × P × C / (P + C)`. Só é alta quando as duas métricas são altas.

Exemplo real, o caso da captura de ecrã acima, com 7 tags: `dispneia`, `pieira`, `tiragem_musculos_acessorios`, `ansiedade`, `taquicardia`, `taquipneia`, `spo2_baixo`.

| Variante | Precisão | Cobertura | F1 |
|---|---|---|---|
| Asma — crise moderada | 83% | 100% | **91%** |
| Asma — crise grave | 53% | 86% | 65% |
| Asma — crise ligeira | 100% | 29% | 44% |

A crise ligeira bate 100% dos seus critérios, mas só explica 2 das 7 tags registadas. Com uma percentagem simples ficaria em primeiro lugar. Com F1, fica em terceiro.

### 4. Bónus das bandeiras vermelhas
Os critérios marcados como `bandeira_vermelha` (65 no total) têm o peso **multiplicado por 2** (`BONUS_BANDEIRA = 2`). Assim, um sinal de gravidade pesa mais na precisão do que um achado comum, e a sua ausência também penaliza mais.

### 5. Portões de contexto
As fichas da categoria **Trauma** só entram na disputa com mecanismo de trauma confirmado, e as de **Pediatria** só com vítima pediátrica. Sem estes portões, sinais genéricos de choque (taquicardia, palidez) punham, por exemplo, um hemotórax a competir com quadros puramente clínicos.

### 6. Limiar de diferenciação
Depois de ordenar por F1, o motor descarta as variantes com menos de 2 critérios batidos ou F1 abaixo de 25%, e fica com as 4 melhores. Se alguma estiver a **menos de 12 pontos percentuais** do 1.º lugar (`LIMIAR_DIFERENCIACAO_PONTOS = 12`), nenhuma é destacada: o resultado mostra o grupo empatado e sugere investigar mais achados antes de decidir a conduta.

### 7. Sinais vitais em vítimas pediátricas
Abaixo dos 18 anos (216 meses), a FC, a FR e a PAS são avaliadas com os **limites de alerta do INEM** para o grupo etário da vítima. Estes limites estão guardados no bloco `limites_alerta_inem` de [`parametros_vitais.json`](parametros_vitais.json) e são usados só pelo motor.

| Grupo (INEM) | Idade | FC normal | FR máx. | PAS mínima | Hipoglicemia |
|---|---|---|---|---|---|
| Recém-nascido | < 1 mês | 100–180 | 60 | 60 | < 40 |
| 1-12 meses | 1–11 meses | 80–180 | 40 | 70 | < 60 |
| 1-5 anos | 12–71 meses | 70–140 | 40 | 70 + 2 × anos completos | < 60 |
| 6-10 anos | 72–131 meses | 60–120 | 30 | 70 + 2 × anos completos | < 60 |
| > 10 anos | 132–215 meses | 60–100 | 18 | 90 | < 60 |

- **Taquicardia** com FC > máximo, **bradicardia** com FC < mínimo, **taquipneia** com FR > máximo, **hipotensão** com PAS < PAS mínima, **hipoglicemia** com glicemia abaixo do valor do grupo. O valor do próprio limite ainda é aceitável.
- **SpO2 ≤ 93, Glasgow ≤ 8, hiperglicemia (≥ 201), temperatura e apneia** usam as mesmas regras que nos adultos.
- **A PAD e a hipertensão sistólica não ativam tags** abaixo dos 18 anos.
- A partir dos 18 anos, ou sem idade indicada, aplicam-se as regras de adulto sem nenhuma alteração.

Exemplo: um bebé de 6 meses com FC 140, FR 30 e PAS 80 está dentro dos limites do grupo "1-12 meses" e não gera nenhuma tag. Com as regras de adulto gerava taquicardia, taquipneia e hipotensão.

**Decisões registadas:**
- **Fonte:** todos os limites pediátricos vêm do manual INEM "TAS – Emergências Pediátricas" (2024). A página de consulta dos Parâmetros Vitais mostra exatamente os mesmos valores.
- **Glicemia:** hipoglicemia < 40 mg/dL no recém-nascido (p. 51) e < 60 mg/dL nas outras idades pediátricas.
- **Peso estimado** (Quadro 1, p. 9): (meses + 9) / 2 dos 1 aos 11 meses, 2 × anos + 8 dos 1 aos 10 anos, 3 × anos acima dos 10 anos, sempre com os anos completos. No recém-nascido não se aplica: usa-se o peso ao nascer, se conhecido. A PAS normal (Quadro 4) segue a mesma lógica: 90 + 2 × anos completos dos 1 aos 10 anos.
- **Febre:** além do limite ≥ 38 °C, a consulta mostra a nota da p. 40: retal/timpânica ≥ 38 °C; axilar/oral ≥ 37,6 °C.
- **Recém-nascido:** usa-se 60, o valor mais alto do intervalo 50-60 indicado pelo INEM.
- **Dos 1 aos 10 anos:** a PAS mínima é calculada com os anos completos (por exemplo, 4 anos e 11 meses → 78).
- **SpO2:** mantém-se ≤ 93 nas crianças, por ser a regra mais sensível.
- **FR mínima:** fica guardada (`fr_min`), mas só será usada quando existir a tag `bradipneia`.

## Arquitetura e tecnologias

- **HTML, CSS e JavaScript puros**, sem frameworks, sem dependências e sem passo de build.
- **Dados em JSON:** taxonomia, critérios, atuações, casos, parâmetros vitais e avaliação ABCDE.
- **Código partilhado entre páginas:** o motor (`motor.js`), os componentes de interface (`ui.js`), os estilos (`simulador.css`) e os dados (`dados.js`) existem uma só vez e são usados pelo Caso Treino e pela Avaliação ABCDE.
- **Python 3** (só a biblioteca padrão) para o motor de pontuação e os testes automatizados. O teste de paridade com o motor JavaScript usa também o **Node.js**.
- **GitHub Pages** para a publicação.

```
simulador-triagem/
├── index.html               # Caso Treino
├── abcde.html               # Avaliação ABCDE
├── parametros_vitais.html   # Consulta dos parâmetros vitais por idade (mesma fonte que o motor)
├── motor.js                 # Motor de pontuação em JS (partilhado)
├── ui.js                    # Componentes de interface partilhados (sinais vitais, chips, resultado)
├── dados.js                 # Gerado a partir dos JSON (não editar à mão)
├── estilo.css               # Estilos base de todas as páginas
├── simulador.css            # Estilos partilhados pelo Caso Treino e pela Avaliação ABCDE
├── taxonomia.json           # Tags: 107 sinais/sintomas + 14 regras de sinais vitais
├── criterios.json           # 47 fichas com critérios, pesos e bandeiras vermelhas
├── atuacoes.json            # Atuação recomendada para cada uma das 47 fichas
├── casos_ficticios.json     # 5 casos de treino com cenário e gabarito
├── parametros_vitais.json   # Limites de referência pediátricos (INEM), usados pelo motor e pela consulta
├── abcde.json               # Letras A–E: achados, tags, sinais vitais, ações e objetivos
├── motor_pontuacao.py       # Motor de pontuação em Python + 4 cenários de exemplo
├── demo_score_teste.py      # Versão inicial do motor, com a amostra de teste
├── taxonomia_teste.json     # Amostra inicial (4 fichas) usada pelo demo
├── criterios_teste.json     #   "
├── ferramentas/             # gerar_dados_js.py: gera o dados.js a partir dos JSON
├── tests/                   # Testes automatizados (motor, dados, ABCDE, paridade Python ↔ JS)
├── docs/screenshots/        # Capturas de ecrã deste README
├── wireframe/               # Protótipos de design (não usados pela aplicação)
└── LICENSE                  # Licença MIT
```

As páginas carregam os dados com `<script src="dados.js">`. O `dados.js` é gerado a partir dos ficheiros JSON, que continuam a ser a fonte (e que o motor em Python lê diretamente).

### Atualizar os dados

Depois de editar qualquer ficheiro JSON, gera de novo o `dados.js` e faz commit dele juntamente com o JSON (o GitHub Pages não corre scripts):

```bash
python3 ferramentas/gerar_dados_js.py
```

Se te esqueceres, o `test_dados.py` falha e indica o comando.

## Como executar localmente

```bash
git clone https://github.com/rolimjeferson26-cyber/simulador-triagem.git
cd simulador-triagem
python3 -m http.server 8000
```

Depois abre <http://localhost:8000> no browser.

**Abrir os ficheiros diretamente (`file://`):** todas as páginas funcionam também com duplo clique, porque carregam os dados com `<script src>` e não com `fetch`. Ainda assim, usar o servidor local reproduz melhor o GitHub Pages.

Para correr os cenários de exemplo do motor em Python:

```bash
python3 motor_pontuacao.py
```

## Testes

Os testes estão na pasta [`tests/`](tests) e não precisam de instalar nada (usam só a biblioteca padrão do Python):

```bash
python3 tests/correr_testes.py
```

- **`test_motor.py`** verifica:
  - os limites pediátricos de cada grupo e as fronteiras entre grupos (11 vs 12 meses, 5a 11m vs 6 anos, 10a 11m vs 11 anos, 17a 11m vs 18 anos);
  - a fórmula da PAS mínima;
  - que os resultados de adulto são **exatamente iguais** aos de antes desta alteração. A comparação é feita com uma fotografia guardada em `tests/baseline_adulto.json`: os 5 casos incluídos em todos os contextos, mais 300 cenários aleatórios.
- **`test_dados.py`** confirma que o `dados.js` está atualizado em relação aos ficheiros JSON e que as páginas usam os ficheiros partilhados, sem cópias embutidas.
- **`test_abcde.py`** confirma que todos os achados do `abcde.json` apontam para tags que existem na taxonomia, que cada tag e cada sinal vital pertence a uma só letra, e que os 5 casos, avaliados com ABCDE + história, dão o mesmo ranking que no Caso Treino.
- **`test_pesquisa.py`** corre a pesquisa real do `ui.js` no Node.js: acentos e maiúsculas, sinónimos, mínimo de 2 letras, tags já marcadas excluídas e sinónimos sem ambiguidade.
- **`test_consulta.py`** confirma, para várias idades e para as fronteiras entre grupos, que os valores mostrados na consulta dos Parâmetros Vitais são exatamente os limites a que o motor reage (por exemplo, FC no máximo do grupo → sem tag; máximo + 1 → taquicardia). Verifica também a PAS e o peso (4 anos → PAS mínima 78, PAS normal 98, peso estimado 16 kg).
- **`test_paridade.py`** carrega o `dados.js` e o `motor.js` no Node.js, tal como as páginas os usam, e compara tags e ranking com o motor Python em 2 270 cenários, e compara mês a mês os valores de referência que a consulta mostra. Sem Node.js, este teste é ignorado e aparece como `IGNORADO`.
- **`test_seguranca.py`** corre no Node.js o `esc()` e o `validarCasosImportados` do `ui.js` com casos maliciosos (HTML no título e na nota, fichas inexistentes, campos estranhos) e confirma que nada chega à página como HTML e que os 5 casos incluídos passam sem alterações. Verifica também que a CSP de cada página está atualizada.

Os testes são funções com `assert`, por isso também correm com o pytest (`pip install pytest`, depois `pytest tests`).

## Segurança e privacidade

- **Content-Security-Policy:** cada página tem uma CSP numa etiqueta `<meta>` (o GitHub Pages não permite cabeçalhos HTTP). Só correm scripts do próprio site e os scripts embutidos autorizados pelo seu hash SHA-256. **Se editar um `<script>` dentro de um `.html`, corra `python3 ferramentas/atualizar_csp.py`**; o teste `tests/test_seguranca.py` falha se a CSP ficar desatualizada.
- **Casos importados são tratados como não confiáveis:** `validarCasosImportados` (em `ui.js`) reconstrói cada caso só com os campos conhecidos, nos tipos certos e com tamanho máximo, e rejeita casos com fichas inexistentes. Todo o texto vindo de casos passa por `esc()` antes de entrar em `innerHTML`.
- **Privacidade:** sem contas, cookies nem estatísticas. Os casos criados e o modo escolhido ficam só no `localStorage` do dispositivo. Ver [`privacidade.html`](privacidade.html).

## Dados e fontes

- As fichas, critérios e atuações foram anotados a partir das fichas de consulta do projeto [Guia de Emergências](https://github.com/rolimjeferson26-cyber/guia-emergencias). O campo `fonte` desse projeto descreve-as como *"compiladas a partir de conhecimento clínico geral (…) amplamente reconhecido na literatura de emergência médica"*, e não como reprodução de nenhum manual ou entidade formadora.
- Os **pesos (1–3) e as bandeiras vermelhas** foram atribuídos por julgamento clínico durante a anotação, e não por cálculo estatístico. O próprio `taxonomia.json` regista isto no campo `limitacoes`.
- A **página de consulta dos Parâmetros Vitais** mostra os mesmos limites que o motor usa, calculados pela mesma função.
- Os **limites de referência pediátricos** (motor e consulta) vêm do manual INEM, "TAS – Emergências Pediátricas", versão 1.0, março de 2024, capítulo II "Abordagem e Avaliação da Vítima Pediátrica" (Quadro 1, p. 9; Quadro 4, p. 10; Quadro 7, p. 18; Quadros 8 e 9, p. 20; temperatura, p. 40; glicemia, p. 51).
- Os achados e as ações da **Avaliação ABCDE** (`abcde.json`) foram escritos por palavras próprias, a partir da abordagem ABCDE usada na formação em emergência pré-hospitalar.
- Todo o conteúdo está em ficheiros JSON separados do código, o que permite revê-lo ou corrigi-lo sem mexer na lógica.
- Projeto independente, sem afiliação a qualquer instituição oficial.

## Limitações conhecidas

- **Uma FR baixa para a idade não é detetada:** ainda não existe a tag `bradipneia`.
- **O modo instrutor não é uma proteção real.** A verificação do código de acesso é feita no browser, e a escolha de modo fica guardada no `localStorage`. Serve para separar as vistas de formando e de formador em aula, mas não controla acessos.
- **Os casos criados pelo formador ficam só no browser onde foram criados** (`localStorage`). Para os passar para outro computador é preciso exportá-los e importá-los em JSON. Limpar os dados do browser apaga-os.
- **Os pesos dos critérios não foram validados estatisticamente**, como descrito em *Dados e fontes*.
- **Na Avaliação ABCDE, 14 achados não têm tag na taxonomia** (por exemplo, tempo de preenchimento capilar aumentado, pulso fraco, pele fria, pupilas anisocóricas ou não reativas, enfisema subcutâneo). Ficam registados no resumo e obrigam a fazer as ações da letra, mas não entram no motor.
- **Na Avaliação ABCDE, o gabarito do caso aparece a todos no fim**, como correção da avaliação. No Caso Treino, só aparece no modo instrutor.
- **Os testes cobrem o motor e os dados, mas não a interface** (formulário, cliques, editor de casos), e ainda não correm automaticamente a cada push.
- **Há apenas 5 casos incluídos.** O resto do treino depende de casos criados pelo formador ou do caso livre.

## Próximos passos

Por ordem de prioridade, a partir das limitações acima:

1. **Tag `bradipneia`**, para o motor detetar uma frequência respiratória abaixo do normal para a idade, usando o `fr_min` já guardado.
2. **Criar tags e critérios para os achados ABCDE sem tag** (prioridade: TPC aumentado, pulso fraco, pele fria, pupilas anisocóricas/não reativas, enfisema subcutâneo).
3. **Unificar as tags duplicadas de rash petequial** (`rash_petequial` e `rash_hemorragico`).
4. **Mais casos de treino**, incluindo casos pediátricos com idade, de várias categorias e níveis de dificuldade.

## Projeto relacionado

**[Guia de Emergências](https://rolimjeferson26-cyber.github.io/guia-emergencias)**: guia de consulta rápida com 68 fichas de emergências médicas e de trauma, e anatomia interativa dos 11 sistemas do corpo humano. As fichas do simulador foram anotadas a partir dele. ([repositório](https://github.com/rolimjeferson26-cyber/guia-emergencias))

## Autor

**Jeferson Rolim**, Bombeiro EIP
- GitHub: [@rolimjeferson26-cyber](https://github.com/rolimjeferson26-cyber)
- LinkedIn: [Jeferson Rolim](https://www.linkedin.com/in/jeferson-rolim-023348437)

## Licença

O código deste projeto está disponível sob a [licença MIT](LICENSE).

A licença cobre o código. Os conteúdos clínicos (fichas, critérios, atuações, casos, avaliação ABCDE e valores de referência) são material educativo e não substituem os protocolos oficiais em vigor nem a formação certificada.
