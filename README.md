Query Analyzer and Java Bean Generator

Developed a SQL query analysis tool in Python that parses and tokenizes raw SQL queries to extract and structurally represent key clauses such as SELECT, FROM, JOIN, WHERE, GROUP BY, and ORDER BY.
Retrieved table metadata using MySQL’s INFORMATION_SCHEMA via Python's MySQL Connector library for accurate query validation.

Key components include:

1) Custom SQL Tokenizer and Parser: Breaks down raw SQL into meaningful segments.
2) Dynamic Schema Mapping: Retrieves live table structures and identifies column-table relationships, including join conditions and alias resolution.
3) Object-Oriented Schema Representation: Implements core classes (Table, Column, Field, etc.) to model relational metadata in-memory.
J4) ava Bean Class Generator: Automatically generates Java Bean classes (POJOs) for the fields selected in a query, including proper data types, getters, and setters based on SQL column types.
