# Arquitetura-Cliente-Middleware-Servidor-Uma-Abordagem-Prática-em-Python

# COMANDOS
*- Execução de soma:* --op soma --a NUMERO --b NUMERO

*- Middleware rejeitando requisição com chave inválida:* --op invalida --a NUMERO --b NUMERO
 Obs.: "invalida" pode ser qualquer termo além de: soma, subtracao, multiplicacao, divisao e fib.

*- Teste de concorrência com 5 requisições em paralelo (multiplicação):* --op multiplicacao --a NUMERO --b NUMERO --paralelo QUANTIDADE ESCOLHIDA

*- Teste de paralelismo com fibonacci (n=30) rodando em múltiplos processos:* --op fib --n 30 --paralelo QUANTIDADE ESCOLHIDA
