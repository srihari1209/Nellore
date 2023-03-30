DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id int( 11 ) NOT NULL AUTO_INCREMENT ,
    email varchar(50)  NOT NULL,
    password varchar(128) NOT NULL,
    name varchar(30),
	PRIMARY KEY (id),
	UNIQUE KEY name (name)
);


INSERT INTO users (email,password,name) VALUES("ch.srihari1209@gmail.com","Master@mar2022","Master");