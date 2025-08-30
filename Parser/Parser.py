from Nodes import NumberNode,BinaryNode,StatementsNode, ShowNode, VariableNode, StringNode, VariableAccessNode,BooleanNode
from ErrorHandler import ParserResult
from Tokenizer import TokenTypes, tokenGenerator

class Parser:
    def __init__(self, tokens):
        self.tokens=tokens
        self.current_token_index=0
        self.current_token=self.tokens[self.current_token_index]
        self.variables:list[str]=[]

    def advance(self):
        self.current_token_index+=1
        if self.current_token_index < len(self.tokens):
            self.current_token=self.tokens[self.current_token_index]
        else:
            self.current_token=None

    def parse(self):
        res=ParserResult()
        statements=[]
        while self.current_token is not None and self.current_token.type != TokenTypes["TT_EOF"]:
            if self.current_token.type==TokenTypes["TT_NEWLINE"]:
                res.register_advance()
                self.advance()
                continue

            stmnt=res.register(self.expression())
            if res.error:
                return res
            
            statements.append(stmnt)
        return res.success(StatementsNode(statements))


    def factor(self,expression_meta_data):
        res=ParserResult()
        token=self.current_token
        if expression_meta_data.prev_token_type is not None and expression_meta_data.prev_token_type != self.current_token.type:
            return res.failure(f"Can't use differnet Literals, '{expression_meta_data.prev_token_type}' '{self.current_token.type}'")

        if  token.type == TokenTypes['TT_IDENTIFIER']:
            res.register_advance()
            self.advance()
            return res.success(VariableAccessNode(variable_token_name=token.value))
        
        if token.type in (TokenTypes["TT_INT"],TokenTypes["TT_DOUBLE"]):
            res.register_advance()
            self.advance()
            if(expression_meta_data["prev_token_type"] is None):expression_meta_data["prev_token_type"] = self.current_token.type
            return res.success(NumberNode(value=token.value))
        
        if token.type ==TokenTypes["TT_STRING"]:
            res.register_advance()
            self.advance()
            if(expression_meta_data["prev_token_type"] is None):expression_meta_data["prev_token_type"] = self.current_token.type
            return res.success(StringNode(value=token.value))
        
        if token.type ==TokenTypes["TT_BOOL"]:
            res.register_advance()
            self.advance()
            if(expression_meta_data["prev_token_type"] is None):expression_meta_data["prev_token_type"] = self.current_token.type
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
               self.tokens[self.current_token_index+1].type in (TokenTypes["TT_INT"],TokenTypes["TT_DOUBLE"])
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
            if expression_meta_data.prev_token_type is  not None and expression_meta_data.prev_token_type== TokenTypes["TT_STRING"]:
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
                if expression_meta_data.prev_token_type is  not None and expression_meta_data.prev_token_type== TokenTypes["TT_STRING"] and token.type==TokenTypes["TT_MINUS"]:
                    return res.failure(f"Operations '{token}' is not available for String Literal")
                res.register_advance()
                self.advance()
                right=res.register(self.term())
                if res.error: return res
                node=BinaryNode(left=node,op=token,right=right)
            return res.success(node)

        if not calc and  self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"]:
            variable_token=self.current_token
            res.register_advance()
            self.advance()
            
            if self.current_token is not None and self.current_token.value!="is":
                res.failure("Expected 'is'")

            res.register_advance()
            self.advance()

            if self.current_token is None:
                return res.failure("Expected 'Literal'")
            
            node=res.register(self.expression(calc=True))
            if res.error:
                return res
            self.variables.append(str(variable_token.value))
            if self.current_token is None and self.current_token.type!=TokenTypes["TT_TERMINATOR"]:
                return res.failure("Expected '.'")
            res.register_advance()
            self.advance()
            return res.success(VariableNode(variable_token_name=variable_token.value, variable_node=node))

        if self.current_token is not None and self.current_token.type== TokenTypes["TT_KEYWORD"] and self.current_token.value=="show":
            res.register_advance()
            self.advance()
            if self.current_token.type!=TokenTypes["TT_LP"]:
                return res.failure("Expected '('")
            
            res.register_advance()
            self.advance()
            body=[]
            if self.current_token == TokenTypes['TT_RP']:
                return res.success(ShowNode(body))
            exp=res.register(self.expression(calc=True))
            if res.error:
                return res
            body.append(exp)
            while self.current_token is not None and self.current_token==TokenTypes['TT_SEPERATOR']:
                res.register_advance()
                self.advance()
                exp=res.register(self.expression(calc=True))
                if res.error:
                    return res
                body.append(exp)

            if self.current_token != TokenTypes['TT_RP']:
                return res.failure("Expected ')'")
            res.register_advance()
            self.advance()
            if self.current_token is None and self.current_token.type!=TokenTypes["TT_TERMINATOR"]:
                return res.failure("Expected '.'")
            res.register_advance()
            self.advance()
            return res.success(ShowNode(body))

    def generate(self):
        return self.expression()
    
def run(filename)-> tuple[ParserResult | None]:
    tokens, error=tokenGenerator(filename)
    if error==None:
        parser=Parser(tokens)
        ast: ParserResult| None=parser.parse()
        if ast is None:
            print("Error: Invalid syntax")
            return none, "Invalid Syntax"
        else:
            print("AST:", ast.node)
            return ast.node, ast.error
    else:
        return None, error