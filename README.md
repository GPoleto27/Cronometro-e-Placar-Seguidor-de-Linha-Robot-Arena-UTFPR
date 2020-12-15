# Cronometro e placar - Seguidor de Linha - Robot Arena - UTFPR
Protótipo (desenvolvido em uma semana) em Python usando PyGObject para interface gráfica para cronômetro e placar para a competição Robot Arena (UTFPR - Toledo) para a categoria seguidor de linha.

# O sensor
É utilizado um sensor LDR numa extremidade de um arco no qual o seguidor deve passar por baixo iluminado por um led na outra extremidade do arco.
Quando o robô passa através do sensor é acionada uma interrupção no Arduino que manda um Byte via serial que é lido pelo programa, responsável pela manipulação dos tempos e do placar

# O programa
O programa é responsável pela contagem do tempo das três voltas permitidas para cada robô bem como o gerenciamento do placar.

# To-Do
<ul>
  <li>Necessário reestruturar o código</li>
  <li>Utilizar algum SGBD para manipular os dados</li>
  <li>Utilizar algum ORM para melhor manipulação</li>
  <li>Limpeza e otimização do código</li>
  <li>Documentação do uso e funcionamento do programa</li>
</ul>
