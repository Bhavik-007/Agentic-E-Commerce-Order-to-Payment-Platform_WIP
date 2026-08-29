/*
  Run from an elevated Windows-authenticated SQL Server session:
  sqlcmd -E -S localhost -C -i database/create_database.sql

  For a named instance replace localhost, for example:
  sqlcmd -E -S localhost\MSSQLSERVER01 -C -i database/create_database.sql
*/
IF DB_ID(N'ShopPilotAI') IS NULL
BEGIN
    CREATE DATABASE ShopPilotAI;
END
GO

USE ShopPilotAI;
GO

/* Map the signed-in Windows login to this development database. */
DECLARE @login_name sysname = SUSER_SNAME();
DECLARE @sql nvarchar(max);

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE sid = SUSER_SID())
BEGIN
    SET @sql = N'CREATE USER ' + QUOTENAME(@login_name) + N' FOR LOGIN ' + QUOTENAME(@login_name) + N';';
    EXEC sys.sp_executesql @sql;
END

IF IS_ROLEMEMBER(N'db_owner', @login_name) <> 1
BEGIN
    SET @sql = N'ALTER ROLE db_owner ADD MEMBER ' + QUOTENAME(@login_name) + N';';
    EXEC sys.sp_executesql @sql;
END
GO
