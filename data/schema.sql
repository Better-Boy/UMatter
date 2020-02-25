create database umatter;
use umatter;
create table transaction(channel_id varchar(100) not null, channel_name varchar(100) not null, from_user_id varchar(100) not null, from_user_name varchar(100) not null, points integer, to_user_id varchar(100), to_user_name varchar(100), post_id varchar(100), timestamp TIMESTAMP);