
class OperatorAwarenessV3:
    MAP = {
        'numeric':['=','!=','>','>=','<','<='],
        'text':['=','!=','contains'],
        'date':['before','after','between'],
        'boolean':['=']
    }

    def operators(self, datatype):
        return self.MAP.get(datatype, ['='])
