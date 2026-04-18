class Calculator:
    def calculate(self, expression):
        try:
            return str(eval(expression))
        except:
            return "Error"