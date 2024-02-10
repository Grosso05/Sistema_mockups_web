-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         10.4.32-MariaDB - mariadb.org binary distribution
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para software_innova
CREATE DATABASE IF NOT EXISTS `software_innova` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `software_innova`;

-- Volcando estructura para tabla software_innova.customers
CREATE TABLE IF NOT EXISTS `customers` (
  `CUSTOMER_ID` int(2) NOT NULL AUTO_INCREMENT,
  `CUSTOMER_NAME` varchar(50) DEFAULT NULL,
  `CUSTOMER_LAST_NAME` varchar(50) DEFAULT NULL,
  `CUSTOMER_EMAIL` varchar(80) NOT NULL,
  `CUSTOMER_PHONE` varchar(15) DEFAULT NULL,
  `CUSTOMER_DATE` date NOT NULL,
  `USER` int(2) DEFAULT NULL,
  PRIMARY KEY (`CUSTOMER_ID`),
  KEY `FK_customers_users` (`USER`),
  CONSTRAINT `FK_customers_users` FOREIGN KEY (`USER`) REFERENCES `users` (`USER_ID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla software_innova.customers: ~8 rows (aproximadamente)
INSERT IGNORE INTO `customers` (`CUSTOMER_ID`, `CUSTOMER_NAME`, `CUSTOMER_LAST_NAME`, `CUSTOMER_EMAIL`, `CUSTOMER_PHONE`, `CUSTOMER_DATE`, `USER`) VALUES
	(2, NULL, NULL, 'pruebainput@h.coom', NULL, '2024-02-09', NULL),
	(3, NULL, NULL, 'pruebarandom@gmail.com', NULL, '2024-02-09', 110),
	(4, NULL, NULL, 'pruebarandom2@gmail.com', NULL, '2024-02-09', 3),
	(5, NULL, NULL, 'pruebarandom3@gmail.com', NULL, '2024-02-09', 3),
	(6, NULL, NULL, 'pruebaobligatoria@example.com.co', NULL, '2024-02-09', 110),
	(7, NULL, NULL, 'pruebaasignacion@example.com', NULL, '2024-02-10', 110),
	(8, NULL, NULL, 'pruebaasignacion@example.com', NULL, '2024-02-10', 110),
	(9, NULL, NULL, 'pruebaasignacion2@example.com', NULL, '2024-02-10', 3);

-- Volcando estructura para tabla software_innova.users
CREATE TABLE IF NOT EXISTS `users` (
  `USER_ID` int(2) NOT NULL AUTO_INCREMENT,
  `USER_NAME` varchar(30) NOT NULL,
  `USER_LAST_NAME` varchar(30) NOT NULL,
  `USER_EMAIL` varchar(30) NOT NULL,
  `USER_PASSWORD` varchar(12) NOT NULL,
  `USER_ROL` int(1) NOT NULL,
  `session_token` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`USER_ID`),
  KEY `FK_users_users_rol` (`USER_ROL`),
  CONSTRAINT `FK_users_users_rol` FOREIGN KEY (`USER_ROL`) REFERENCES `users_rol` (`ID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=111 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla software_innova.users: ~5 rows (aproximadamente)
INSERT IGNORE INTO `users` (`USER_ID`, `USER_NAME`, `USER_LAST_NAME`, `USER_EMAIL`, `USER_PASSWORD`, `USER_ROL`, `session_token`) VALUES
	(1, 'administrador', 'pruebas', 'admin@example.com', 'admin1234567', 1, NULL),
	(3, 'usuario', 'pruebas', 'usuario@example.com', 'usuario12345', 2, NULL),
	(107, 'Brayan', 'Grosso', 'brayan@example.com', 'brayan123', 1, NULL),
	(108, 'vendedor', 'uno', 'vendedor1@example.com', 'vendedor123', 2, NULL),
	(110, 'vendedor2', 'dos', 'vendedor2@example.com', 'vendedor123', 2, NULL);

-- Volcando estructura para tabla software_innova.users_rol
CREATE TABLE IF NOT EXISTS `users_rol` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DESCRIPCION` varchar(20) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla software_innova.users_rol: ~2 rows (aproximadamente)
INSERT IGNORE INTO `users_rol` (`ID`, `DESCRIPCION`) VALUES
	(1, 'ADMINISTRADOR'),
	(2, 'USUARIO');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
