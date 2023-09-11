import os
import sys
from z3 import *
import random
from qiskit.circuit.library.phase_oracle import PhaseOracle

def preorder_to_inorder(strs):
    bracket_stack = list()
    op_stack = list()
    value_stack = list()
    output = ""
    idx = 0
    while idx < len(strs):
        if strs[idx] == "|" or strs[idx] == "&" or strs[idx] == "~":
            op_stack.append(strs[idx])
            idx += 1
        elif strs[idx] == "(":
            bracket_stack.append(strs[idx])
            idx += 1
            
        elif strs[idx] == ")":
            op = op_stack.pop()
            bracket = bracket_stack.pop()
            if op == "~":
                value = value_stack.pop()
                value_stack.append(bracket + "~" + value + strs[idx])
            elif op == "&" or op == "|":
                value1 = value_stack.pop()
                value2 = value_stack.pop()
                value_stack.append(bracket + value2 + op + value1 + strs[idx])
            idx += 1
        elif strs[idx] == 'a' or strs[idx] == 'b' or strs[idx] == 'c':
            value_stack.append(strs[idx])
            idx += 1
        else:
            idx += 1
            continue
    # print(value_stack)
    return value_stack[0]
        
class Generator(object):
    def __init__(self, m):
        self.num_clauses = m
        self.answer = dict()
        while True:
            self.instance = None
            self.instance_list = self.sat()
            self.aggregate(self.instance_list)
            # print(self.instance)
            # self.instance = simplify(self.instance)
            # if self.instance == True:
            #     continue
            if self.verify() == True:
                break
        self.strs = str(self.instance).replace('And', '&').replace('Or', '|').replace('Not', '~')
        self.strs = preorder_to_inorder(self.strs)

    def random_tf_machine(self):
        if random.randint(0,1) == 0:
            return False
        return True

    def verify(self):
        solver = Solver()
        solver.add(self.instance)
        result = solver.check()
        # print(result)
        if result == unsat:
            return False
        m = solver.model()
        for x in m.decls():
            name = x.name()
            solution = m[x]
            self.answer[name] = solution
        return True

    def constant_instance(self):
        a, b, c = Bools('a b c')
        # instance = And(Or(And(a, b), Or(Not(b), a)), Or(Or(Not(c), b), Not(a)))
        instance = And(And(Or(Or(Not(c), b), a), Or(c, a)), And(Not(a), b))
        self.answer = {'b': True, 'a': True, 'c': False}
        return instance

    def sat(self):
        instance_list = list()
        a, b, c = Bools('a b c')
        variable_list = [a,b,c]
        operation_list = ['and', 'or']
        # only support: Not And Or
        for _ in range(self.num_clauses):
            tmp_instance = None
            num_variables = 2 if self.random_tf_machine() == True else 3
            
            if num_variables == 2:
                first, second = random.sample(variable_list, 2)
                third = None
            else:
                first, second, third = random.sample(variable_list, 3)
            if self.random_tf_machine() == True:
                first = Not(first)
            if self.random_tf_machine() == True:
                tmp_instance = And(first, second)
            else:
                tmp_instance = Or(first, second)
            if third == None:
                instance_list.append(tmp_instance)
                continue

            if self.random_tf_machine() == True:
                third = Not(third)
            if self.random_tf_machine() == True:
                tmp_instance = And(tmp_instance, third)
            else:
                tmp_instance = Or(tmp_instance, third)
            instance_list.append(tmp_instance)
        return instance_list

    def aggregate(self, ins_list):
        while True:
            if len(ins_list) == 0:
                break
            if len(ins_list) > 1:
                first = ins_list.pop()
                second = ins_list.pop()
                if self.instance == None:
                    self.instance = first
                if self.random_tf_machine() == True:
                    self.instance = And(self.instance, second)
                else:
                    self.instance = Or(self.instance, second)
            else:
                first = ins_list.pop()
                if self.instance == None:
                    self.instance = first
                if self.random_tf_machine() == True:
                    self.instance = And(self.instance, second)
                else:
                    self.instance = Or(self.instance, second)                    


if __name__ == "__main__":
    for i in range(30):
        path = os.path.join('inst', str(i).zfill(2) + ".or")
        with open(path, "w") as f:
            gen = Generator(4)
            oracle = PhaseOracle(gen.strs)
            print(oracle.qasm(), file = f)
