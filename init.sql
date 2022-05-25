CREATE DATABASE [IF NOT EXISTS] KitabGhar;
USE KitabGhar;

CREATE TABLE `KitabGhar`.`Author` ( 
  `ID` INT NOT NULL AUTO_INCREMENT , 
  `FName` VARCHAR(15) NOT NULL , 
  `LName` VARCHAR(15) NULL , 
  PRIMARY KEY (`ID`), 
  UNIQUE `Name` (`FName`, `LName`));

CREATE TABLE `KitabGhar`.`Course` ( `ID` CHAR(5) NOT NULL , `Name` VARCHAR(100) NOT NULL , `Dept` VARCHAR(4) NULL );

CREATE TABLE `KitabGhar`.`Books` ( 
  `ID` INT NOT NULL AUTO_INCREMENT , 
  `Title` VARCHAR(30) NOT NULL , 
  `Edition` INT NULL , 
  `ShelfNo` INT NOT NULL , 
  `Row` INT NOT NULL , 
  `Section` CHAR(1) NOT NULL , 
  `Stock` INT NULL , 
  `CourseID` CHAR(5) NULL , 
  `Total` INT NOT NULL DEFAULT '0' , 
  PRIMARY KEY (`ID`), 
  UNIQUE `book` (`Title`, `Edition`), 
  UNIQUE `position` (`ShelfNo`, `Row`, `Section`));
ALTER TABLE `ok` ADD CONSTRAINT `BookCourse` FOREIGN KEY (`CourseID`) REFERENCES `Course`(`ID`) ON DELETE SET NULL ON UPDATE CASCADE;

CREATE TABLE `KitabGhar`.`Author_Books` ( 
  `AuthorID` INT NOT NULL , 
  `BookID` INT NOT NULL , 
  UNIQUE `entry` (`AuthorID`, `BookID`));
ALTER TABLE `Author_Books` ADD CONSTRAINT `Author` FOREIGN KEY (`AuthorID`) REFERENCES `Author`(`ID`) ON DELETE CASCADE ON UPDATE CASCADE; 
ALTER TABLE `Author_Books` ADD CONSTRAINT `Book` FOREIGN KEY (`BookID`) REFERENCES `Books`(`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE `KitabGhar`.`Member` ( 
  `ID` INT NOT NULL AUTO_INCREMENT , 
  `FName` VARCHAR(15) NOT NULL , 
  `LName` VARCHAR(15) NULL , 
  `Phone` CHAR(10) NULL , 
  `Email` VARCHAR(30) NOT NULL , 
  `Username` VARCHAR(10) NOT NULL , 
  `Password` VARBINARY(128) NOT NULL , 
  PRIMARY KEY (`ID`), 
  UNIQUE `username` (`Username`), 
  UNIQUE `name` (`FName`, `LName`), 
  UNIQUE `contact` (`Phone`, `Email`));

CREATE TABLE `KitabGhar`.`Staff` ( 
  `ID` INT NOT NULL AUTO_INCREMENT , 
  `FName` VARCHAR(15) NOT NULL , 
  `LName` VARCHAR(15) NULL , 
  `Phone` CHAR(10) NULL , 
  `Email` VARCHAR(30) NOT NULL , 
  `Username` VARCHAR(10) NOT NULL , 
  `Password` VARBINARY(128) NOT NULL , 
  PRIMARY KEY (`ID`), 
  UNIQUE `username` (`Username`), 
  UNIQUE `name` (`FName`, `LName`), 
  UNIQUE `contact` (`Phone`, `Email`));

CREATE TABLE `KitabGhar`.`Student` ( `MemID` INT NOT NULL , `RollNo` CHAR(6) NOT NULL );
ALTER TABLE `Student` ADD CONSTRAINT `f1_stud` FOREIGN KEY (`MemID`) REFERENCES `Member`(`ID`) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE `KitabGhar`. ( 
  `ID` INT NOT NULL AUTO_INCREMENT , 
  `IssueDate` DATE NOT NULL , 
  `ReturnDate` DATE NULL , 
  `Paid` TINYINT(1) NOT NULL DEFAULT '0' , 
  `BookID` INT NOT NULL , 
  `MemberID` INT NOT NULL , 
  PRIMARY KEY (`ID`));
ALTER TABLE `Borrow_log` ADD CONSTRAINT `f1` FOREIGN KEY (`BookID`) REFERENCES `Books`(`ID`) ON DELETE RESTRICT ON UPDATE CASCADE; 
ALTER TABLE `Borrow_log` ADD CONSTRAINT `f2` FOREIGN KEY (`MemberID`) REFERENCES `Member`(`ID`) ON DELETE CASCADE ON UPDATE CASCADE;
