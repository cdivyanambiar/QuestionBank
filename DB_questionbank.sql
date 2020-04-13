create database questionbank;
show  databases;
use  questionbank;
create table  questions(ID int auto_increment primary key ,question varchar(2500),solution varchar(2000),includegraphics varchar(100)); 
create table choices(ID int auto_increment primary key,
questionID int ,
choice varchar(1000),isCorrectChoice boolean,
FOREIGN KEY (questionID)
        REFERENCES questions(id)
        ON DELETE CASCADE
);
delete from questions;

select *  from questions;
