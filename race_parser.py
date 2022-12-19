import string

keywords = [
    "executable",
    "include",
    "files",
]

class Parser:
    def __init__(self, tokens : list) -> None:
        self.tokens = tokens
        self.index = 0
        self.value_buffer = []
        self.type_buffer = []
        self.instructions = []
        self.braces = 0

    def start(self) -> list[list[str]]:
        while self.index < len(self.tokens):
            self.type_buffer.append(self.tokens[self.index][0])
            self.value_buffer.append(self.tokens[self.index][1])
            self.match()
            self.index += 1

        return self.applystructure()

    def parsetarget(self, target, depth):
        if not "childs" in target:
            target["childs"] = []
        if self.instructions[0][-1] == depth: 
            ins = self.instructions.pop(0)
            if ins[0] in ["include", "files"]:
                try:
                    child = {"name": ins[0]}
                    while self.instructions[0][-1] == depth + 1:
                        self.parsetarget(child, depth + 1)

                except IndexError: # empty remaining instruction
                    pass
                
                target["childs"].append(child)

            else:
                target["childs"].append(ins)
        

    def applystructure(self):
        # pack variables in dict
        buildvars = {}
        for ins in self.instructions:
            if ins[0] == "assignment":
                buildvars[ins[1].lower()] = ins[3]
        
        print(buildvars)

        # filter out assignments
        self.instructions = list(filter(lambda ins: ins[0] != "assignment", self.instructions))
        # loop over remaining instructions
        targets = []
        while self.instructions:
            ins = self.instructions.pop(0)
            if ins[0] == "executable":
                target = {}
                target["type"] = "executable"
                target["name"] = ins[1]
                try:
                    while self.instructions[0][-1] == 1:
                        self.parsetarget(target, 1)
                except IndexError: # empty remaining instruction
                    pass
                targets.append(target)

        return buildvars, targets


    def isbrace(self, char : string) -> bool:
        return char in ["{", "}"]

    def match(self) -> None:
        if self.type_buffer == ["string", "operator", "string"]: # assignment
            # add assignment instruction and clear buffers
            self.instructions.append(["assignment", *self.value_buffer])
            self.type_buffer = []
            self.value_buffer = []

        elif self.type_buffer == ["keyword", "string", "punctuation"]: # executable
            # determine which keyword it is and if punctuation is brace
            if self.value_buffer[0] == "executable" and self.value_buffer[2] == "{":
                # add executable to complex buffer and clear buffers
                self.instructions.append(["executable", self.value_buffer[1], self.braces])
                self.braces += 1
                self.type_buffer = []
                self.value_buffer = []

        elif self.type_buffer == ["keyword", "punctuation"]: # include, files
            if (self.value_buffer[0] == "include" or self.value_buffer[0] == "files") and self.isbrace(self.value_buffer[1]):
                # add include/files instruction, increment brace and clear buffers
                self.instructions.append([self.value_buffer[0], self.braces])
                self.braces += 1
                self.type_buffer = []
                self.value_buffer = []

        elif self.type_buffer == ["punctuation"]:
            if self.value_buffer[0] == "}":
                # "close" one brace and clear buffers
                self.braces -= 1
                self.type_buffer = []
                self.value_buffer = []
        
        elif self.type_buffer == ["string"]:
            # check if it is operator, else add string as single value and clear buffers
            if self.tokens[self.index + 1][0] != "operator":
                self.instructions.append(["string", self.value_buffer[0], self.braces])
                self.type_buffer = []
                self.value_buffer = []
        