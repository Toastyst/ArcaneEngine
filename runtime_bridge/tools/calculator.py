class Calculator:
    def calculate(self, expression):
        try:
            # Simple math only, no functions
            allowed_names = {"__builtins__": None}
            return str(eval(expression, allowed_names))
        except:
            return "Error"
