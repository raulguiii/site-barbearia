CREATE DATABASE bd_barbearia;

USE bd_barbearia;

CREATE TABLE usuarios ( 
id INT AUTO_INCREMENT PRIMARY KEY, 
nome VARCHAR(255) NOT NULL, 
senha VARCHAR(255) NOT NULL,
chave_pix VARCHAR(255),
pagamento_realizado BOOLEAN DEFAULT 0, 
comprovante VARCHAR(255),
tempo_de_casa INT,
horario_trabalho VARCHAR(255),
cargo VARCHAR(50) NOT NULL DEFAULT 'Barbeiro');

SELECT * FROM usuarios;





CREATE TABLE agendamentos ( 
id INT AUTO_INCREMENT PRIMARY KEY, 
nome VARCHAR(255) NOT NULL, 
telefone VARCHAR(11) NOT NULL, 
servico VARCHAR(255) NOT NULL,
data1 DATE NOT NULL, 
candidato TINYINT DEFAULT 0,
barbeiro_nome VARCHAR(255) DEFAULT NULL,
horario TIME NOT NULL,
salario DECIMAL(10, 2) );

SELECT * FROM agendamentos;



CREATE TABLE financeiro ( id INT AUTO_INCREMENT PRIMARY KEY, 
nome_funcionario VARCHAR(100) NOT NULL, 
horario_trabalho VARCHAR(50) NOT NULL, 
salario DECIMAL(10, 2) NOT NULL, 
status_pagamento VARCHAR(20) DEFAULT 'Pendente' );

SELECT * FROM financeiro;




CREATE TABLE produtos ( 
id INT AUTO_INCREMENT PRIMARY KEY, 
nome VARCHAR(255) NOT NULL, 
quantidade INT NOT NULL, 
preco DECIMAL(10,2) NOT NULL );

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
