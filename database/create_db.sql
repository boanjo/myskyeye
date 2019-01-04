-- Serverversion: 10.3.9-MariaDB-1:10.3.9+maria~bionic
-- PHP-version: 7.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Databas: `myskyeye`
--
CREATE DATABASE IF NOT EXISTS `myskyeye` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `myskyeye`;

-- --------------------------------------------------------

--
-- Tabellstruktur `metadata`
--

CREATE TABLE `metadata` (
  `id` int(11) NOT NULL,
  `file_name` tinytext NOT NULL,
  `file_tb_name` tinytext NOT NULL,
  `weight` tinytext NOT NULL
) ENGINE=Aria DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Tabellstruktur `motion`
--

CREATE TABLE `motion` (
  `id` int(11) NOT NULL,
  `date` tinytext NOT NULL,
  `time` tinytext NOT NULL,
  `duration` double NOT NULL,
  `frame_count` int(11) NOT NULL,
  `motion_count` int(11) NOT NULL,
  `path` tinytext NOT NULL,
  `file_name` tinytext NOT NULL,
  `objects` tinytext NOT NULL
) ENGINE=Aria DEFAULT CHARSET=latin1;

