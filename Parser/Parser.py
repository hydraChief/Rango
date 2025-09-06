import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Nodes import NumberNode,BinaryNode,StatementsNode, ShowNode, VariableNode, StringNode, VariableAccessNode,BooleanNode
from ErrorHandler import ParserResult
from Tokenizer import TokenTypes, tokenGenerator, KEYWORDS
from Logger import get_logger

class Parser:
    def __init__(self, tokens):
        self.tokens=tokens
        self.current_token_index=0
        self.current_token=self.tokens[self.current_token_index]
        self.variables:list[str]=[]
        self.logger = get_logger()

    def advance(self):
        self.current_token_index+=1
        if self.current_token_index < len(self.tokens):
            self.current_token=self.tokens[self.current_token_index]
        else:
            self.current_token=None

    def parse(self):
        self.logger.log_parsing_start(len(self.tokens))
        res=ParserResult()
        statements=[]
        while self.current_token is not None and self.current_token.type != TokenTypes["TT_EOF"]:
            self.logger.debug(f"Parsing token", token_type=self.current_token.type, token_value=self.current_token.value, token_index=self.current_token_index)
            
            if self.current_token.type==TokenTypes["TT_NEWLINE"]:
                res.register_advance()
                self.advance()
                continue

            old_token_index = self.current_token_index
            stmt_result = ParserResult()
            stmnt = stmt_result.register(self.expression())
            if stmt_result.error:
                self.logger.log_parsing_error(stmt_result.error)
                return res.failure(stmt_result.error)
            
            self.logger.debug(f"Expression returned", statement_type=type(stmnt).__name__ if stmnt else "None", advance_count=stmt_result.advance_count)
            
            # Apply the advances that were tracked during parsing
            # for _ in range(stmt_result.advance_count):
                # self.advance()
            
            statements.append(stmnt)
            new_token_index = self.current_token_index
            self.logger.debug(f"Statement parsed successfully", statements_count=len(statements), old_index=old_token_index, new_index=new_token_index, advances_applied=stmt_result.advance_count)
            
            # Safety check to prevent infinite loop
            if new_token_index == old_token_index:
                self.logger.error("Parser stuck - token index not advancing!")
                break
        
        ast_node = StatementsNode(statements)
        self.logger.log_parsing_complete(type(ast_node).__name__)
        for stmt in statements:
            self.logger.info(f"node type '{type(stmt).__name__}'")
        return res.success(ast_node)


    def factor(self,expression_meta_data):
        res=ParserResult()
        token=self.current_token
        if expression_meta_data["prev_token_type"] is not None and expression_meta_data["prev_token_type"] != self.current_token.type and self.current_token.type != TokenTypes["TT_IDENTIFIER"]:
            return res.failure(f"Can't use differnet Literals, '{expression_meta_data['prev_token_type']}' '{self.current_token.type}'")

        if  token.type == TokenTypes['TT_IDENTIFIER']:
            res.register_advance()
            self.advance()
            return res.success(VariableAccessNode(variable_token_name=token.value))
        
        if token.type in (TokenTypes["TT_INT"],TokenTypes["TT_FLOAT"]):
            res.register_advance()
            self.advance()
            if(expression_meta_data["prev_token_type"] is None):expression_meta_data["prev_token_type"] = token.type
            return res.success(NumberNode(value=token.value))
        
        if token.type ==TokenTypes["TT_STRING"]:
            res.register_advance()
            self.advance()
            if(expression_meta_data["prev_token_type"] is None):expression_meta_data["prev_token_type"] = token.type
            return res.success(StringNode(value=token.value))
        
        if token.type ==TokenTypes["TT_BOOL"]:
            res.register_advance()
            self.advance()
            if(expression_meta_data["prev_token_type"] is None):expression_meta_data["prev_token_type"] = token.type
            boolval=True if token.value in ('true') else False
            return res.success(BooleanNode(boolval))
        
        if token.type==TokenTypes["TT_LP"]:
            res.register_advance()
            self.advance()
            node=res.register(self.expression(calc=True,expression_meta_data=expression_meta_data))
            if res.error:
                return res
            if self.current_token.type==TokenTypes["TT_RP"]:
                self.advance()
                return res.success(node)
            else:
                res.failure("Expected closing Parenthesis")

        if token.type==TokenTypes['TT_MINUS']:
            if(self.current_token_index+1<len(self.tokens) and 
               self.current_token_index-1>=0 and 
               (
                   self.tokens[self.current_token_index-1].type in (TokenTypes["TT_LP"], None) or
                   self.tokens[self.current_token_index-1].value == "is"
                ) and 
               self.tokens[self.current_token_index+1].type in (TokenTypes["TT_INT"],TokenTypes["TT_FLOAT"])
               ):
                res.register_advance()
                self.advance()
                value=self.current_token.value
                if(expression_meta_data["prev_token_type"] is None):expression_meta_data["prev_token_type"] = self.current_token.type
                res.register_advance()
                self.advance()
                return res.success(NumberNode(value=(value)*(-1)))
            return res.failure("Expected 'Literal', but got '-'")
        return res.failure("Expected 'Literal' or 'Expression'")
            
    def term(self,expression_meta_data):
        res=ParserResult()
        node=res.register(self.factor(expression_meta_data=expression_meta_data))
        if res.error:
            return res
        
        while self.current_token is not None and self.current_token.type in (TokenTypes["TT_MUL"],TokenTypes["TT_DIV"]):
            token=self.current_token
            if expression_meta_data["prev_token_type"] is  not None and expression_meta_data["prev_token_type"]== TokenTypes["TT_STRING"]:
                return res.failure(f"Operation '{token}' is not available for String Literal")
            res.register_advance()
            self.advance()
            right=res.register(self.factor(expression_meta_data=expression_meta_data))
            if res.error:
                return res
            node=BinaryNode(left=node,op=token,right=right)
        return res.success(node)

    def expression(self, calc=False,expression_meta_data={"prev_token_type":None}):
        res= ParserResult()

        if calc and self.current_token is not None:
            node=res.register(self.term(expression_meta_data))
            if res.error:
                return res
            while self.current_token is not None and self.current_token.type in (TokenTypes["TT_PLUS"],TokenTypes["TT_MINUS"]):
                token=self.current_token
                if expression_meta_data["prev_token_type"] is  not None and expression_meta_data["prev_token_type"]== TokenTypes["TT_STRING"] and token.type==TokenTypes["TT_MINUS"]:
                    return res.failure(f"Operations '{token}' is not available for String Literal")
                res.register_advance()
                self.advance()
                right=res.register(self.term(expression_meta_data))
                if res.error: return res
                node=BinaryNode(left=node,op=token,right=right)
            return res.success(node)

        if not calc and  self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"]:
            variable_token=self.current_token
            res.register_advance()
            self.advance()
            
            if self.current_token is None or self.current_token.value!="is":
                return res.failure("Expected 'is'")

            res.register_advance()
            self.advance()

            if self.current_token is None:
                return res.failure("Expected 'Literal'")
            
            node=res.register(self.expression(calc=True))
            if res.error:
                return res
            self.variables.append(str(variable_token.value))
            if self.current_token is None or self.current_token.type!=TokenTypes["TT_TERMINATOR"]:
                return res.failure("Expected ';'")
            res.register_advance()
            self.advance()
            return res.success(VariableNode(variable_token_name=variable_token.value, variable_node=node))

        if self.current_token is not None and self.current_token.type== TokenTypes[KEYWORDS["show"]] and self.current_token.value=="show":
            res.register_advance()
            self.advance()
            if self.current_token.type!=TokenTypes["TT_LP"]:
                return res.failure("Expected '('")
            
            res.register_advance()
            self.advance()
            body=[]
            if self.current_token.type == TokenTypes['TT_RP']:
                return res.success(ShowNode(body))
            exp=res.register(self.expression(calc=True))
            if res.error:
                return res
            body.append(exp)
            while self.current_token is not None and self.current_token.type==TokenTypes['TT_SEPERATOR']:
                res.register_advance()
                self.advance()
                exp=res.register(self.expression(calc=True))
                if res.error:
                    return res
                body.append(exp)

            if self.current_token.type != TokenTypes['TT_RP']:
                return res.failure("Expected ')'")
            res.register_advance()
            self.advance()
            if self.current_token is not None and self.current_token.type!=TokenTypes["TT_TERMINATOR"]:
                return res.failure("Expected ';'")
            res.register_advance()
            self.advance()
            return res.success(ShowNode(body))
        
        # If no valid expression pattern is matched, return an error
        return res.failure("Invalid expression or statement")

    def generate(self):
        return self.expression()
    
def run(filename):
    logger = get_logger()
    logger.log_tokenization_start(filename)
    
    tokens, error=tokenGenerator(filename)
    if error==None:
        logger.log_tokenization_complete(filename, len(tokens))
        parser=Parser(tokens)
        ast: ParserResult| None=parser.parse()
        if ast is None:
            logger.error("Parser returned None - Invalid syntax")
            print("Error: Invalid syntax")
            return None, "Invalid Syntax"
        else:
            logger.debug(f"AST generated successfully", ast_type=type(ast.node).__name__)
            print("AST:", ast.node)
            return ast.node, ast.error
    else:
        logger.log_tokenization_error(filename, error)
        return None, error