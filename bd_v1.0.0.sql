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

-- Volcando estructura para tabla software_innova.users
CREATE TABLE IF NOT EXISTS `users` (
  `USER_ID` int(2) NOT NULL AUTO_INCREMENT,
  `USER_NAME` varchar(30) NOT NULL,
  `USER_LAST_NAME` varchar(30) NOT NULL,
  `USER_EMAIL` varchar(30) NOT NULL,
  `USER_PASSWORD` varchar(12) NOT NULL,
  `USER_ROL` int(1) NOT NULL,
  PRIMARY KEY (`USER_ID`),
  KEY `FK_users_users_rol` (`USER_ROL`),
  CONSTRAINT `FK_users_users_rol` FOREIGN KEY (`USER_ROL`) REFERENCES `users_rol` (`ID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla software_innova.users: ~2 rows (aproximadamente)
INSERT IGNORE INTO `users` (`USER_ID`, `USER_NAME`, `USER_LAST_NAME`, `USER_EMAIL`, `USER_PASSWORD`, `USER_ROL`) VALUES
	(1, 'administrador', 'pruebas', 'admin@example.com', 'admin1234567', 1),
	(3, 'usuario', 'pruebas', 'usuario@example.com', 'usuario12345', 2);

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
