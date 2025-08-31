from Lexer import tokenGenerator
from .Token import Token
TokenTypes={
    'TT_INT': 'INT',
    'TT_FLOAT': 'FLOAT',  
    'TT_PLUS': 'PLUS',
    'TT_MINUS': 'MINUS',
    'TT_MUL': 'MUL',
    'TT_DIV': 'DIV',
    'TT_NEWLINE': 'NEWLINE',
    'TT_EOF': 'EOF',
    'TT_BLOCKSTART': '{',
    'TT_BLOCKEND': '}',
    'TT_IDENTIFIER':'IDENTIFIER',
    'TT_KEYWORD':'KEYWORD',
    'TT_STRING':'STRING',
    'TT_LP':'(',
    'TT_RP':')',
    'TT_BOOL':'BOOL',
    'TT_TERMINATOR':';',
    'TT_SEPERATOR':',',
    'TT_CONDITIONALOP':'CONDITIONALOP',
    'TT_LOGICALOP':'LOGICALOP'
}
Digits='0123456789'
Letters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
Letter_Digits=Letters+Digits
KEYWORDS={
    'show':'TT_KEYWORD',
    'is':'TT_KEYWORD',
    'false':'TT_BOOL',
    'true':'TT_BOOL',
    'gt':'TT_CONDITIONALOP',
    'gteq':'TT_CONDITIONALOP',
    'lt':'TT_CONDITIONALOP',
    'lteq':'TT_CONDITIONALOP',
    'eq':'TT_CONDITIONALOP',
    'noteq':'TT_CONDITIONALOP',
    'and':'TT_LOGICALOP',
    'or':'TT_LOGICALOP',
    'if':'TT_CONDITIONAL',
    'else_if':'TT_CONDITIONAL',
    'else':'TT_CONDITIONAL',
}

all=['tokenGenerator','KEYWORDS','Digits','Letter_Digits','TokenTypes','Letters']