drop table if exists user;

create table user (
    id integer primary key autoincrement,
    username text unique not null,
    password text not null
);