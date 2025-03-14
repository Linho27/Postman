# Carrinho Inteligente para Leitura de Códigos e ligação com MTS

Este projeto tem como objetivo o desenvolvimento de um carrinho inteligente capaz de realizar as seguintes tarefas:

	• Leitura de Códigos em Placas: O carrinho é equipado com um sistema para ler códigos fornecidos em placas, identificando informações chave.
 
	• Integração com o MTS da Empresa: Após a leitura do código, o carrinho entra em contato com o MTS da empresa para obter o local exato do item relacionado ao código lido.
 
	• Orientação ao Usuário: O carrinho indica ao usuário o local onde a placa deve ser colocada, proporcionando uma experiência eficiente e sem complicações.

Funcionalidades

	• Leitura de códigos QR ou códigos de barras em placas.
 
	• Comunicação com o MTS para verificar e obter dados de localização.
 
	• Interface amigável para direcionar o usuário sobre onde colocar a placa de forma otimizada.
 
Tecnologias Utilizadas

	• Raspberry Pi
 
	• Python para a lógica de controle e comunicação com o MTS
 
	• GPIO para controlo do hardware
 
	• API de Integração com MTS para consultar informações de localização.
 
Como Funciona

	1. O código é lido através de uma camera.
 
	2. O sistema faz uma solicitação ao MTS para localizar a informação correspondente ao código.
 
	3. O carrinho indica o local exato onde o usuário deve colocar a placa.
 
