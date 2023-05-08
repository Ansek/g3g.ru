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


class SoapProductNotFound(ResourceNotFoundError):
    def __init__(self, id, order_id=None):
        fs = f'Product #{id} not found'
        if order_id is not None:
           fs += f' in order #{order_id}'
        Fault.__init__(
            self,
            faultcode='ProductNotFound',
            faultstring=fs
        )


class SoapStatusAssignmentError(Fault):
    def __init__(self, s1, s2):
        Fault.__init__(
            self,
            faultcode='StatusAssignmentError',
            faultstring=f'"{s1}" status must follow "{s2}" status'
        )


class SoapNotEnoughProducts(Fault):
    def __init__(self, id, name, count1, count2):
        Fault.__init__(
            self,
            faultcode='NotEnoughProducts',
            faultstring=f'Count of product #{id} ({name})'+\
                f' less than {count1}.'+\
                f'Total available: {count2}.'
        )