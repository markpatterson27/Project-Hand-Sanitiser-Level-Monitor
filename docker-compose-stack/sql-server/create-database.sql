/*
Enter custom T-SQL here that would run after SQL Server has started up. 
*/

/** create database **/
USE master
GO

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'HandSanitiserLevels')
BEGIN
  CREATE DATABASE HandSanitiserLevels;
END;
GO

/** create sensor readings table **/
USE [HandSanitiserLevels]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = N'SensorReadings')
BEGIN
    CREATE TABLE [dbo].[SensorReadings](
        [Id] [int] IDENTITY(1,1) NOT NULL,
        [Datetime] [datetime2](7) NOT NULL,
        [Device] [nvarchar](50) NOT NULL,
        [Location] [nvarchar](50) NULL,
        [Method] [nvarchar](50) NULL,
        [CapacitanceFullLength] [decimal](4, 0) NULL,
        [CapacitanceTop] [decimal](4, 0) NULL,
        [CapacitianceBottom] [decimal](4, 0) NULL,
        [CapacitanceCallibrated] [float] NULL,
        [BatteryLevel] [float] NULL,
        CONSTRAINT [PK_Sensor-Readings] PRIMARY KEY CLUSTERED 
        (
            [Id] ASC
        )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
    ) ON [PRIMARY]
END
GO