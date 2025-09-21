import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Nodes import NumberNode,BinaryNode,StatementsNode, ShowNode, VariableNode, StringNode, VariableAccessNode,BooleanNode, LogicalNode, ComparatorNode, ConditionalNode, TillNode, RepeatNode, StopNode, ContinueNode, FunctionDefinitionNode, FunctionCallNode, ReturnNode, NoneNode, AccessItSelfMethodNode, AccessItSelfVariableNode, MethodCallNode, InstanceCreationNode, ClassDefinitionNode, InstanceVariableAssignmentNode
from ErrorHandler import ParserResult
from Tokenizer import TokenTypes, tokenGenerator, KEYWORDS
from Logger import get_logger

class Parser:
    def __init__(self, tokens,debugFlag=False):
        self.tokens=tokens
        self.current_token_index=0
        self.current_token=self.tokens[self.current_token_index]
        self.variables:list[str]=[]
        self.logger = get_logger(debugFlag=debugFlag)

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
            stmnt = stmt_result.register(self.statement())
            if stmt_result.error:
                self.logger.info(f"current token: '{self.current_token.value}'")
                self.logger.log_parsing_error(stmt_result.error)
                return res.failure(stmt_result.error)
            
            self.logger.debug(f"Expression returned", statement_type=type(stmnt).__name__ if stmnt else "None", advance_count=stmt_result.advance_count)
            
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

    def parseBlock(self):
        res=ParserResult()
        if self.current_token is None or self.current_token.value!=TokenTypes["TT_BLOCKSTART"]:
            return res.failure("Expected '{'")
        
        res.register_advance()
        self.advance()
        statements=[]
        while self.current_token is not None and self.current_token.type != TokenTypes["TT_BLOCKEND"]:
            
            if self.current_token.type==TokenTypes["TT_NEWLINE"]:
                res.register_advance()
                self.advance()
                continue

            stmt_result = ParserResult()
            stmnt = stmt_result.register(self.statement())
            if stmt_result.error:
                return res.failure(stmt_result.error)
            
            self.logger.debug(f"Expression returned", statement_type=type(stmnt).__name__ if stmnt else "None", advance_count=stmt_result.advance_count)
            
            statements.append(stmnt)

        if self.current_token is None or self.current_token.value!=TokenTypes["TT_BLOCKEND"]:
            return res.failure("Expected '}'")
        res.register_advance()
        self.advance()
        ast_node = StatementsNode(statements)
        return res.success(ast_node)


    def condFactor(self,expression_meta_data):
        res=ParserResult()
        if self.current_token.type == TokenTypes["TT_LP"]:
            res.register_advance()
            self.advance()
            node=res.register(self.condExpression(expression_meta_data))
            if res.error:
                return res
            if self.current_token.type!=TokenTypes["TT_RP"]:
                return res.failure("Expected ')'")
            res.register_advance()
            self.advance()
            while self.current_token is not None and self.current_token.type in (TokenTypes['TT_PLUS'],TokenTypes['TT_MINUS'],TokenTypes['TT_MUL'],TokenTypes['TT_DIV']):
                if self.current_token is not None and self.current_token.type in (TokenTypes['TT_PLUS'],TokenTypes['TT_MINUS']):
                    node=res.register(self.plusMinusHandler(node=node,expression_meta_data=expression_meta_data))
                    if res.error:
                        return res
                if self.current_token is not None and self.current_token.type in (TokenTypes['TT_MUL'],TokenTypes['TT_DIV']):
                    node=res.register(self.mulDivHandler(node=node,expression_meta_data=expression_meta_data))
                    if res.error:
                        return res
            return res.success(node)
    
        node=res.register(self.expression(expression_meta_data=expression_meta_data))
        if res.error:
            return res
        return res.success(node)
    
    def condTerm(self,expression_meta_data):
        res=ParserResult()
        node=res.register(self.condFactor(expression_meta_data))
        if self.current_token is not  None and self.current_token.type== TokenTypes['TT_CONDITIONALOP']:
            op=self.current_token.value
            res.register_advance()
            self.advance()
            right=res.register(self.condFactor(expression_meta_data))
            if res.error:
                return res
            node=ComparatorNode(left=node,value=op,right=right)
        return res.success(node)

    def condExpression(self,expression_meta_data={"prev_token_type":None}):
        res=ParserResult()
        if self.current_token is None:
            return res.failure("Expected 'Literal'")
        node=res.register(self.condTerm(expression_meta_data))
        if res.error:
            return res
        while self.current_token is not None and self.current_token.type == TokenTypes["TT_LOGICALOP"]:
            op=self.current_token.value
            res.register_advance()
            self.advance()
            right=res.register(self.condTerm(expression_meta_data=expression_meta_data))
            if res.error:
                return res
            node = LogicalNode(left=node,value=op,right=right)
        return res.success(node)
    

    def plusMinusHandler(self,node,expression_meta_data):
        res=ParserResult()
        token=self.current_token
        if expression_meta_data["prev_token_type"] is  not None and expression_meta_data["prev_token_type"]== TokenTypes["TT_STRING"] and token.type==TokenTypes["TT_MINUS"]:
            return res.failure(f"Operations '{token}' is not available for String Literal")
        res.register_advance()
        self.advance()
        right=res.register(self.term(expression_meta_data=expression_meta_data))
        if res.error: 
            return res
        node=BinaryNode(left=node,op=token,right=right)
        return res.success(node)

    def mulDivHandler(self,node,expression_meta_data):
        res=ParserResult()
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
    
    def factor(self,expression_meta_data):
        res=ParserResult()
        token=self.current_token
        # if expression_meta_data["prev_token_type"] is not None and expression_meta_data["prev_token_type"] != self.current_token.type and self.current_token.type not in (TokenTypes["TT_IDENTIFIER"],TokenTypes["TT_LP"]):
        #     return res.failure(f"Can't use differnet Literals, '{expression_meta_data['prev_token_type']}' '{self.current_token.type}'")
        if token is not None and token.type==TokenTypes["TT_OBJECTPOINTER"]:
            res.register_advance()
            self.advance()
            if self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"] and (self.current_token_index+1<len(self.tokens) and self.tokens[self.current_token_index+1].type==TokenTypes["TT_LP"]):
                methodData=res.register(self.methodCallStatement())
                if res.error:
                    return res
                return res.success(AccessItSelfMethodNode(methodName=methodData["value"],args=methodData["args"]))
            
            if  self.current_token.type == TokenTypes['TT_IDENTIFIER']:
                variable_token_name=self.current_token.value
                res.register_advance()
                self.advance()
                return res.success(AccessItSelfVariableNode(variable_token_name=variable_token_name))
            return res.failure("Expected 'Identifier'")
        if token is not None and token.type==TokenTypes["TT_IDENTIFIER"] and (self.current_token_index+1<len(self.tokens) and self.tokens[self.current_token_index+1].type==TokenTypes["TT_LP"]):
            node=res.register(self.functionCallStatement())
            if res.error:
                return res
            return res.success(node)
        
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
            node=res.register(self.expression(expression_meta_data=expression_meta_data))
            if res.error:
                return res
            if self.current_token.type==TokenTypes["TT_RP"]:
                res.register_advance()
                self.advance()
                return res.success(node)
            else:
                return res.failure("Expected closing Parenthesis")

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
        print(token.value)
        return res.failure("Expected 'Literal' or 'Expression'")
            
    def term(self,expression_meta_data):
        res=ParserResult()
        node=res.register(self.factor(expression_meta_data=expression_meta_data))
        if res.error:
            return res
        
        while self.current_token is not None and self.current_token.type in (TokenTypes["TT_MUL"],TokenTypes["TT_DIV"]):
            node=res.register(self.mulDivHandler(node=node,expression_meta_data=expression_meta_data))
            if res.error:
                return res
        return res.success(node)

    def expression(self,expression_meta_data={"prev_token_type":None}):
        res= ParserResult()
        if self.current_token is not None:
            node=res.register(self.term(expression_meta_data))
            if res.error:
                return res
            while self.current_token is not None and self.current_token.type in (TokenTypes["TT_PLUS"],TokenTypes["TT_MINUS"]):
                node=res.register(self.plusMinusHandler(node=node,expression_meta_data=expression_meta_data))
                if res.error:
                    return res
            return res.success(node)

    def assignmentStatement(self):
        res=ParserResult()
        variable_token=self.current_token
        # print(f"DEBUG: assignmentStatement - variable_token: {variable_token.type} = {variable_token.value}")
        res.register_advance()
        self.advance()
        
        # print(f"DEBUG: assignmentStatement - after advance, current_token: {self.current_token.type if self.current_token else None} = {self.current_token.value if self.current_token else None}")
        if self.current_token is not None and self.current_token.value!="is":
            return res.failure("Expected 'is'")

        res.register_advance()
        self.advance()

        # print(f"DEBUG: assignmentStatement - before condExpression, current_token: {self.current_token.type if self.current_token else None} = {self.current_token.value if self.current_token else None}")
        node=res.register(self.condExpression())
        if res.error:
            return res
        
        # print(f"DEBUG: assignmentStatement - after condExpression, current_token: {self.current_token.type if self.current_token else None} = {self.current_token.value if self.current_token else None}")

        self.variables.append(str(variable_token.value))
        if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
            # print(f"DEBUG: assignmentStatement - Expected ';' but got: {self.current_token.type if self.current_token else None} = {self.current_token.value if self.current_token else None}")
            return res.failure("Expected ';'")
        res.register_advance()
        self.advance()
        return res.success(VariableNode(variable_token_name=variable_token.value, variable_node=node))
    
    def assignmentStatementInInstance(self):
        res=ParserResult()
        variable_token=self.current_token
        # print(f"DEBUG: assignmentStatement - variable_token: {variable_token.type} = {variable_token.value}")
        res.register_advance()
        self.advance()
        
        # print(f"DEBUG: assignmentStatement - after advance, current_token: {self.current_token.type if self.current_token else None} = {self.current_token.value if self.current_token else None}")
        if self.current_token is not None and self.current_token.value!="is":
            return res.failure("Expected 'is'")

        res.register_advance()
        self.advance()

        # print(f"DEBUG: assignmentStatement - before condExpression, current_token: {self.current_token.type if self.current_token else None} = {self.current_token.value if self.current_token else None}")
        node=res.register(self.condExpression())
        if res.error:
            return res
        
        # print(f"DEBUG: assignmentStatement - after condExpression, current_token: {self.current_token.type if self.current_token else None} = {self.current_token.value if self.current_token else None}")

        self.variables.append(str(variable_token.value))
        if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
            # print(f"DEBUG: assignmentStatement - Expected ';' but got: {self.current_token.type if self.current_token else None} = {self.current_token.value if self.current_token else None}")
            return res.failure("Expected ';'")
        res.register_advance()
        self.advance()
        return res.success(InstanceVariableAssignmentNode(variable_token_name=variable_token.value, variable_node=node))
    
    
    def showStatement(self):
        res=ParserResult()
        res.register_advance()
        self.advance()
        if self.current_token.type!=TokenTypes["TT_LP"]:
            return res.failure("Expected '('")
        
        res.register_advance()
        self.advance()
        body=[]
        if self.current_token.type == TokenTypes['TT_RP']:
            res.register_advance()
            self.advance()
            if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
                return res.failure("Expected ';'")
            res.register_advance()
            self.advance()
            return res.success(ShowNode(body))
        
        exp=res.register(self.condExpression())
        if res.error:
            return res
        body.append(exp)
        
        while self.current_token is not None and self.current_token.type == TokenTypes['TT_SEPERATOR']:
            res.register_advance()
            self.advance()
            exp=res.register(self.condExpression())
            if res.error:
                return res
            body.append(exp)

        if self.current_token is None or self.current_token.type != TokenTypes['TT_RP']:
            return res.failure("Expected ')'")
        res.register_advance()
        self.advance()
        
        if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
            return res.failure("Expected ';'")
        res.register_advance()
        self.advance()
        return res.success(ShowNode(body))

    def ifStatement(self):
        res=ParserResult()
        value=self.current_token.value
        res.register_advance()
        self.advance()
        if self.current_token is None:
            return res.failure("Expected Condition Expression")
        condition_node=BooleanNode(False)
        if value=="else":
            condition_node.value=True
        else:
            condition_node=res.register(self.condExpression())
            if res.error:
                return res
        
        body=res.register(self.parseBlock())
        if res.error:
            return res

        elseIfBlockNodes=[]
        if value=="if":
            while self.current_token is not None and self.current_token.type==TokenTypes["TT_CONDITIONAL"] and self.current_token.value!="if":
                noMoreBlocksAheadFlag=False
                if self.current_token.value=="else":
                    noMoreBlocksAheadFlag=True
                elseIfStatement=res.register(self.ifStatement())
                if res.error:
                    return res
                elseIfBlockNodes.append(elseIfStatement)
                if(noMoreBlocksAheadFlag):
                    break
        self.logger.info(f"{value} {condition_node.value} {type(body).__name__}")
        return res.success(ConditionalNode(value=value,condition=condition_node,body=body,elseIfBlockNodes=elseIfBlockNodes))
    
    def repeatStatement(self):
        res = ParserResult()
        res.register_advance()
        self.advance()

        if self.current_token is None:
            return res.failure("Expected Condition Expression")
        
        condition_node=res.register(self.condExpression())
        if res.error:
            return res
        if self.current_token is not None and self.current_token.type != TokenTypes["TT_TIMESITITERATOR"]:
            return res.failure(f"Expected '{TokenTypes['TT_TIMESITITERATOR']}'")
        res.register_advance()
        self.advance()
        body=res.register(self.parseBlock())
        if res.error:
            return res
        return res.success(RepeatNode(condition=condition_node,body=body))

    def tillStatement(self):
        res = ParserResult()
        res.register_advance()
        self.advance()

        if self.current_token is None:
            return res.failure("Expected Condition Expression")
        
        condition_node=res.register(self.condExpression())
        if res.error:
            return res

        body=res.register(self.parseBlock())
        if res.error:
            return res
        return res.success(TillNode(condition=condition_node,body=body))
    
    def stopStatement(self):
        res=ParserResult()
        res.register_advance()
        self.advance()
        if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
            return res.failure("Expected ';'")
        res.register_advance()
        self.advance()
        return res.success(StopNode())
    
    def continueStatement(self):
        res=ParserResult()
        res.register_advance()
        self.advance()
        if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
            return res.failure("Expected ';'")
        res.register_advance()
        self.advance()
        return res.success(ContinueNode())
    
    def functionDefinitionStatement(self):
        res=ParserResult()
        res.register_advance()
        self.advance()
        if self.current_token is None:
            return res.failure("Expected Function Name")
        name=self.current_token.value

        res.register_advance()
        self.advance()

        if self.current_token is None or self.current_token.type != TokenTypes["TT_LP"]:
            return res.failure("Expected '('")
        res.register_advance()
        self.advance()
        params=[]
        if self.current_token is not None and self.current_token.type == TokenTypes["TT_RP"]:
            res.register_advance()
            self.advance()
            body=res.register(self.parseBlock())
            if res.error:
                return res
            return res.success(FunctionDefinitionNode(value=name,params=params,body=body))
        if self.current_token is not None and self.current_token.type == TokenTypes["TT_IDENTIFIER"]:
            params.append(self.current_token.value)
            res.register_advance()
            self.advance()
        while self.current_token is not None and self.current_token.type == TokenTypes["TT_SEPERATOR"]:
            res.register_advance()
            self.advance()
            if self.current_token is not None and self.current_token.type == TokenTypes["TT_IDENTIFIER"]:
                params.append(self.current_token.value)
                res.register_advance()
                self.advance()
            else:
                return res.failure("Expected Identifier")
        if self.current_token is None or self.current_token.type != TokenTypes["TT_RP"]:
            return res.failure("Expected ')'" )
        res.register_advance()
        self.advance()
        body=res.register(self.parseBlock())
        if res.error:
            return res
        return res.success(FunctionDefinitionNode(value=name,params=params,body=body))
        
    def functionCallStatement(self):
        res= ParserResult()
        name=self.current_token.value
        res.register_advance()
        self.advance()
        if self.current_token is None or self.current_token.type!=TokenTypes["TT_LP"]:
            return res.failure("Expected '('")
        res.register_advance()
        self.advance()
        args=[]
        if self.current_token is not None and self.current_token.type == TokenTypes["TT_RP"]:
            res.register_advance()
            self.advance()
            return res.success(FunctionCallNode(value=name,args=args))
    
        if self.current_token is not None:
            arg=res.register(self.condExpression())
            if res.error:
                return res
            args.append(arg)
        while self.current_token is not None and self.current_token.type == TokenTypes["TT_SEPERATOR"]:
            res.register_advance()
            self.advance()
            if self.current_token is not None:
                arg=res.register(self.condExpression())
                if res.error:
                    return res
                args.append(arg)
            else:
                return res.failure("Expected expression")
        if self.current_token is None or self.current_token.type != TokenTypes["TT_RP"]:
            return res.failure("Expected ')'" )
        res.register_advance()
        self.advance()
        return res.success(FunctionCallNode(value=name,args=args))

    def methodCallStatement(self):
        res= ParserResult()
        name=self.current_token.value
        res.register_advance()
        self.advance()
        if self.current_token is None or self.current_token.type!=TokenTypes["TT_LP"]:
            return res.failure("Expected '('")
        res.register_advance()
        self.advance()
        args=[]
        if self.current_token is not None and self.current_token.type == TokenTypes["TT_RP"]:
            res.register_advance()
            self.advance()
            return res.success({"value":name,"args":args})
    
        if self.current_token is not None:
            arg=res.register(self.condExpression())
            if res.error:
                return res
            args.append(arg)
        while self.current_token is not None and self.current_token.type == TokenTypes["TT_SEPERATOR"]:
            res.register_advance()
            self.advance()
            if self.current_token is not None:
                arg=res.register(self.condExpression())
                if res.error:
                    return res
                args.append(arg)
            else:
                return res.failure("Expected expression")
        if self.current_token is None or self.current_token.type != TokenTypes["TT_RP"]:
            return res.failure("Expected ')'" )
        res.register_advance()
        self.advance()
        return res.success({"value":name,"args":args})

    def returnStatement(self):
        res=ParserResult()
        res.register_advance()
        self.advance()
        if self.current_token is not None and self.current_token.type == TokenTypes["TT_TERMINATOR"]:
            res.register_advance()
            self.advance()
            return res.success(ReturnNode(returnNode=NoneNode()))
        node=res.register(self.condExpression())
        if res.error:
            return res
        if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
            return res.failure("Expected ';'")
        res.register_advance()
        self.advance()
        return res.success(ReturnNode(returnNode=node))

    def statement(self):
        res=ParserResult()
        
        if self.current_token is not None and self.current_token.type==TokenTypes["TT_COMMENT"]:
            res.register_advance()
            self.advance()
            while self.current_token is not None and self.current_token.type!=TokenTypes["TT_END"]:
                res.register_advance()
                self.advance()
            if self.current_token is None or self.current_token.type != TokenTypes["TT_END"]:
                return res.failure("Expected '.'")
            res.register_advance()
            self.advance()
            return res.success(NoneNode())

        if self.current_token is not None and self.current_token.type==TokenTypes["TT_CLASS"]:
            res.register_advance()
            self.advance()
            className=self.current_token.value
            res.register_advance()
            self.advance()
            body=res.register(self.parseBlock())
            if res.error:
                return res
            return res.success(ClassDefinitionNode(value=className,body=body))

        if self.current_token is not None and self.current_token.type==TokenTypes["TT_NEWOBJECT"]:
            res.register_advance()
            self.advance()
            if self.current_token is None or self.current_token.type!=TokenTypes["TT_IDENTIFIER"]:
                return res.failure("Expected Class Name")
            name=self.current_token.value
            res.register_advance()
            self.advance()
            if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
                return res.failure("Expected ';'")
            res.register_advance()
            self.advance()
            return res.success(InstanceCreationNode(value=name))

        if self.current_token is not None and self.current_token.type==TokenTypes["TT_OBJECTPOINTER"]:
            res.register_advance()
            self.advance()
            if self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"] and (self.current_token_index+1<len(self.tokens) and self.tokens[self.current_token_index+1].type==TokenTypes["TT_LP"]):
            
                methodData=res.register(self.methodCallStatement())
                if res.error:
                    return res
                if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
                    return res.failure("Expected ';'")
                res.register_advance()
                self.advance()
                return res.success(AccessItSelfMethodNode(methodName=methodData["value"],args=methodData["args"]))
            
            if self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"]:
                node=res.register(self.assignmentStatementInInstance())
                if res.error:
                    return res
                return res.success(node)
            
            return res.failure("Expected Identifier")
        
        if self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"] and (self.current_token_index+1<len(self.tokens) and self.tokens[self.current_token_index+1].type==TokenTypes["TT_ATTRIBUTEACCESSOR"]):
            objName=self.current_token.value
            res.register_advance()
            self.advance()
            res.register_advance()
            self.advance()
            if self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"] and (self.current_token_index+1<len(self.tokens) and self.tokens[self.current_token_index+1].type==TokenTypes["TT_LP"]):
            
                methodData=res.register(self.methodCallStatement())
                if res.error:
                    return res
                if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
                    return res.failure("Expected ';'")
                res.register_advance()
                self.advance()
                return res.success(MethodCallNode(instanceName=objName,methodName=methodData["value"],args=methodData["args"]))
            if self.current_token is None or self.current_token.type!=TokenTypes["TT_IDENTIFIER"]:
                return res.failure("Expected Identifier")
            return res.failure("Expected '('")

        if self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"] and (self.current_token_index+1<len(self.tokens) and self.tokens[self.current_token_index+1].type==TokenTypes["TT_LP"]):
            node=res.register(self.functionCallStatement())
            if res.error:
                return res
            if self.current_token is None or self.current_token.type != TokenTypes["TT_TERMINATOR"]:
                return res.failure("Expected ';'")
            res.register_advance()
            self.advance()
            return res.success(node)
        
        if self.current_token is not None and self.current_token.type==TokenTypes["TT_FUNCTIONDEFINITION"]:
            node=res.register(self.functionDefinitionStatement())
            if res.error:
                return res
            return res.success(node)

        if self.current_token is not None and self.current_token.type== TokenTypes["TT_FUNCTIONRETURN"] and self.current_token.value=="return":
            node=res.register(self.returnStatement())
            if res.error:
                return res
            return res.success(node)

        if self.current_token is not None and self.current_token.type==TokenTypes["TT_IDENTIFIER"]:
            node=res.register(self.assignmentStatement())
            if res.error:
                return res
            return res.success(node)
        
        if self.current_token is not None and self.current_token.type== TokenTypes["TT_KEYWORD"] and self.current_token.value=="show":
            node=res.register(self.showStatement())
            if res.error:
                return res
            return res.success(node)

        if self.current_token is not None and self.current_token.type==TokenTypes["TT_CONDITIONAL"]:
            self.logger.info(f"parsing '{self.current_token.value}'")
            if self.current_token.value!="if":
                return res.failure("Expected 'if'")
            node=res.register(self.ifStatement())
            if res.error:
                return res
            return res.success(node)
        
        if self.current_token is not None and self.current_token.type==TokenTypes["TT_ITERATOR"]:
            self.logger.info(f"parsing '{self.current_token.value}'")
            if self.current_token.value=="repeat":
                node=res.register(self.repeatStatement())
                if res.error:
                    return res
                return res.success(node)
            elif self.current_token.value=="till":
                node=res.register(self.tillStatement())
                if res.error:
                    return res
                return res.success(node)
            else:
                return res.failure(f"Invalid KEYWORD, '{self.current_token.value}'")
            
        if self.current_token is not None and self.current_token.type==TokenTypes["TT_STOPITERATOR"]:
            node=res.register(self.stopStatement())
            if res.error:
                return res
            return res.success(node)
        
        if self.current_token is not None and self.current_token.type==TokenTypes["TT_CONTINUEITERATOR"]:
            node=res.register(self.continueStatement())
            if res.error:
                return res
            return res.success(node)
        return res.failure("Invalid Syntax")
    def generate(self):
        return self.expression()
    
def run(filename,debugFlag=False):
    logger = get_logger(debugFlag=debugFlag)
    logger.log_tokenization_start(filename)
    
    tokens, error=tokenGenerator(filename,debugFlag)
    if error==None:
        logger.log_tokenization_complete(filename, len(tokens))
        parser=Parser(tokens,debugFlag=debugFlag)
        ast: ParserResult| None=parser.parse()
        if ast is None:
            logger.error("Parser returned None - Invalid syntax")
            return None, "Invalid Syntax"
        else:
            logger.debug(f"AST generated successfully", ast_type=type(ast.node).__name__)
            print("AST:", ast.node)
            return ast.node, ast.error
    else:
        logger.log_tokenization_error(filename, error)
        return None, error