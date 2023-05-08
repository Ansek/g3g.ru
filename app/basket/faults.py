from spyne.error import Fault, ResourceNotFoundError

class SoapDBError(Fault):
    def __init__(self, err):
        Fault.__init__(
            self,
            faultcode='DBError',
            faultstring=str(err)
        )
        
class SoapOrderNotFound(ResourceNotFoundError):
    def __init__(self, id):
        Fault.__init__(
            self,
            faultcode='OrderNotFound',
            faultstring=f'Order #{id} not found'
        )
        
class SoapStatusAssignmentError(Fault):
    def __init__(self, s1, s2):
        Fault.__init__(
            self,
            faultcode='StatusAssignmentError',
            faultstring=f'"{s1}" status must follow "{s2}" status'
        )
        
 