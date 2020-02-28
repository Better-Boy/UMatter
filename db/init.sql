DROP TABLE IF EXISTS `transaction`;
CREATE TABLE `transaction`(
  `channel_id` varchar(100) NOT NULL,
  `channel_name` varchar(100) NOT NULL,
  `from_user_id` varchar(100) NOT NULL,
  `from_user_name` varchar(100) NOT NULL,
  `points` int DEFAULT NULL,
  `to_user_id` varchar(100) DEFAULT NULL,
  `to_user_name` varchar(100) DEFAULT NULL,
  `post_id` varchar(100) DEFAULT NULL,
  `insertionTime` timestamp NULL DEFAULT NULL,
  `message` varchar(100) DEFAULT NULL
);