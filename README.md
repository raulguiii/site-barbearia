<h1>Trabalho de Software Product da Faculdade Impacta.</h1>

<p>Projeto de uma barbearia com diversas funcionalidades. Integrantes: Raul Guilherme Silva Rodrigues, Enzo Lacerda Costa, Rodrigo Coutrufo Silva</p>


https://trello.com/b/J6BtshPV/projeto-da-barbearia


<h2>MySQl Workbench:</h2>

CREATE DATABASE bd_barbearia;

USE bd_barbearia;

CREATE TABLE usuarios ( id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255) NOT NULL, senha VARCHAR(255) NOT NULL );

SELECT * FROM usuarios;

CREATE TABLE agendamentos ( id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255) NOT NULL, telefone VARCHAR(11) NOT NULL, servico VARCHAR(255) NOT NULL, data1 DATE NOT NULL, horario TIME NOT NULL );

SELECT * FROM agendamentos;

CREATE TABLE financeiro ( id INT AUTO_INCREMENT PRIMARY KEY, nome_funcionario VARCHAR(100) NOT NULL, horario_trabalho VARCHAR(50) NOT NULL, salario DECIMAL(10, 2) NOT NULL, status_pagamento VARCHAR(20) DEFAULT 'Pendente' );

SELECT * FROM financeiro;

ALTER TABLE agendamentos ADD COLUMN candidato TINYINT DEFAULT 0;

ALTER TABLE agendamentos ADD COLUMN barbeiro_nome VARCHAR(255) DEFAULT NULL;

ALTER TABLE usuarios ADD COLUMN salario DECIMAL(10, 2), ADD COLUMN tempo_de_casa INT, ADD COLUMN horario_trabalho VARCHAR(255);

ALTER TABLE usuarios ADD chave_pix VARCHAR(255);

ALTER TABLE usuarios ADD COLUMN pagamento_realizado BOOLEAN DEFAULT 0, ADD COLUMN comprovante VARCHAR(255);

CREATE TABLE produtos ( id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255) NOT NULL, quantidade INT NOT NULL, preco DECIMAL(10,2) NOT NULL );

SELECT * FROM produtos;

CREATE TABLE vendas_produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    endereco VARCHAR(255) NOT NULL,
    metodo_entrega ENUM('retirada', 'entrega') NOT NULL,
    produto ENUM('gel', 'pomada', 'shampoo', 'condicionador', 'escova') NOT NULL,
    data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM vendas_produtos;

