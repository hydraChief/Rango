from .Utility import Position
from .Token import Token
from . import Digits, Letters, KEYWORDS, TokenTypes
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Logger import get_logger
class Lexer:
    def __init__(self, text, filename=None):
        self.text = text
        self.filename = filename
        self.pos = Position(-1, 0, -1, filename, text)
        self.current = None
        self.logger = get_logger()
        self.advance()
    
    def create_token(self):
        tokens = []
        while self.current is not None:
            char = self.current
            if char in ' \t':
                self.advance()
            elif char == '\n':
                self.pos.line+=1
                self.pos.col=0
                tokens.append(Token(TokenTypes['TT_NEWLINE'], start=self.pos.copy()))
                self.advance()
            elif char in Digits:
                tokens.append(self.create_number())
            elif char in Letters or char == '_':
                tokens.append(self.create_identifier())
            elif char == '+':
                tokens.append(Token(TokenTypes['TT_PLUS'], value ='+', start=self.pos.copy()))
                self.advance()
            elif char == '-':
                tokens.append(Token(TokenTypes['TT_MINUS'], value='-',start=self.pos.copy()))
                self.advance()
            elif char == '*':
                tokens.append(Token(TokenTypes['TT_MUL'], value ='*', start=self.pos.copy()))
                self.advance()
            elif char == '/':
                tokens.append(Token(TokenTypes['TT_DIV'], value='/',start=self.pos.copy()))
                self.advance()
            elif char == '(':
                tokens.append(Token(TokenTypes['TT_LP'], value='(',start=self.pos.copy()))
                self.advance()
            elif char == ')':
                tokens.append(Token(TokenTypes['TT_RP'], value=')',start=self.pos.copy()))
                self.advance()
            elif char == ';':
                tokens.append(Token(TokenTypes['TT_TERMINATOR'], value=';',start=self.pos.copy()))
                self.advance()
            elif char == '.':
                tokens.append(Token(TokenTypes['TT_END'], value='.',start=self.pos.copy()))
                self.advance()
            elif char == ',':
                tokens.append(Token(TokenTypes['TT_SEPERATOR'], value=',',start=self.pos.copy()))
                self.advance()
            elif char == '{':
                tokens.append(Token(TokenTypes['TT_BLOCKSTART'], value='{',start=self.pos.copy()))
                self.advance()
            elif char == '}':
                tokens.append(Token(TokenTypes['TT_BLOCKEND'], value='}',start=self.pos.copy()))
                self.advance()
            elif char == '"':
                tokens.append(self.create_string())
            elif char in Letters:
                tokens.append(self.create_identifier())
                self.advance()
            else:
                start_pos = self.pos.copy()
                char = self.current
                error_msg = f"Invalid syntax, '{char}'"
                self.logger.error(f"Tokenization error", character=char, position=f"line {self.pos.line}, col {self.pos.col}")
                self.advance()
                return [], error_msg
        tokens.append(Token(TokenTypes['TT_EOF'], start=self.pos.copy()))
        self.logger.debug(f"Tokenization completed successfully", total_tokens=len(tokens))
        return tokens, None

    def advance(self):
        self.pos.index+=1
        if(self.pos.index<len(self.text)):
            self.current=self.text[self.pos.index]
        else : self.current=None

    def create_number(self):
        num_str=''
        dot_count=0
        start_pos=self.pos.copy()
        while self.current is not None and self.current in Digits+'.':
            if self.current=='.':
                if dot_count==1:break
                dot_count+=1
            num_str+=self.current
            self.advance()

        if dot_count==0: return Token(TokenTypes['TT_INT'],int(num_str),start_pos, self.pos)
        else:
            return Token(TokenTypes['TT_FLOAT'],float(num_str),start_pos,self.pos)


    def create_string(self):
        id_str=""
        start_pos=self.pos.copy()
        self.advance()
        while self.current is not None and self.current!='"':
            id_str+=self.current
            self.advance()
        if(self.current=='"'):
            self.advance()
            return Token(TokenTypes['TT_STRING'],id_str,start_pos,self.pos.copy())
        

    def create_identifier(self):
        id_str=""
        start_pos=self.pos.copy()
        while self.current is not None and self.current in Letters+Digits+"_":
            id_str+=self.current
            self.advance()
        if id_str in KEYWORDS:
            return Token(TokenTypes[KEYWORDS[id_str]],id_str,start_pos,self.pos.copy())
        return Token(TokenTypes['TT_IDENTIFIER'],id_str,start_pos,self.pos.copy())

def tokenGenerator(filename):
    logger = get_logger()
    logger.debug(f"Reading source file", filename=filename)
    
    try:
        with open(filename,'r', encoding='utf-8') as f:
            text=f.read()
        logger.debug(f"File read successfully", filename=filename, file_size=len(text))
    except FileNotFoundError:
        error_msg = f"Error: File '{filename}' not found"
        logger.error(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Error: Error reading file: {e}"
        logger.error(error_msg)
        return None, error_msg

    logger.debug(f"Starting lexical analysis", filename=filename)
    lexer =Lexer(text,filename)
    tokens,error= lexer.create_token()
    
    if error:
        logger.error(f"Lexical analysis failed", filename=filename, error=error)
    else:
        logger.debug(f"Lexical analysis completed", filename=filename, tokens_generated=len(tokens))
    
    return tokens,error