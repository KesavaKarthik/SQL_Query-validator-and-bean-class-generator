import mysql.connector
class Column:
    def __init__(self, name,datatype,size,decimal,is_null,key):
        self.name = name
        self.datatype = datatype
        self.size = size
        self.decimal = decimal
        self.is_null = is_null
        self.key = key

class Query:
    def __init__(self,SELECT, FROM ,JOIN,WHERE,GROUP_BY,ORDER_BY):
        self.SELECT = SELECT
        self.FROM = FROM
        self.JOIN = JOIN
        self.WHERE = WHERE
        self.GROUP_BY = GROUP_BY
        self.ORDER_BY = ORDER_BY

class Query_Table:
    def __init__(self , table_name , alias , condition , columns):
        self.tableName = table_name
        self.alias = alias
        self.condition = condition
        self.columns = columns
        
class Table:
    def __init__(self,name):
        self.name = name
        self.columns = []
    
    def add_column(self,colm):
        self.columns.append(colm)
class Field:
    def __init__(self,name,alias,table_name,datatype,size,decimal,func):
        self.name = name
        self.alias = alias
        self.table_name = table_name
        self.datatype= datatype
        self.size = size
        self.decimal = decimal
        self.func = func
class Token:
    def __init__(self, val):
        self.val = val       

def tokenizer(file):
    word = ""
    tokens = []
    for ch in file:
        if( ch == ' '):
            if( word != ""): tokens.append(word)
            word = ""
        elif( ch == '\n' or ch == '(' or ch == ',' or ch == ')' or ch == '+' or ch == '=' or ch == '.'):
            if( word != "") :tokens.append(word)
            tokens.append(ch)
            word = ""
        else : word += ch
    if( word != ""): tokens.append(word)
    return tokens




def analyze_query(tokens):
    """
    Analyzes SQL tokens to identify components like SELECT, FROM, WHERE, etc.
    """
    query_structure = {
        "SELECT": [],
        "FROM": [],
        "JOIN": [],
        "WHERE": [],
        "GROUP BY": [],
        "ORDER BY": [],
    }

    current_section = None
    i = 0
    join = []
    while i < len(tokens):
        if(tokens[i] == "\n"):
            i += 1
            continue
        
        upper_token = tokens[i].upper()
        # Handle multi-word clauses
        if upper_token == "GROUP" and i + 1 < len(tokens) and tokens[i + 1].upper() == "BY":
            current_section = "GROUP BY"
            i += 1  # Skip the next token ('BY')
        elif upper_token == "ORDER" and i + 1 < len(tokens) and tokens[i + 1].upper() == "BY":
            current_section = "ORDER BY"
            i += 1  # Skip the next token ('BY')
        elif( upper_token == "JOIN"):
            current_section = upper_token
            if( join):
                query_structure["JOIN"].append(join)
            join = []

        elif upper_token in query_structure:
            current_section = upper_token
        elif current_section == "JOIN":
            join.append(tokens[i])
        elif current_section:
            query_structure[current_section].append(tokens[i])
        i += 1
    if( join):
        query_structure["JOIN"].append(join)

    query = Query( query_structure["SELECT"], query_structure["FROM"],query_structure["JOIN"],query_structure["WHERE"],query_structure["GROUP BY"],query_structure["ORDER BY"])

    return query


            
        
def names_of_tables():
    conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Shiva@2005',
    database='flight_booking_project'
    )

    cursor = conn.cursor()
    cursor.execute("""
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'flight_booking_project';
    """)

    tables = cursor.fetchall()
    table_names = []
    for (table_name,) in tables:
       table_names.append(table_name)

    conn.close()
    return table_names


def column_find(tables,query_tables , name):
    for table_name in query_tables:
        for column in tables[table_name].columns : 
            if( name == column.name): 
                return table_name
    
    return None

def column_details(table,cname):
    for col in table.columns:
        if( col.name == cname):
            return col.datatype,col.size,col.decimal
    
    return None

def table_description(table_name , columns):
    table = Table(table_name)

    for column in columns:
        column_name = column['COLUMN_NAME']
        data_type = column['DATA_TYPE']
        is_null = column['IS_NULLABLE']
        column_type = column['COLUMN_TYPE']
        size = 0
        decimal = 0
        key = "NO"
        for i in range(len(column_type)) :
            if( column_type[i] == '('):
                size = column_type[i + 1]
            elif( column_type[i] == ','):
                decimal = column_type[i + 1]
        colm = Column(column_name , data_type , size , decimal , is_null , key)
        table.add_column(colm)
    
    return table


def query_table( joins, From):
    alias = {}
    prev = ""
    names_table = names_of_tables()
    #print(names_table)
# dictionary of alais names and their corresponding table
    for word in From:
        if(word == ','): continue 
        elif(word in names_table): 
            alias[word] = word
        else: 
            alias[word] =  prev
        prev = word
    for join in joins :
        
        alias[join[0]] = join[0]
        if( len(join) > 1) : alias[join[1]] = join[0]

    #print( alias)
    

    return alias

def table_names( dict):
    names = []
    for name in dict.values():
        if name not in names :names.append( name)

    return names
def field_creation(select,is_function,field_name,columns , table_name, column_alais,table):

    if table_name == "multiple":
            select.append(Field(field_name,column_alais, table_name,"number","-",0 , is_function))
    elif(len(columns) > 1):
        select.append(Field(field_name,column_alais, table_name,"number","-",0 , is_function))
    else :
        
        if( is_function == 0) :datatype, size, decimal = column_details(table[table_name], field_name)
        else : datatype, size, decimal = column_details(table[table_name], columns[0])
        select.append(Field(field_name,column_alais, table_name, datatype, size, decimal, is_function))

def Join( joins , tables , query_tables):
    flag = 0
    table_name = ""
    alias = "none"
    condition = "none"
    columns = []
    tables_structure = []
    i = 0
    for tokens in joins:
        flag = 0
        table_name = "none"
        alias = "none"
        condition = ""
        columns = []
        i = 0
        while( i < len(tokens)):

            tokens[i].upper()
            #print(token)
            if tokens[i].upper() == "ON" :
                flag = 1
            elif flag == 0 and table_name == "none":
                table_name = tokens[i]
            elif flag == 0 :
                alias = tokens[i]
            elif flag == 1 :
                condition += tokens[i]
                if( i < len(tokens) - 2 and tokens[i + 1] == '.' ):
                    name = column_find( tables , query_tables , tokens[i + 2])
                    if( name != None ):columns.append(tokens[i + 2])
                    
                    condition += tokens[i + 1] + tokens[i + 2]
                    i += 2
            
                elif( len(tokens[i]) > 1 ):
                    name = column_find( tables , query_tables , tokens[i])

                    if( name != None ): columns.append( tokens[i])
                    
            i += 1
        

        tables_structure.append( Query_Table(table_name , alias , condition , columns))     

    return tables_structure



def Select(token,table ,alias , query_tables):
    select = []
    table_name = "NONE"
    field_name = "NONE"
    column_alias = "NONE"
    columns = []
    expression = ""
    is_function = 0
    f_open = 0
    tables = set()
    length = len(token)
    i = -1
    while(i < (len(token)) - 1) :
        i += 1
        if(token[i] == ',' and f_open == 0):
            if(len(tables) > 1):
                table_name = "multiple"
            if( len(columns) > 1 ):
                field_name = expression
            if( is_function == 1): field_name = expression

            field_creation(select,is_function,field_name,columns , table_name, column_alias,table)
            expression = ""
            is_function = 0
            columns = []
            tables = set()
            column_alias = "NONE"
            continue
    
    
        if( i < length - 1 and len(token[i]) > 1 and token[i + 1] == '('):
            is_function = 1
            f_open += 1
        elif( token[i] == ')'): f_open -= 1
    

        elif( i < length - 3 and len(token[i]) > 1 and token[i + 1] == '.'):
            table_name = alias[token[i]]
            field_name = token[i + 2]
            columnDetails = column_details(table[table_name] ,field_name)
            if( columnDetails == None) : print("error")
            tables.add(table_name)
            columns.append(field_name)
            expression += (token[i] + token[i + 1] + token[i + 2] )
            i += 2
            continue
    

        elif( token[i].upper() == "AS"):
            column_alias = token[i + 1]
            i += 1
            continue
            
        
        elif( len(token[i])> 1 ):
            field_name = token[i]
            table_name = column_find(table, query_tables , token[i])
            if( table_name == None): print("error")
            else:  tables.add(table_name)
            columns.append(token[i])
        
        expression += token[i]
        #print(expression)
        #print( i )
    
    if(len(tables) > 1):
            table_name = "multiple"
    if( len(columns) > 1 ):
        field_name = expression
    if( is_function == 1): field_name = expression
    field_creation(select,is_function,field_name,columns , table_name, column_alias,table)
    
    return select


def table_creation( table_names):
    tables = {}
    conn = mysql.connector.connect(
        host = 'localhost' ,
        user = 'root' ,
        password = 'Shiva@2005' ,
        database = 'flight_booking_project'
    )
    cursor = conn.cursor(dictionary = True)
    for name in table_names:
        cursor.execute(f"""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'flight_booking_project' AND TABLE_NAME = '{name}'
        """)
        #print( cursor.fetchall() )
        tables[name] = table_description(name , cursor.fetchall())

    conn.close()

    return tables


    
    
    





        
                

                
            



#file = open(r"C:\Users\kesav\OneDrive\Documents\dummyfile.txt")
#file = file.read()
#tokens = tokenizer(file)
#table = table_description(tokens)

#for i in range(0,len(table[name].columns)):
#    print(table[name].columns[i].name," ",table[name].columns[i].datatype," ",table[name].columns[i].size," ",table[name].columns[i].decimal," ",table[name].columns[i].is_null," ",table[name].columns[i].key)
#print()

file = open(r"C:\Users\kesav\OneDrive\Documents\query.txt")
file = file.read()
tokens = tokenizer(file)
#print(tokens)
qr = analyze_query(tokens)

#print( qr.JOIN)
#print( qr.FROM)
# from and join
alias = query_table(qr.JOIN, qr.FROM)
query_tables = table_names(alias)
table = table_creation(query_tables)
for table_name , table_desc in table.items():
    print( table_name , "Table")
    print(" {:<25} {:<25} {:<10} {:<10} {:<10} {:<10}".format ( "Table Name", "Data Type", "Size", "Decimal", "is null" , " key "))
    print(" {:<25} {:<25} {:<10} {:<10} {:<10} {:<10}".format ( "---------------", "----------", "-----", "-------", "----------" , "-------"))
    for column in table_desc.columns:
        print(" {:<25} {:<25} {:<10} {:<10} {:<10} {:<10}".format ( column.name , column.datatype , column.size , column.decimal , column.is_null , column.key ))
    print()
#print(alias)
#print( qr.SELECT)
#print(query_tables)
print("Select  - ")
print()
select = Select( qr.SELECT,table, alias , query_tables)
#print(query_tables,"empty")
join_tables = Join(qr.JOIN , table , query_tables)
print("{:<25} {:<25} {:<25} {:<10} {:<10} {:<10} {:<25}".format ("Name", "Alias", "Table Name", "Data Type", "Size", "Decimal", "Field Type"))
print("{:<25} {:<25} {:<25} {:<10} {:<10} {:<10} {:<25}".format ("---------------", "----------", "---------------", "----------", "-----", "-------", "----------"))
for col in select:
#    print("name: ",col.name," Alias : ",col.alias," Table name: ",col.table_name," Data Type : ",col.datatype," Size : ",col.size," Decimal : ",col.decimal," col.func : ",col.func)
    print("{:<25} {:<25} {:<25} {:<10} {:<10} {:<10} {:<25}".format (col.name, col.alias, col.table_name, col.datatype, col.size, col.decimal, col.func))
print()

print("Join  - ")
print()
print("{:<25} {:<25} {:<25} {:<10} ".format ("Table Name", "Alias", "Condition", "Columns"))
for col in join_tables:
    columns = ""
    for colm in col.columns :
        #print("hi" + colm)
        columns += colm + ","
    #columns -= ","
    print("{:<25} {:<25} {:<25} {:<10} ".format (col.tableName, col.alias,  col.condition , columns))

print()
