import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    """
    Base Class. The dunder methods for all binary operations are reassigned here
    so that it's always inherited. 
    """
    @staticmethod
    def parse_rdunders(self, other, class_type):
        """
        Called when any rdunder method is called. Takes in the two objects and the 
        Operator Class that called it and returns an instance of that Operator Class
        """
        if type(other) == str:
            return class_type(Var(other), self)
        else:
            return class_type(Num(other), self)

    def __add__(self, other):
        return Add(self, other)
    
    def __radd__(self, other):
        return Symbol.parse_rdunders(self, other, Add) 

    def __sub__(self, other):
        return Sub(self, other)
    
    def __rsub__(self, other):
        return Symbol.parse_rdunders(self, other, Sub) 

    def __mul__(self, other):
        return Mul(self, other)
    
    def __rmul__(self, other):
        return Symbol.parse_rdunders(self, other, Mul) 

    def __truediv__(self, other):
        return Div(self, other)
    
    def __rtruediv__(self, other):
        return Symbol.parse_rdunders(self, other, Div) 
    
    def __pow__(self, other):
        return Pow(self, other)
    
    def __rpow__(self, other):
        return Symbol.parse_rdunders(self, other, Pow) 
        

class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n
        # op => operation
        self.op = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"

    def deriv(self, var):
        # if differentiating with respect to this variable,
        # return 1
        if var == self.name:
            return Num(1)
        # otherwise, treat as a constant, whose derivative is 0
        else:
            return Num(0)
    
    def simplify(self):
        # can't simplify any further
        return self
    
    def eval(self, mapping):
        # if the variable has been given a value, assign it
        if self.name in mapping:
            return mapping[self.name]
        # otherwise, return the variable
        return self

class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n
        self.op = None

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"
    
    def deriv(self, var):
        # derivative of constant is always 0
        return Num(0)
    
    def simplify(self):
        # can't simplify further
        return self
    
    def eval(self, mapping):
        return self.n


class BinOp(Symbol):
    def __init__(self, left, right):
        self.left = BinOp.parse_symbol(left)
        self.right = BinOp.parse_symbol(right)
    
    @staticmethod
    def parse_symbol(attr):
        # check if given attribute is a Num Object,
        # Var Object, integer, float, or string
        if isinstance(attr, (Num, Var, BinOp)):
            return attr
        elif isinstance(attr, int) or isinstance(attr, float):
            return Num(attr)
        elif isinstance(attr, str):
            return Var(attr)
        else:
            raise ValueError()
        
    def __str__(self):
        # recursively call string functions
        l_str = ['', self.left.__str__(), '']
        r_str = ['', self.right.__str__(), '']

        # PARENTHESIZATION; based on PEMDAS
        # if binary operation is multiplication or division...
        if self.op == ' * ' or self.op == ' / ':
            # if either part of the operation is of lower precedence
            # add parentheses
            if self.left.op == ' + ' or self.left.op == ' - ':
                l_str[0], l_str[2] = '(', ')'
            if self.right.op == ' + ' or self.right.op == ' - ':
                r_str[0], r_str[2] = '(', ')'
        # SPECIAL CASES
        # if binary operation is division and the right operation has an equal precedence
        # add parentheses
        if self.op == ' / ' and (self.right.op == ' / ' or self.right.op == ' * '):
            r_str[0], r_str[2] = '(', ')'
        # same for subtraction
        elif self.op == ' - ' and (self.right.op == ' - ' or self.right.op == ' + '):
            r_str[0], r_str[2] = '(', ')'
        
        # if binary operation is exponentiation and left has equal or lower precedence,
        # add parantheses
        if self.op == ' ** ' and (self.left.op in (' ** ', ' * ', ' / ', ' + ', ' - ')):
            l_str[0], l_str[2] = '(', ')'

        return ''.join(l_str) + self.op + ''.join(r_str)

    def __repr__(self):
        # recursively call repr functions
        return self.op_name + '(' + self.left.__repr__() + ", " + self.right.__repr__() +")"
    
"""
The following children Classes of BinOp have the following methods:
    deriv(self, var):
        Finds the binary operations derivative with respect to the variable given.
    simplify(self):
        Simplifies the expressions based on the following rules:
        - Any binary operation on two numbers should simplify to a single number containing the result.
        - Adding 0 to (or subtracting 0 from) any expression E should simplify to E.
        - Multiplying or dividing any expression E by 1 should simplify to E.
        - Multiplying any expression E by 0 should simplify to 0.
        - Dividing 0 by any expression E should simplify to 0.
        - A single number or variable always simplifies to itself.
        - Any expression raised to the power 0 should simplify to 11.
        - Any expression raised to the power 1 should simplify to itself.
        - 0 raised to any positive power (or to any other symbolic expression that is not a single number) 
            should simplify to 0.
    eval(self, mapping):
        Given a dictionary, mapping, that holds assignments for variables in a given expression, the method 
            evaluates the expression with the given assignments
    
    All of the following methods above do this recursively for nested binary operations.
"""

class Add(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        # store the operation type and class name so that the inherited
        # str method can call them
        self.op = " + "
        self.op_name = "Add"
    
    def deriv(self, var):
        # linear derivative
        return self.left.deriv(var) + self.right.deriv(var)
    
    def simplify(self):
        # recursively call simplify
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # if both right and left are numbers, return their sum
        if isinstance(self.right, Num) and isinstance(self.left, Num):
            return Num(self.right.n + self.left.n)
        # if one of them is 0, return its complement
        elif isinstance(self.right, Num) and self.right.n == 0:
            return self.left
        elif isinstance(self.left, Num) and self.left.n == 0:
            return self.right
        # base case: can't simplify further
        return self.left + self.right
    
    def eval(self, mapping):
        # recursively evaluate expression
        return self.left.eval(mapping) + self.right.eval(mapping)

class Sub(BinOp):
    def __init__(self, left, right):
        super().__init__(left, right)
        # store the operation type and class name so that the inherited
        # str method can call them
        self.op = " - "
        self.op_name = "Sub"
    
    def deriv(self, var):
        # linear derivative
        return self.left.deriv(var) - self.right.deriv(var)

    def simplify(self):
        # recursively call simplify
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # if both left and right are numbers, return their difference
        if isinstance(self.right, Num) and isinstance(self.left, Num):
            return Num(self.left.n - self.right.n)
        # if either left or right are 0, return its complement
        elif isinstance(self.right, Num) and self.right.n == 0:
            return self.left
        # base case: can't simplify further
        return self.left - self.right
    
    def eval(self, mapping):
        # recursively evaluate expression
        return self.left.eval(mapping) - self.right.eval(mapping)

class Mul(BinOp):
    def __init__(self, left, right):
        # store the operation type and class name so that the inherited
        # str method can call them
        super().__init__(left, right)
        self.op = " * "
        self.op_name = "Mul"
    
    def deriv(self, var):
        # product rule
        return self.left.deriv(var)*self.right + self.right.deriv(var)*self.left

    def simplify(self):
        # recursively simplify
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # if both left and right are numbers, return their product
        if isinstance(self.right, Num) and isinstance(self.left, Num):
            return Num(self.right.n * self.left.n)
        # if either of them (left and right) is equal to 1, return its complement. 
        # And if either of them is equal to 0, return 0
        elif isinstance(self.right, Num):
            if self.right.n == 1:
                return self.left
            elif self.right.n == 0:
                return Num(0)
        elif isinstance(self.left, Num):
            if self.left.n == 1:
                return self.right
            elif self.left.n == 0:
                return Num(0)
        # Base case: can't simplify further
        return self.left * self.right

    def eval(self, mapping):
        # recursively evaluate expression
        return self.left.eval(mapping) * self.right.eval(mapping)

class Div(BinOp):
    def __init__(self, left, right):
        # store the operation type and class name so that the inherited
        # str method can call them
        super().__init__(left, right)
        self.op = " / "
        self.op_name = "Div"
    
    def deriv(self, var):
        # quotient rule
        return (self.left.deriv(var)*self.right - self.right.deriv(var)*self.left)/(self.right*self.right)
    
    def simplify(self):
        # recursively simplify
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # if both left and right are numbers, return their quotient
        if isinstance(self.right, Num) and isinstance(self.left, Num):
            return Num(self.left.n / self.right.n)
        # if the denominator is 1, return the numerator
        elif isinstance(self.right, Num) and self.right.n == 1:
            return self.left
        # if the numerator is 0, return 0
        elif isinstance(self.left, Num) and self.left.n == 0:
            return Num(0)
        
        # base case: can't divide further
        return self.left / self.right
    
    def eval(self, mapping):
        # recursively evaluate expression
        return self.left.eval(mapping) / self.right.eval(mapping)

class Pow(BinOp):
    def __init__(self, left, right):
        # store the operation type and class name so that the inherited
        # str method can call them
        super().__init__(left, right)
        self.op = " ** "
        self.op_name = "Pow"
    
    def deriv(self, var):
        # power rule, but only when exponent is a number
        if isinstance(self.right, Num):
            return (self.right * (self.left ** (self.right - Num(1)))) * self.left.deriv(var)
        else:
            raise TypeError("Can only get derivatives of polynomials with integer exponents")

    def simplify(self):
        # recursively simplify
        self.left = self.left.simplify()
        self.right = self.right.simplify()

        # if something is to the power of 0, simplify to 1
        if isinstance(self.right, Num) and self.right.n == 0:
            return Num(1)
        # if something is something to the power of 1, return the base
        elif isinstance(self.right, Num) and self.right.n == 1:
            return self.left
        # if base is 0 and exponent is a positive number or any other 
        # symbolic expression that not a number, return 0
        elif isinstance(self.left, Num) and self.left.n == 0:
            if isinstance(self.right, Num) and self.right.n > 0:
                return Num(0)
            elif isinstance(self.right, BinOp):
                return Num(0)
    
    def eval(self, mapping):
        return self.left.eval(mapping) ** self.right

def expression(string):
    # return parsed expression
    return parse(tokenize(string))

def tokenize(string):
    """
    >>> tokenize("(x * (2 + 3))")
    ['(', 'x', '*', '(', '2', '+', '3', ')', ')']
    """
    output = []
    
    # check if first character is not a space and add it if true
    if string[0] != " ":
        output.append(string[0])
    for i in range(1, len(string)):
        # remove all spaces
        if string[i] != " ":
            # if the current token is part of a multi-digit number, add it to previous token
            if string[i].isnumeric() and (string[i-1].strip('-').isnumeric() or (output[-1] == '-' and string[i-1] != ' ')):
                output[-1] += string[i]
            # if the previous token was * and the current token is also *, then it's an exponentiation sign
            elif string[i] == '*' and output[-1] == '*':
                output[-1] += string[i]
            # otherwise, add the token
            else:
                output.append(string[i])
    
    return output

def parse(tokens):
   def parse_expression(index):
        token = tokens[index]
        # if token is a number...
        if token.strip('-').isnumeric():
           return Num(int(token)), index + 1
        # if token is a variable...
        elif token.isalpha():
            return Var(token), index + 1
        # dealing with operation '('
        else:
            # recurse on left side of operation
            left_side, operator_i = parse_expression(index+1)
            # recurse on right side of operation
            right_side, n_index = parse_expression(operator_i+1)

            # check operator and return proper BinOp
            if tokens[operator_i] == '+':
                return Add(left_side, right_side), n_index + 1
            elif tokens[operator_i] == '-':
                return Sub(left_side, right_side), n_index + 1
            elif tokens[operator_i] == '*':
                return Mul(left_side, right_side), n_index + 1
            elif tokens[operator_i] == '**':
                return Pow(left_side, right_side), n_index + 1
            else:
                return Div(left_side, right_side), n_index + 1

   parsed_expression, next_index = parse_expression(0)
   return parsed_expression

if __name__ == "__main__":
    doctest.testmod()
