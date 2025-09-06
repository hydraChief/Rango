
TokenTypes={
    'TT_INT': 'INT',
    'TT_FLOAT': 'FLOAT',  
    'TT_PLUS': 'PLUS',
    'TT_MINUS': 'MINUS',
    'TT_MUL': 'MUL',
    'TT_DIV': 'DIV',
    'TT_NEWLINE': 'NEWLINE',
    'TT_EOF': 'EOF',
    'TT_IDENTIFIER':'IDENTIFIER',
    'TT_KEYWORD':'KEYWORD',
    'TT_STRING':'STRING',
    'TT_LP':'(',
    'TT_RP':')',
    'TT_BOOL':'BOOL',
    'TT_TERMINATOR':';',
    'TT_SEPERATOR':','
}
Digits='0123456789'
Letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
Letter_Digits=Letters+Digits
KEYWORDS={
    'show':'TT_KEYWORD',
    'is':'TT_KEYWORD',
    'false':'TT_BOOL',
    'true':'TT_BOOL'
}