
class ParameterInfo:

    def __init__(self):
        super().__init__()

        self.name: str = None
        self.string: bool = False
        self.integer: bool = False
        self.double: bool = False
        self.number: bool = False
        self.boolean: bool = False
        self.file: bool = False
        self.intfloat: int = 0
        self.enum: bool = False
        self.array: bool = False
        self.map: bool = False
        self.object: bool = False
        self.optional: bool = False
        self.index:  int = 0
        self.input: bool = False
        self.output: bool = False
        self.comment: str = None
        self.valtyp = None
        self.keytyp = None
